from __future__ import annotations

import asyncio
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterator, Literal, TypeVar

import httpx
from textual import on
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import ScrollableContainer
from textual.widgets import (
    DataTable,
    Footer,
    Header,
    Input,
    Label,
    Static,
)

from fr24.authentication import login
from fr24.json import (
    AirportListParams,
    FindParams,
    FlightListParams,
    PlaybackParams,
    airport_list,
    airport_list_parse,
    find,
    find_parse,
    flight_list,
    flight_list_parse,
    get_json_headers,
    playback,
    playback_parse,
)
from fr24.tui.formatters import Aircraft, Airport, Time
from fr24.tui.widgets import AircraftWidget, AirportWidget, FlightWidget
from fr24.types import IntoTimestamp, IntTimestampS
from fr24.types.json import (
    Authentication,
    FlightList,
    FlightListItem,
    is_schedule,
)
from fr24.utils import get_current_timestamp, to_unix_timestamp

T = TypeVar("T")


def flatten(*args: list[T]) -> Iterator[T]:
    for elt in args:
        yield from elt


class SearchBlock(Static):
    def compose(self) -> ComposeResult:
        yield Label("date")
        self.date_input = Input(id="date")
        self.date_input.value = f"{datetime.now(tz=timezone.utc):%Y-%m-%d}"
        yield self.date_input
        yield AircraftWidget(name="aircraft")
        yield FlightWidget(name="number")
        yield AirportWidget(id="departure", name="origin")
        yield AirportWidget(id="arrival", name="destination")


# -- Application --


class FR24(App[None]):
    CSS_PATH = "style.tcss"
    BINDINGS = [  # noqa: RUF012
        ("q", "quit", "Quit"),
        ("l", "login", "Log in"),
        ("r", "refresh", "Refresh"),  # TODO
        ("/", "search", "Search"),
        ("s", "save", "Save"),
        ("c", "clear", "Clear"),
        Binding("escape", "escape", show=False),
    ]
    line_info: dict[str, str] = {}  # noqa: RUF012

    def compose(self) -> ComposeResult:
        self.client = httpx.AsyncClient(http1=False, http2=True)
        self.auth: Authentication | None = None
        self.json_headers = httpx.Headers(get_json_headers())
        self.search_visible = True
        yield Header()
        yield Footer()
        yield SearchBlock()
        yield ScrollableContainer(DataTable())

    def on_mount(self) -> None:
        self.title = "FlightRadar24"
        table = self.query_one(DataTable)
        table.cursor_type = "row"
        table.add_columns(
            "date",
            "number",
            "callsign",
            "aircraft",
            "from",
            "to",
            "STD",
            "ATD",
            "STA",
            "status",
            "flightid",
        )

    def action_search(self) -> None:
        self.search_visible = not self.search_visible
        if self.search_visible:
            self.query_one(SearchBlock).remove_class("hidden")
        else:
            self.query_one(SearchBlock).add_class("hidden")
            self.query_one(DataTable).focus()

    def action_clear(self) -> None:
        for widget in self.query(Input):
            if widget.id != "date":
                widget.value = ""

    async def action_escape(self) -> None:
        if not self.search_visible:
            await self.action_quit()

        self.search_visible = False
        self.query_one(SearchBlock).add_class("hidden")
        self.query_one(DataTable).focus()

    async def action_login(self) -> None:
        self.auth = await login(self.client)
        if self.auth is not None:
            identity = self.auth.get("user", {}).get("identity") or self.auth[
                "userData"
            ].get("identity")
            self.sub_title = (
                f"(authenticated: {identity})"
                if identity
                else "(authenticated)"
            )
            self.query_one(Header).add_class("authenticated")
            self.query_one(Footer).add_class("authenticated")

    async def on_data_table_row_selected(
        self, event: DataTable.RowSelected
    ) -> None:
        columns = [c.label.plain for c in event.data_table.columns.values()]
        self.line_info = dict(
            zip(columns, event.data_table.get_row(event.row_key))
        )

    async def action_save(self) -> None:
        if len(self.line_info) == 0:
            return
        date = self.line_info["date"] + " " + self.line_info["STD"]
        timestamp = to_unix_timestamp(date, format="%Y-%m-%d %H:%MZ")
        assert timestamp != "now"
        result = playback_parse(
            await playback(
                self.client,
                PlaybackParams(
                    flight_id=self.line_info["flightid"],
                    timestamp=timestamp,
                ),
                self.json_headers,
                auth=self.auth,
            )
        ).unwrap()
        filename = f"{self.line_info['flightid']}.json"
        self.notify(f"Saving to {filename}")
        Path(filename).write_text(json.dumps(result, indent=2))

    @on(Input.Submitted)
    async def action_refresh(self) -> None:
        ts_str = self.query_one("#date", Input).value
        ts = to_unix_timestamp(ts_str if ts_str else "now")

        aircraft_widget = self.query_one(AircraftWidget)
        if aircraft := aircraft_widget.aircraft_id:
            await self.lookup_aircraft(aircraft, ts=ts)
            return
        number_widget = self.query_one(FlightWidget)
        if number := number_widget.number:
            await self.lookup_number(number, ts=ts)
            return
        departure_widget = self.query_one("#departure", AirportWidget)
        arrival_widget = self.query_one("#arrival", AirportWidget)
        if departure := departure_widget.airport_id:
            if arrival := arrival_widget.airport_id:
                ts = get_current_timestamp() if ts == "now" else ts
                await self.lookup_city_pair(departure, arrival, ts=ts)
                return
            await self.lookup_departure(departure, ts=ts)
            return
        if arrival := arrival_widget.airport_id:
            await self.lookup_arrival(arrival, ts=ts)
            return

    async def lookup_aircraft(
        self, value: str, ts: IntoTimestamp | Literal["now"]
    ) -> None:
        results = flight_list_parse(
            await flight_list(
                self.client,
                FlightListParams(
                    reg=value,
                    limit=100,
                    timestamp=ts,
                ),
                self.json_headers,
                auth=self.auth,
            )
        ).unwrap()
        self.update_table(results["result"]["response"].get("data", None))

    async def lookup_number(
        self, value: str, ts: IntoTimestamp | Literal["now"]
    ) -> None:
        results = flight_list_parse(
            await flight_list(
                self.client,
                FlightListParams(
                    flight=value,
                    limit=100,
                    timestamp=ts,
                ),
                self.json_headers,
                auth=self.auth,
            )
        ).unwrap()
        self.update_table(results["result"]["response"].get("data", None))

    async def lookup_city_pair(
        self, departure: str, arrival: str, ts: IntTimestampS
    ) -> None:
        results = find_parse(
            await find(
                self.client,
                FindParams(query=f"{departure}-{arrival}"),
                self.json_headers,
                auth=self.auth,
            )
        ).unwrap()
        if results is None or results["stats"]["count"]["schedule"] == 0:
            return
        flight_numbers = list(
            sched["detail"]["flight"]
            for sched in results["results"]
            if is_schedule(sched)
        )
        flight_lists: list[FlightList] = []
        for value in flight_numbers:
            flight_list_request = FlightListParams(
                flight=value, limit=10, timestamp=ts
            )
            try:
                res = flight_list_parse(
                    await flight_list(
                        self.client,
                        flight_list_request,
                        self.json_headers,
                        auth=self.auth,
                    )
                ).unwrap()
            except httpx.HTTPStatusError as exc:
                if exc.response.status_code == 402:  # payment required
                    await asyncio.sleep(10)
                    res = flight_list_parse(
                        await flight_list(
                            self.client,
                            flight_list_request,
                            self.json_headers,
                            auth=self.auth,
                        )
                    ).unwrap()
                else:
                    raise exc

            flight_lists.append(res)

            compacted_view = list(
                flatten(
                    *(
                        entry
                        for e in flight_lists
                        if (
                            (entry := e["result"]["response"]["data"])
                            is not None
                        )
                    )
                )
            )

            def by_departure_time(elt: FlightListItem) -> int:
                departure_time = elt["time"]["scheduled"]["departure"]
                return -departure_time if departure_time else 0

            compacted_view = sorted(
                (
                    entry
                    for entry in compacted_view
                    if (sobt := entry["time"]["scheduled"]["departure"])
                    is not None
                    and sobt < ts + 3600 * 24
                ),
                key=by_departure_time,
            )
            self.update_table(compacted_view)

            await asyncio.sleep(2)

    async def lookup_arrival(
        self, value: str, ts: IntoTimestamp | Literal["now"]
    ) -> None:
        results = airport_list_parse(
            await airport_list(
                self.client,
                AirportListParams(
                    airport=value,
                    mode="arrivals",
                    limit=100,
                    timestamp=ts,
                ),
                self.json_headers,
                auth=self.auth,
            )
        ).unwrap()
        s = results["result"]["response"]["airport"]["pluginData"]["schedule"]
        data = s["arrivals"].get("data", None)
        if data is not None:
            self.update_table(
                [  # TODO add airport info from
                    elt["flight"]  # type: ignore
                    for elt in data
                ]
            )

    async def lookup_departure(
        self, value: str, ts: IntoTimestamp | Literal["now"]
    ) -> None:
        results = airport_list_parse(
            await airport_list(
                self.client,
                AirportListParams(
                    airport=value,
                    mode="departures",
                    limit=100,
                    timestamp=ts,
                ),
                self.json_headers,
                auth=self.auth,
            )
        ).unwrap()
        s = results["result"]["response"]["airport"]["pluginData"]["schedule"]
        data = s["departures"].get("data", None)
        if data is not None:
            self.update_table(
                [  # TODO add airport info from
                    elt["flight"]  # type: ignore
                    for elt in data
                ]
            )

    def update_table(self, data: None | list[FlightListItem]) -> None:
        table = self.query_one(DataTable)
        table.clear()
        if data is None:
            return
        table.add_rows(
            [
                (
                    f"{Time(entry['time']['scheduled']['departure']):%Y-%m-%d}",
                    entry["identification"]["number"]["default"],
                    entry["identification"]["callsign"],
                    f"{Aircraft(entry['aircraft']):%r (%c)}",
                    f"{Airport(entry['airport']['origin']):%y (%o)}",
                    f"{Airport(entry['airport']['destination']):%y (%o)}",
                    f"{Time(entry['time']['scheduled']['departure']):%H:%MZ}",
                    f"{Time(entry['time']['real']['departure']):%H:%MZ}",
                    f"{Time(entry['time']['scheduled']['arrival']):%H:%MZ}",
                    entry["status"]["text"],
                    entry["identification"]["id"],
                )
                for entry in data
            ]
        )


def main() -> None:
    app = FR24()
    app.run()


if __name__ == "__main__":
    main()
