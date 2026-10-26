"""Segment checks for the Biederitz <-> Gerwisch corridor.

The test reads the scenario exactly as it lies on disk: it never creates,
renames or moves directories, and it does not rely on the absolute paths baked
into ``sim.sumocfg`` (those point into the container layout). All SUMO
artefacts are read through the official ``sumolib`` API -- ``sumolib.xml`` for
the stop list and the vehroute output, ``sumolib.net`` for resolving the
stations onto network edges.
"""

import os
from pathlib import Path

import pytest
import sumolib

STATION_A = "Biederitz"
STATION_B = "Gerwisch"

# Radius around a station coordinate in which network edges count as "at the
# station". 100 m keeps the two station edge sets disjoint (see test below).
STATION_RADIUS_M = 100.0

# Point the test at a scenario outside of ``data/scenarios`` if needed.
SCENARIO_DIR_ENV = "RAILWAY_SCENARIO_DIR"

# Artefacts relative to a scenario directory; the first existing candidate
# wins, so plain and gzipped variants are both accepted.
NET_CANDIDATES = ("sumo/final.net.xml.gz", "sumo/final.net.xml")
VEHROUTE_CANDIDATES = ("output/vehroute.xml", "output/vehroute.xml.gz")
STOPS_CANDIDATES = ("misc/train_stops.xml.gz", "misc/train_stops.xml")

STOP_ATTRS = ("id", "name", "lat", "lon")
VEHICLE_ATTRS = ("id", "type")


def _first_existing(scenario_dir, relative_paths):
    """Return the first existing artefact, or None if none of them is present."""
    for relative in relative_paths:
        candidate = scenario_dir / relative
        if candidate.is_file():
            return candidate
    return None


def _candidate_scenario_dirs():
    """Scenario directories to consider, without assuming a fixed repo layout."""
    override = os.environ.get(SCENARIO_DIR_ENV)
    if override:
        return [Path(override).expanduser()]

    for parent in Path(__file__).resolve().parents:
        scenarios = parent / "data" / "scenarios"
        if scenarios.is_dir():
            return sorted(p for p in scenarios.iterdir() if p.is_dir())
    return []


def _as_dict(attributes, row):
    """Zip a ``parse_fast`` row by position.

    ``sumolib`` renames reserved attribute names (``name`` becomes
    ``attr_name``), so positional zipping is more robust than attribute access.
    """
    return dict(zip(attributes, row))


@pytest.fixture(scope="session")
def scenario_dir():
    """First scenario directory that carries both a network and vehroute output."""
    candidates = _candidate_scenario_dirs()
    for candidate in candidates:
        if _first_existing(candidate, NET_CANDIDATES) and _first_existing(
            candidate, VEHROUTE_CANDIDATES
        ):
            return candidate

    checked = [str(c) for c in candidates] or "no data/scenarios directory"
    pytest.skip(
        "No scenario with both a SUMO network and vehroute output found "
        f"(checked: {checked}). Run the simulation or set {SCENARIO_DIR_ENV}."
    )


@pytest.fixture(scope="session")
def vehroute_path(scenario_dir):
    return _first_existing(scenario_dir, VEHROUTE_CANDIDATES)


@pytest.fixture(scope="session")
def sumo_net(scenario_dir):
    """The scenario network, read with sumolib (internal edges are irrelevant here)."""
    net_path = _first_existing(scenario_dir, NET_CANDIDATES)
    return sumolib.net.readNet(str(net_path), withInternal=False)


@pytest.fixture(scope="session")
def station_stops(scenario_dir):
    """GTFS-derived stops per station keyword: {station: [stop dicts]}.

    The SUMO ``stops.add.xml`` only carries numeric OSM ids, so station names
    are taken from the GTFS-derived stop list instead of matched on stop ids.
    """
    stops_path = _first_existing(scenario_dir, STOPS_CANDIDATES)
    if stops_path is None:
        pytest.skip(f"No stop list in {scenario_dir} (looked for {STOPS_CANDIDATES}).")

    found = {STATION_A: [], STATION_B: []}
    for row in sumolib.xml.parse_fast(str(stops_path), "stop", STOP_ATTRS):
        stop = _as_dict(STOP_ATTRS, row)
        for station, hits in found.items():
            if station.casefold() in stop["name"].casefold():
                hits.append(stop)
    return found


@pytest.fixture(scope="session")
def station_edges(sumo_net, station_stops):
    """Network edge ids near each station: {station: {edge id}}.

    Uses sumolib geo lookups (``convertLonLat2XY`` + ``getNeighboringEdges``)
    instead of keyword matching on edge or busStop ids.
    """
    edges = {}
    for station, stops in station_stops.items():
        edge_ids = set()
        for stop in stops:
            x, y = sumo_net.convertLonLat2XY(float(stop["lon"]), float(stop["lat"]))
            neighbours = sumo_net.getNeighboringEdges(
                x, y, STATION_RADIUS_M, includeJunctions=False
            )
            edge_ids.update(edge.getID() for edge, _distance in neighbours)
        edges[station] = edge_ids
    return edges


def test_station_stops_are_known(station_stops):
    """Both corridor stations appear in the scenario stop list."""
    missing = [station for station, hits in station_stops.items() if not hits]
    assert not missing, f"Stations not found in the scenario stop list: {missing}"


def test_stations_resolve_to_disjoint_edges(station_edges):
    """Each station maps onto network edges, and the two sets stay distinct."""
    for station, edge_ids in station_edges.items():
        assert edge_ids, (
            f"No network edge within {STATION_RADIUS_M:.0f} m of {station}; "
            "the station is outside the network or the radius is too small."
        )

    overlap = station_edges[STATION_A] & station_edges[STATION_B]
    assert not overlap, (
        f"{STATION_A} and {STATION_B} share edges {sorted(overlap)}; "
        f"STATION_RADIUS_M={STATION_RADIUS_M:.0f} is too large for this segment."
    )


def test_vehroute_contains_vehicles(vehroute_path):
    """The vehroute output parses and holds at least one vehicle."""
    vehicles = [
        _as_dict(VEHICLE_ATTRS, row)
        for row in sumolib.xml.parse_fast(str(vehroute_path), "vehicle", VEHICLE_ATTRS)
    ]
    assert vehicles, f"No <vehicle> elements in {vehroute_path}."


def test_trains_serve_both_stations(vehroute_path, station_edges):
    """At least one train runs over the edges of both stations."""
    routed_edges = {}
    for vehicle, route in sumolib.xml.parse_fast_nested(
        str(vehroute_path), "vehicle", ("id",), "route", ("edges",)
    ):
        # Rerouted or incomplete vehicles can carry several <route> elements.
        routed_edges.setdefault(vehicle[0], set()).update(route[0].split())

    matched = {STATION_A: set(), STATION_B: set()}
    both = set()
    for vehicle_id, edge_ids in routed_edges.items():
        at_stations = {
            station: bool(edge_ids & station_edge_ids)
            for station, station_edge_ids in station_edges.items()
        }
        for station, hit in at_stations.items():
            if hit:
                matched[station].add(vehicle_id)
        if all(at_stations.values()):
            both.add(vehicle_id)

    assert both, (
        f"No train runs over both {STATION_A} and {STATION_B}.\n"
        f"- routed vehicles: {len(routed_edges)}\n"
        f"- at {STATION_A}: {len(matched[STATION_A])}\n"
        f"- at {STATION_B}: {len(matched[STATION_B])}"
    )
