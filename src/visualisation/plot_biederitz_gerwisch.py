"""Single-segment train diagram (Marey chart) for the Biederitz <-> Gerwisch corridor.

Reads a SUMO ``vehroute`` output and draws one line per train over the two
corridor stations: a horizontal line while the train dwells at a station and a
sloped line while it runs the segment.

Stations are resolved by id, not by name: the vehroute output only carries
numeric SUMO stop ids, so the station name is looked up in the GTFS-derived
stop list (``misc/train_stops.xml``) and translated into SUMO stop ids through
``misc/mapping.xml``. Scenarios that embed station names directly in their stop,
lane or edge ids still work through keyword matching.

Run it as a script::

    uv run python src/visualisation/plot_biederitz_gerwisch.py
    uv run python src/visualisation/plot_biederitz_gerwisch.py --times scheduled
"""

import argparse
import gzip
import sys
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.ticker import FuncFormatter

# Stations of the corridor, searched case-insensitively in stop names.
STATION_A_KW = "biederitz"
STATION_B_KW = "gerwisch"
STATION_A_NAME = "Biederitz"
STATION_B_NAME = "Gerwisch"

DEFAULT_VEHROUTE = Path("data/scenarios/sachsen-anhalt/output/vehroute.xml")
OUTPUT_IMAGE_NAME = "biederitz_gerwisch_diagram.png"

# Scenario artefacts relative to a scenario directory; first existing wins, so
# plain and gzipped variants are both accepted.
STOP_LIST_CANDIDATES = ("misc/train_stops.xml.gz", "misc/train_stops.xml")
MAPPING_CANDIDATES = ("misc/mapping.xml.gz", "misc/mapping.xml")

# Stop attributes that can carry a station name in name-based scenarios.
LOCATION_ATTRS = ("busStop", "lane", "edge")

# Time attributes tried in order, as (arrival candidates, departure candidates).
# SUMO logs the realised times as started/ended and the timetable as
# arrival/until, so the two sources plot a different diagram from the same file.
ACTUAL_TIMES = (("started", "arrival"), ("ended", "until"))
SCHEDULED_TIMES = (("arrival", "started"), ("until", "ended"))
TIME_SOURCES = {"actual": ACTUAL_TIMES, "scheduled": SCHEDULED_TIMES}

SECONDS_PER_MINUTE = 60.0
MINUTES_PER_HOUR = 60

# y positions of the two stations; the segment line runs between them.
Y_STATION_A = 0
Y_STATION_B = 1

FIGSIZE = (11, 6)
DPI = 300
DWELL_LINESTYLE = "-"
SEGMENT_LINESTYLE_A_TO_B = "-"
SEGMENT_LINESTYLE_B_TO_A = "--"


@dataclass(frozen=True)
class TrainStyle:
    """Legend entry and line appearance of one train class."""

    label: str
    color: str
    linewidth: float


HIGH_SPEED_STYLE = TrainStyle("ICE / HighSpeed", "#D90429", 2.2)
INTERCITY_STYLE = TrainStyle("IC / InterCity", "#0077B6", 1.8)
DEFAULT_STYLE = TrainStyle("Regional Line", "#2B9348", 1.2)

# (vehicle type keyword, vehicle id keyword, style); first match wins.
STYLE_RULES = (
    ("highspeed", "ICE", HIGH_SPEED_STYLE),
    ("intercity", "IC", INTERCITY_STYLE),
)


@dataclass(frozen=True)
class StopEvent:
    """Arrival and departure at one station, in minutes since simulation start."""

    arrival: float
    departure: float


@dataclass(frozen=True)
class TrainRun:
    """One train's passage over the corridor, seen at both stations."""

    id: str
    type: str
    at_a: StopEvent
    at_b: StopEvent

    @property
    def travels_a_to_b(self):
        """True if the train leaves station A no later than it reaches station B."""
        return self.at_a.departure <= self.at_b.arrival


@dataclass(frozen=True)
class Station:
    """One corridor station and the SUMO stop ids that belong to it."""

    name: str
    keyword: str
    stop_ids: frozenset = field(default_factory=frozenset)

    def matches(self, stop):
        """True if a vehroute ``<stop>`` element happens at this station."""
        if stop.get("busStop") in self.stop_ids:
            return True
        location = "_".join(stop.get(attr, "") for attr in LOCATION_ATTRS)
        return self.keyword in location.lower()


def parse_time(value):
    """Seconds from a SUMO time, either ``HH:MM:SS[.s]`` or plain seconds.

    Raises ``ValueError`` for anything else, so a missing or malformed time can
    never silently land at minute zero of the diagram.
    """
    if not isinstance(value, str) or not value:
        raise ValueError(f"not a SUMO time: {value!r}")

    if ":" not in value:
        return float(value)

    parts = value.split(":")
    if len(parts) != 3:
        raise ValueError(f"not a SUMO time: {value!r}")
    hours, minutes, seconds = (float(part) for part in parts)
    return hours * 3600.0 + minutes * SECONDS_PER_MINUTE + seconds


def format_clock(minutes, _position=None):
    """Render a minute offset as ``HH:MM``, counting past 24 h if needed."""
    total = int(round(minutes))
    return f"{total // MINUTES_PER_HOUR:02d}:{total % MINUTES_PER_HOUR:02d}"


def style_for(run):
    """Line style of a train run, derived from its type and its id."""
    for type_keyword, id_keyword, style in STYLE_RULES:
        if type_keyword in run.type or id_keyword in run.id:
            return style
    return DEFAULT_STYLE


def _open_xml(path):
    """Open a plain or gzipped XML file as text."""
    open_fn = gzip.open if str(path).endswith(".gz") else open
    return open_fn(path, "rt", encoding="utf-8")


def _first_existing(scenario_dir, relative_paths):
    """First existing artefact of the candidates, or None."""
    for relative in relative_paths:
        candidate = scenario_dir / relative
        if candidate.is_file():
            return candidate
    return None


def _gtfs_stop_ids(stop_list_path, keyword):
    """GTFS stop ids whose name contains ``keyword`` (case-insensitive)."""
    with _open_xml(stop_list_path) as handle:
        root = ET.parse(handle).getroot()

    return {
        stop.get("id")
        for stop in root.iter("stop")
        if keyword in stop.get("name", "").lower()
    }


def _mapped_stop_ids(mapping_path, gtfs_stop_ids):
    """SUMO stop ids that ``mapping.xml`` assigns to the given GTFS stop ids."""
    with _open_xml(mapping_path) as handle:
        root = ET.parse(handle).getroot()

    sumo_ids = set()
    for entry in root.iter("entry"):
        if entry.get("value") in gtfs_stop_ids:
            sumo_ids.update(
                option.get("stop_id") for option in entry.iter("stop_option")
            )
    return sumo_ids


def resolve_station_stop_ids(scenario_dir, keyword):
    """SUMO stop ids of the station matching ``keyword``.

    Returns an empty set when the scenario carries no stop list or no mapping;
    the caller then falls back to keyword matching on the stop ids themselves.
    """
    stop_list_path = _first_existing(scenario_dir, STOP_LIST_CANDIDATES)
    mapping_path = _first_existing(scenario_dir, MAPPING_CANDIDATES)
    if stop_list_path is None or mapping_path is None:
        return frozenset()

    gtfs_ids = _gtfs_stop_ids(stop_list_path, keyword)
    if not gtfs_ids:
        return frozenset()

    return frozenset(_mapped_stop_ids(mapping_path, gtfs_ids))


def load_stations(scenario_dir):
    """The two corridor stations, in the order they sit on the y axis."""
    return tuple(
        Station(
            name=name,
            keyword=keyword,
            stop_ids=resolve_station_stop_ids(scenario_dir, keyword),
        )
        for name, keyword in (
            (STATION_A_NAME, STATION_A_KW),
            (STATION_B_NAME, STATION_B_KW),
        )
    )


def _minutes(stop, attribute_names):
    """First parsable time among ``attribute_names``, in minutes, else None."""
    for attribute in attribute_names:
        try:
            return parse_time(stop.get(attribute)) / SECONDS_PER_MINUTE
        except ValueError:
            continue
    return None


def _stop_event(stop, times):
    """Arrival/departure of one stop, or None if it carries no usable time."""
    arrival_attrs, departure_attrs = times

    arrival = _minutes(stop, arrival_attrs)
    if arrival is None:
        return None

    departure = _minutes(stop, departure_attrs)
    # A stop the train never left is drawn as a zero-length dwell.
    return StopEvent(arrival=arrival, departure=arrival if departure is None else departure)


def parse_corridor_runs(vehroute_path, stations, times=ACTUAL_TIMES):
    """Train runs from a vehroute output that call at both corridor stations.

    ``stations`` is the pair returned by :func:`load_stations`; ``times``
    selects :data:`ACTUAL_TIMES` or :data:`SCHEDULED_TIMES`.
    """
    station_a, station_b = stations

    with _open_xml(vehroute_path) as handle:
        root = ET.parse(handle).getroot()

    runs = []
    for vehicle in root.iter("vehicle"):
        at_a, at_b = None, None
        for stop in vehicle.iter("stop"):
            if station_a.matches(stop):
                at_a = _stop_event(stop, times) or at_a
            elif station_b.matches(stop):
                at_b = _stop_event(stop, times) or at_b

        # Only a train seen at both stations defines a segment line.
        if at_a is not None and at_b is not None:
            runs.append(
                TrainRun(
                    id=vehicle.get("id"),
                    type=vehicle.get("type", "default"),
                    at_a=at_a,
                    at_b=at_b,
                )
            )
    return runs


def _draw_run(axes, run, style):
    """Draw one train: dwell at the origin, the segment, dwell at the destination."""
    if run.travels_a_to_b:
        origin, destination = (run.at_a, Y_STATION_A), (run.at_b, Y_STATION_B)
        segment_linestyle = SEGMENT_LINESTYLE_A_TO_B
    else:
        origin, destination = (run.at_b, Y_STATION_B), (run.at_a, Y_STATION_A)
        segment_linestyle = SEGMENT_LINESTYLE_B_TO_A

    for event, y in (origin, destination):
        axes.plot(
            [event.arrival, event.departure],
            [y, y],
            color=style.color,
            linewidth=style.linewidth,
            linestyle=DWELL_LINESTYLE,
        )

    (departed, y_origin), (arrived, y_destination) = origin, destination
    axes.plot(
        [departed.departure, arrived.arrival],
        [y_origin, y_destination],
        color=style.color,
        linewidth=style.linewidth,
        linestyle=segment_linestyle,
    )


def _add_legend(axes, styles):
    """Legend built from proxy lines, so the swatches do not depend on draw order."""
    if not styles:
        return
    handles = [
        Line2D([], [], color=style.color, linewidth=style.linewidth, label=style.label)
        for style in styles
    ]
    axes.legend(
        handles=handles,
        bbox_to_anchor=(1.02, 1),
        loc="upper left",
        fontsize=10,
    )


def build_diagram(runs, stations, time_source_name="actual"):
    """Render the corridor runs into a matplotlib figure."""
    station_a, station_b = stations
    figure, axes = plt.subplots(figsize=FIGSIZE)

    used_styles = []
    for run in runs:
        style = style_for(run)
        if style not in used_styles:
            used_styles.append(style)
        _draw_run(axes, run, style)

    axes.set_yticks([Y_STATION_A, Y_STATION_B])
    axes.set_yticklabels(
        [station_a.name, station_b.name], fontsize=12, fontweight="bold"
    )
    axes.xaxis.set_major_formatter(FuncFormatter(format_clock))
    axes.set_xlabel("Time (HH:MM since simulation start)", fontsize=11)
    axes.set_ylabel("Station", fontsize=11)
    axes.set_title(
        f"Single-Segment Train Diagram: {station_a.name} - {station_b.name} "
        f"({time_source_name} times, dashed = {station_b.name} -> {station_a.name})",
        fontsize=13,
        fontweight="bold",
    )
    axes.grid(True, linestyle=":", alpha=0.6)

    _add_legend(axes, used_styles)
    figure.tight_layout()
    return figure


def _parse_args(argv):
    """Command line of the diagram script."""
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "--vehroute",
        type=Path,
        default=DEFAULT_VEHROUTE,
        help="SUMO vehroute output, plain or gzipped (default: %(default)s)",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help=f"target image (default: <vehroute dir>/{OUTPUT_IMAGE_NAME})",
    )
    parser.add_argument(
        "--scenario-dir",
        type=Path,
        default=None,
        help="scenario root holding misc/ (default: parent of the vehroute dir)",
    )
    parser.add_argument(
        "--times",
        choices=sorted(TIME_SOURCES),
        default="actual",
        help="plot realised (started/ended) or scheduled (arrival/until) times",
    )
    return parser.parse_args(argv)


def main(argv=None):
    """Render the corridor diagram; returns a process exit code."""
    args = _parse_args(argv)

    if not args.vehroute.is_file():
        print(
            f"error: {args.vehroute} not found; run the simulation first.",
            file=sys.stderr,
        )
        return 1

    scenario_dir = args.scenario_dir or args.vehroute.parent.parent
    output_image = args.output or args.vehroute.parent / OUTPUT_IMAGE_NAME

    stations = load_stations(scenario_dir)
    for station in stations:
        if not station.stop_ids:
            print(
                f"warning: no stop ids resolved for {station.name} in {scenario_dir}; "
                f"falling back to keyword matching on {LOCATION_ATTRS}.",
                file=sys.stderr,
            )

    runs = parse_corridor_runs(args.vehroute, stations, times=TIME_SOURCES[args.times])
    print(
        f"{len(runs)} trains call at both {stations[0].name} and {stations[1].name} "
        f"({args.times} times)"
    )

    figure = build_diagram(runs, stations, time_source_name=args.times)
    output_image.parent.mkdir(parents=True, exist_ok=True)
    figure.savefig(output_image, dpi=DPI)
    plt.close(figure)
    print(f"saved diagram: {output_image}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
