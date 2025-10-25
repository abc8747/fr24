# ruff: noqa
# mypy: disable-error-code="top-level-await, no-redef"
# %%
# --8<-- [start:script]
from fr24 import FR24, FR24Cache
from rich import print


async def my_top_flights() -> None:
    async with FR24() as fr24:
        result = await fr24.top_flights.fetch(limit=10)
        print(result)
        print(result.to_dict())
        print(result.to_polars())
        result.write_table(FR24Cache.default())


await my_top_flights()
# --8<-- [end:script]
# %%
"""
# --8<-- [start:result]
TopFlightsResult(
    request=TopFlightsParams(limit=10),
    response=<Response [200 OK]>,
    timestamp=1748188667
)
# --8<-- [end:result]
# --8<-- [start:dict]
{
    'scoreboard_list': [
        {
            'flight_id': 981367259,
            'live_clicks': 1438,
            'total_clicks': 1438,
            'flight_number': 'DOC72',
            'callsign': 'DOC72',
            'from_iata': 'FRG',
            'from_city': 'Farmingdale',
            'to_iata': 'FRG',
            'to_city': 'Farmingdale',
            'type': 'B29',
            'full_description': 'Boeing TB-29 Superfortress'
        },
        ...
        {
            'flight_id': 981290224,
            'live_clicks': 514,
            'total_clicks': 514,
            'flight_number': 'SQ326',
            'callsign': 'SIA326',
            'from_iata': 'SIN',
            'from_city': 'Singapore',
            'to_iata': 'FRA',
            'to_city': 'Frankfurt',
            'type': 'A388',
            'full_description': 'Airbus A380-841'
        }
    ]
}
# --8<-- [end:dict]
# --8<-- [start:polars]
shape: (10, 12)
┌───────────┬─────────────┬────────────┬────────────┬───┬─────────┬────────────┬──────┬────────────┐
│ flight_id ┆ live_clicks ┆ total_clic ┆ flight_num ┆ … ┆ to_iata ┆ to_city    ┆ type ┆ full_descr │
│ ---       ┆ ---         ┆ ks         ┆ ber        ┆   ┆ ---     ┆ ---        ┆ ---  ┆ iption     │
│ u32       ┆ u32         ┆ ---        ┆ ---        ┆   ┆ str     ┆ str        ┆ str  ┆ ---        │
│           ┆             ┆ u32        ┆ str        ┆   ┆         ┆            ┆      ┆ str        │
╞═══════════╪═════════════╪════════════╪════════════╪═══╪═════════╪════════════╪══════╪════════════╡
│ 981367259 ┆ 1438        ┆ 1438       ┆ DOC72      ┆ … ┆ FRG     ┆ Farmingdal ┆ B29  ┆ Boeing     │
│           ┆             ┆            ┆            ┆   ┆         ┆ e          ┆      ┆ TB-29 Supe │
│           ┆             ┆            ┆            ┆   ┆         ┆            ┆      ┆ rfortress  │
│ 981383686 ┆ 1066        ┆ 1066       ┆ RRR4952    ┆ … ┆ RZE     ┆ Rzeszow    ┆ A400 ┆ Airbus     │
│           ┆             ┆            ┆            ┆   ┆         ┆            ┆      ┆ A400M      │
│           ┆             ┆            ┆            ┆   ┆         ┆            ┆      ┆ Atlas      │
│ 981393352 ┆ 890         ┆ 890        ┆            ┆ … ┆         ┆            ┆ DC3  ┆ Douglas    │
│           ┆             ┆            ┆            ┆   ┆         ┆            ┆      ┆ DC-3C      │
│ 981407748 ┆ 831         ┆ 831        ┆            ┆ … ┆         ┆            ┆ EC35 ┆ Airbus Hel │
│           ┆             ┆            ┆            ┆   ┆         ┆            ┆      ┆ icopters   │
│           ┆             ┆            ┆            ┆   ┆         ┆            ┆      ┆ H135       │
│ 981398120 ┆ 707         ┆ 707        ┆            ┆ … ┆ RTM     ┆ Rotterdam  ┆ SR22 ┆ Cirrus     │
│           ┆             ┆            ┆            ┆   ┆         ┆            ┆      ┆ SR22       │
│ 981400483 ┆ 673         ┆ 673        ┆            ┆ … ┆         ┆            ┆ BR23 ┆ BRM Aero   │
│           ┆             ┆            ┆            ┆   ┆         ┆            ┆      ┆ Bristell   │
│           ┆             ┆            ┆            ┆   ┆         ┆            ┆      ┆ B23        │
│ 981402316 ┆ 616         ┆ 616        ┆            ┆ … ┆         ┆            ┆ DHC6 ┆ Viking     │
│           ┆             ┆            ┆            ┆   ┆         ┆            ┆      ┆ DHC-6-400  │
│           ┆             ┆            ┆            ┆   ┆         ┆            ┆      ┆ Twin Otter │
│ 981368239 ┆ 554         ┆ 554        ┆ VJT750     ┆ … ┆ GIG     ┆ Rio de     ┆ GL7T ┆ Bombardier │
│           ┆             ┆            ┆            ┆   ┆         ┆ Janeiro    ┆      ┆ Global     │
│           ┆             ┆            ┆            ┆   ┆         ┆            ┆      ┆ 7500       │
│ 981404508 ┆ 535         ┆ 535        ┆            ┆ … ┆         ┆            ┆ GLID ┆ Alexander  │
│           ┆             ┆            ┆            ┆   ┆         ┆            ┆      ┆ Schleicher │
│           ┆             ┆            ┆            ┆   ┆         ┆            ┆      ┆ ASK-23B    │
│ 981290224 ┆ 514         ┆ 514        ┆ SQ326      ┆ … ┆ FRA     ┆ Frankfurt  ┆ A388 ┆ Airbus     │
│           ┆             ┆            ┆            ┆   ┆         ┆            ┆      ┆ A380-841   │
└───────────┴─────────────┴────────────┴────────────┴───┴─────────┴────────────┴──────┴────────────┘
# --8<-- [end:polars]
"""
