"""Unit tests for the Biederitz <-> Gerwisch timetable diagram module.

Most tests build synthetic ``vehroute``, stop-list and mapping documents, so
they stay fast and independent of simulation output. One test at the end runs
against the real scenario when it is present, because a diagram that parses
synthetic XML but finds nothing in the actual output would be useless.
Matplotlib runs on the headless Agg backend.
"""

import gzip
import os
import sys
from pathlib import Path

import pytest

os.environ.setdefault("MPLBACKEND", "Agg")

REPO_ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(REPO_ROOT / "src"))

from visualisation.plot_biederitz_gerwisch import (  # noqa: E402
    DEFAULT_STYLE,
    SCHEDULED_TIMES,
    STATION_A_KW,
    STATION_B_KW,
    Station,
    StopEvent,
    TrainRun,
    build_diagram,
    format_clock,
    load_stations,
    main,
    parse_corridor_runs,
    parse_time,
    resolve_station_stop_ids,
    style_for,
)

STOP_EVENT = StopEvent(arrival=10.0, departure=11.0)

# Stop ids as they appear in the real scenario: numeric, no station name.
BIEDERITZ_IDS = frozenset({"2480406266", "2480406275"})
GERWISCH_IDS = frozenset({"268432645", "1364703916"})

BIEDERITZ = Station(name="Biederitz", keyword="biederitz", stop_ids=BIEDERITZ_IDS)
GERWISCH = Station(name="Gerwisch", keyword="gerwisch", stop_ids=GERWISCH_IDS)
STATIONS = (BIEDERITZ, GERWISCH)


def _stop(**attributes):
    """Render one ``<stop>`` element from its attributes."""
    packed = " ".join(f'{name}="{value}"' for name, value in attributes.items())
    return f"    <stop {packed}/>"


def _vehicle(veh_id, stops, vtype="regional"):
    """Render one ``<vehicle>`` element around the given stop elements."""
    body = "\n".join(stops)
    return f'  <vehicle id="{veh_id}" type="{vtype}">\n{body}\n  </vehicle>'


def _write(path, text, compress=False):
    """Write a document, optionally gzipped, creating parent directories."""
    path.parent.mkdir(parents=True, exist_ok=True)
    open_fn = gzip.open if compress else open
    with open_fn(path, "wt", encoding="utf-8") as handle:
        handle.write(text)
    return path


def _write_vehroute(path, vehicles, compress=False):
    """Write a minimal vehroute document."""
    return _write(
        path, "<routes>\n" + "\n".join(vehicles) + "\n</routes>\n", compress=compress
    )


def _run(veh_id="RE_1", vtype="regional"):
    """A minimal corridor run, for checks that do not need parsing."""
    return TrainRun(id=veh_id, type=vtype, at_a=STOP_EVENT, at_b=STOP_EVENT)


def _close(figure):
    """Release a figure once its assertions are done."""
    import matplotlib.pyplot as plt

    plt.close(figure)


# A train calling at both stations. Scheduled 00:04:00 / 00:05:00 at Biederitz
# and 00:10:00 / 00:11:00 at Gerwisch; it runs two minutes late in reality.
DOWN_TRAIN = _vehicle(
    "V1",
    [
        _stop(
            busStop="2480406266",
            arrival="00:04:00",
            until="00:05:00",
            started="00:06:00",
            ended="00:07:00",
        ),
        _stop(
            busStop="268432645",
            arrival="00:10:00",
            until="00:11:00",
            started="00:12:00",
            ended="00:13:00",
        ),
    ],
)


# --- time parsing -----------------------------------------------------------


@pytest.mark.parametrize(
    "value, expected_seconds",
    [
        ("00:04:00", 240.0),
        ("01:02:03", 3723.0),
        ("1:02:03.5", 3723.5),
        ("25:00:00", 90000.0),
        ("3600", 3600.0),
        ("3600.5", 3600.5),
    ],
)
def test_parse_time_accepts_clock_strings_and_plain_seconds(value, expected_seconds):
    """SUMO writes either raw seconds or human-readable HH:MM:SS."""
    assert parse_time(value) == expected_seconds


@pytest.mark.parametrize("value", ["", "abc", "00:04", None])
def test_parse_time_rejects_unusable_values(value):
    """Unparsable times raise instead of silently becoming zero."""
    with pytest.raises(ValueError):
        parse_time(value)


def test_format_clock_renders_minutes_as_hours_and_minutes():
    """The time axis is labelled as a clock, not as a minute count."""
    assert format_clock(0) == "00:00"
    assert format_clock(630) == "10:30"
    assert format_clock(1500) == "25:00"


# --- station resolution -----------------------------------------------------


def test_station_matches_a_stop_by_its_sumo_id():
    """The real scenario only carries numeric stop ids, so ids must match."""
    assert BIEDERITZ.matches({"busStop": "2480406266"})
    assert not BIEDERITZ.matches({"busStop": "268432645"})


@pytest.mark.parametrize("attribute", ["busStop", "lane", "edge"])
def test_station_matches_a_named_location_as_fallback(attribute):
    """Scenarios that embed station names in ids keep working."""
    nameless = Station(name="Biederitz", keyword="biederitz")

    assert nameless.matches({attribute: "BIEDERITZ_Bf_0"})
    assert not nameless.matches({attribute: "Gerwisch_Bf_0"})


def test_resolve_station_stop_ids_bridges_stop_names_to_sumo_ids(tmp_path):
    """Station name -> GTFS id (stop list) -> SUMO stop ids (mapping)."""
    _write(
        tmp_path / "misc" / "train_stops.xml",
        '<additional>\n'
        '  <stop id="de:15086:8010047" name="Biederitz" lat="52.15" lon="11.71"/>\n'
        '  <stop id="de:15086:8011630" name="Gerwisch" lat="52.17" lon="11.74"/>\n'
        "</additional>\n",
    )
    _write(
        tmp_path / "misc" / "mapping.xml",
        '<mapping count="2">\n'
        '  <entry type="IFOPT" value="de:15086:8010047">\n'
        '    <stop_option stop_id="2480406266" rel="general" dist_m="8.8"/>\n'
        '    <stop_option stop_id="2480406275" rel="general" dist_m="21.0"/>\n'
        "  </entry>\n"
        '  <entry type="IFOPT" value="de:15086:8011630">\n'
        '    <stop_option stop_id="268432645" rel="general" dist_m="4.6"/>\n'
        "  </entry>\n"
        "</mapping>\n",
    )

    assert resolve_station_stop_ids(tmp_path, "biederitz") == BIEDERITZ_IDS
    assert resolve_station_stop_ids(tmp_path, "gerwisch") == frozenset({"268432645"})


def test_resolve_station_stop_ids_is_empty_without_artefacts(tmp_path):
    """A scenario without misc/ artefacts degrades to keyword matching."""
    assert resolve_station_stop_ids(tmp_path, "biederitz") == frozenset()


def test_load_stations_returns_both_corridor_stations(tmp_path):
    """Station order defines the y axis, so it must be stable."""
    stations = load_stations(tmp_path)

    assert [station.keyword for station in stations] == [STATION_A_KW, STATION_B_KW]


def test_station_keywords_are_lowercase():
    """Station matching is case-insensitive, so the keywords must be folded."""
    assert STATION_A_KW == STATION_A_KW.lower()
    assert STATION_B_KW == STATION_B_KW.lower()


# --- vehroute parsing -------------------------------------------------------


def test_parse_extracts_runs_calling_at_both_stations(tmp_path):
    """Only trains logging a stop at both stations become corridor runs."""
    path = _write_vehroute(
        tmp_path / "vehroute.xml",
        [
            DOWN_TRAIN,
            _vehicle(
                "V2",
                [_stop(busStop="2480406266", started="00:20:00", ended="00:21:00")],
            ),
        ],
    )

    runs = parse_corridor_runs(path, STATIONS)

    assert [run.id for run in runs] == ["V1"]


def test_parse_uses_realised_times_by_default(tmp_path):
    """The default diagram shows what the simulation actually did, in minutes."""
    path = _write_vehroute(tmp_path / "vehroute.xml", [DOWN_TRAIN])

    run = parse_corridor_runs(path, STATIONS)[0]

    assert (run.at_a.arrival, run.at_a.departure) == (6.0, 7.0)
    assert (run.at_b.arrival, run.at_b.departure) == (12.0, 13.0)


def test_parse_can_use_scheduled_times(tmp_path):
    """``SCHEDULED_TIMES`` plots the timetable instead of the simulation."""
    path = _write_vehroute(tmp_path / "vehroute.xml", [DOWN_TRAIN])

    run = parse_corridor_runs(path, STATIONS, times=SCHEDULED_TIMES)[0]

    assert (run.at_a.arrival, run.at_a.departure) == (4.0, 5.0)
    assert (run.at_b.arrival, run.at_b.departure) == (10.0, 11.0)


def test_parse_skips_stops_without_usable_times(tmp_path):
    """A stop with no time attribute is dropped, not placed at minute zero."""
    path = _write_vehroute(
        tmp_path / "vehroute.xml",
        [
            _vehicle(
                "V3",
                [
                    _stop(busStop="2480406266"),
                    _stop(busStop="268432645", started="00:12:00", ended="00:13:00"),
                ],
            )
        ],
    )

    assert parse_corridor_runs(path, STATIONS) == []


def test_parse_falls_back_to_arrival_when_departure_is_missing(tmp_path):
    """A stop without a departure time becomes a zero-length dwell."""
    path = _write_vehroute(
        tmp_path / "vehroute.xml",
        [
            _vehicle(
                "V4",
                [
                    _stop(busStop="2480406266", started="00:06:00"),
                    _stop(busStop="268432645", started="00:12:00", ended="00:13:00"),
                ],
            )
        ],
    )

    run = parse_corridor_runs(path, STATIONS)[0]

    assert run.at_a.arrival == run.at_a.departure == 6.0


def test_parse_reads_gzipped_output(tmp_path):
    """Gzipped vehroute output is accepted transparently."""
    path = _write_vehroute(tmp_path / "vehroute.xml.gz", [DOWN_TRAIN], compress=True)

    assert [run.id for run in parse_corridor_runs(path, STATIONS)] == ["V1"]


def test_run_direction_follows_the_stop_order(tmp_path):
    """Departing A before reaching B marks the A -> B direction, and vice versa."""
    path = _write_vehroute(
        tmp_path / "vehroute.xml",
        [
            DOWN_TRAIN,
            _vehicle(
                "V5",
                [
                    _stop(busStop="268432645", started="00:06:00", ended="00:07:00"),
                    _stop(busStop="2480406266", started="00:12:00", ended="00:13:00"),
                ],
            ),
        ],
    )

    runs = {run.id: run for run in parse_corridor_runs(path, STATIONS)}

    assert runs["V1"].travels_a_to_b is True
    assert runs["V5"].travels_a_to_b is False


# --- styling and drawing ----------------------------------------------------


@pytest.mark.parametrize(
    "veh_id, vtype, expected_label",
    [
        ("train_1", "rail_highspeed", "ICE / HighSpeed"),
        ("ICE_500", "regional", "ICE / HighSpeed"),
        ("train_2", "rail_intercity", "IC / InterCity"),
        ("IC_2071", "regional", "IC / InterCity"),
        ("V1", "regional", "Regional Line"),
    ],
)
def test_style_for_classifies_by_type_then_vehicle_id(veh_id, vtype, expected_label):
    """Train class comes from the vehicle type, with the id as a fallback hint."""
    assert style_for(_run(veh_id, vtype)).label == expected_label


def test_style_for_defaults_to_regional():
    """Unknown train types fall back to the regional style."""
    assert style_for(_run("foo", "bar")) is DEFAULT_STYLE


def test_build_diagram_draws_three_lines_per_run():
    """Each run yields two dwell lines plus one segment line."""
    runs = [_run("V1"), _run("V2")]

    figure = build_diagram(runs, STATIONS)

    try:
        assert len(figure.axes[0].lines) == 3 * len(runs)
    finally:
        _close(figure)


def test_build_diagram_legend_lists_each_train_class_once():
    """Trains of the same class share a single legend entry."""
    runs = [_run("V1"), _run("V2"), _run("ICE_500")]

    figure = build_diagram(runs, STATIONS)

    try:
        labels = [text.get_text() for text in figure.axes[0].get_legend().get_texts()]
        assert labels == ["Regional Line", "ICE / HighSpeed"]
    finally:
        _close(figure)


def test_build_diagram_labels_the_station_axis():
    """The y axis is labelled with the two station names."""
    figure = build_diagram([_run()], STATIONS)

    try:
        labels = [text.get_text() for text in figure.axes[0].get_yticklabels()]
        assert labels == ["Biederitz", "Gerwisch"]
    finally:
        _close(figure)


def test_build_diagram_formats_the_time_axis_as_a_clock():
    """Minute values on the x axis are rendered as HH:MM."""
    figure = build_diagram([_run()], STATIONS)

    try:
        formatter = figure.axes[0].xaxis.get_major_formatter()
        assert formatter(630) == "10:30"
    finally:
        _close(figure)


def test_build_diagram_survives_an_empty_run_list():
    """An empty corridor still produces a figure, without a legend crash."""
    figure = build_diagram([], STATIONS)

    try:
        assert len(figure.axes[0].lines) == 0
    finally:
        _close(figure)


# --- command line -----------------------------------------------------------


def test_main_writes_the_diagram_and_reports_success(tmp_path):
    """``main`` renders the requested vehroute output to the requested image."""
    vehroute = _write_vehroute(tmp_path / "output" / "vehroute.xml", [DOWN_TRAIN])
    image = tmp_path / "images" / "diagram.png"

    exit_code = main(["--vehroute", str(vehroute), "--output", str(image)])

    assert exit_code == 0
    assert image.is_file() and image.stat().st_size > 0


def test_main_fails_cleanly_on_a_missing_vehroute(tmp_path, capsys):
    """A missing input is a non-zero exit, not a traceback."""
    exit_code = main(["--vehroute", str(tmp_path / "nope.xml")])

    assert exit_code == 1
    assert "nope.xml" in capsys.readouterr().err


# --- real scenario ----------------------------------------------------------


@pytest.fixture(scope="session")
def real_scenario():
    """A scenario directory on disk that carries vehroute output."""
    scenarios = REPO_ROOT / "data" / "scenarios"
    for candidate in sorted(p for p in scenarios.glob("*") if p.is_dir()):
        for relative in ("output/vehroute.xml", "output/vehroute.xml.gz"):
            if (candidate / relative).is_file():
                return candidate, candidate / relative
    pytest.skip(f"No scenario with vehroute output under {scenarios}.")


def test_real_scenario_yields_corridor_runs(real_scenario):
    """The diagram must find trains in the actual simulation output."""
    scenario_dir, vehroute = real_scenario

    stations = load_stations(scenario_dir)
    runs = parse_corridor_runs(vehroute, stations)

    assert runs, (
        f"No train calls at both stations in {vehroute}. "
        f"Resolved stop ids: "
        + ", ".join(f"{s.name}={sorted(s.stop_ids)}" for s in stations)
    )
