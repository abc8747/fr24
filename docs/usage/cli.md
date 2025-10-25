# CLI

List all commands and show help:

```console
--8<-- "docs/usage/cli_output.txt:fr24"
```

### `live-feed` & `live-feed-playback`

Dump the current (or playback of) live feed data.

=== "Shell"

    ```sh
    fr24 live-feed --help
    # by default, parquet
    fr24 live-feed --bounding-box "42.0,52.0,-8.0,10.0"

    # write to stdout in csv format
    fr24 live-feed --bounding-box "42.0,52.0,-8.0,10.0" --format csv -o -

    # at a specific time
    fr24 live-feed-playback --bounding-box "42.0,52.0,-8.0,10.0" --timestamp "2024-01-01T12:00:00"
    ```

=== "Help Output (`live-feed`)"
    ```console
    --8<-- "docs/usage/cli_output.txt:fr24_live-feed"
    ```

=== "Help Output (`live-feed-playback`)"
    ```console
    --8<-- "docs/usage/cli_output.txt:fr24_live-feed-playback"
    ```

=== "Example Output"
    ```console
    $ fr24 live-feed --bounding-box "42.0,52.0,-8.0,10.0"
    [00:00:00] INFO     using environment `subscription_key` and      __init__.py:98
                    `token`                                                     
    [00:00:00] INFO     HTTP Request: POST                           _client.py:1740
                        https://data-feed.flightradar24.com/fr24.fee                
                        d.api.v1.Feed/LiveFeed "HTTP/2 200 OK"                      
               INFO     wrote 982 rows to                               utils.py:229
                           `/home/user/live_feed.parquet`

    $ duckdb -c "describe select * from 'live_feed.parquet';"
    ┌─────────────────┬──────────────────────┬─────────┬───┬─────────┬─────────┐
    │   column_name   │     column_type      │  null   │ … │ default │  extra  │
    │     varchar     │       varchar        │ varchar │   │ varchar │ varchar │
    ├─────────────────┼──────────────────────┼─────────┼───┼─────────┼─────────┤
    │ timestamp       │ TIMESTAMP WITH TIM…  │ YES     │ … │ NULL    │ NULL    │
    │ flightid        │ UINTEGER             │ YES     │ … │ NULL    │ NULL    │
    │ latitude        │ FLOAT                │ YES     │ … │ NULL    │ NULL    │
    │ longitude       │ FLOAT                │ YES     │ … │ NULL    │ NULL    │
    │ track           │ USMALLINT            │ YES     │ … │ NULL    │ NULL    │
    │ altitude        │ INTEGER              │ YES     │ … │ NULL    │ NULL    │
    │ ground_speed    │ SMALLINT             │ YES     │ … │ NULL    │ NULL    │
    │ on_ground       │ BOOLEAN              │ YES     │ … │ NULL    │ NULL    │
    │ callsign        │ VARCHAR              │ YES     │ … │ NULL    │ NULL    │
    │ source          │ UTINYINT             │ YES     │ … │ NULL    │ NULL    │
    │ registration    │ VARCHAR              │ YES     │ … │ NULL    │ NULL    │
    │ origin          │ VARCHAR              │ YES     │ … │ NULL    │ NULL    │
    │ destination     │ VARCHAR              │ YES     │ … │ NULL    │ NULL    │
    │ typecode        │ VARCHAR              │ YES     │ … │ NULL    │ NULL    │
    │ eta             │ UINTEGER             │ YES     │ … │ NULL    │ NULL    │
    │ squawk          │ USMALLINT            │ YES     │ … │ NULL    │ NULL    │
    │ vertical_speed  │ SMALLINT             │ YES     │ … │ NULL    │ NULL    │
    │ position_buffer │ STRUCT(delta_lat I…  │ YES     │ … │ NULL    │ NULL    │
    ├─────────────────┴──────────────────────┴─────────┴───┴─────────┴─────────┤
    │ 18 rows                                              6 columns (5 shown) │
    └──────────────────────────────────────────────────────────────────────────┘
    ```

### `flight-list` & `flight-list-all`

Dump the flight list for a given registration or flight number.

=== "Shell"

    ```sh
    fr24 flight-list --help
    fr24 flight-list --reg B-HPB -o - --format csv
    fr24 flight-list-all --flight CX488 -o cache
    ```

=== "Help Output (`flight-list`)"

    ```console
    --8<-- "docs/usage/cli_output.txt:fr24_flight-list"
    ```

=== "Help Output (`flight-list-all`)"

    ```console
    --8<-- "docs/usage/cli_output.txt:fr24_flight-list-all"
    ```

=== "Example Output"

    ```console
    $ fr24 flight-list --reg B-HPB -o - --format csv
    [00:00:00] INFO     using environment `subscription_key` and      __init__.py:98
                    `token`                                                     
    [00:00:00] INFO     HTTP Request: GET                            _client.py:1740
                        https://api.flightradar24.com/common/v1/flig                
                        ht/list.json?query=B-HPB&fetchBy=reg&page=1&                
                        limit=10 "HTTP/200 OK"                                                     
    flight_id,number,callsign,icao24,registration,typecode,origin,destination,status,STOD,ETOD,ATOD,STOA,ETOA,ATOA
    996322074,CX742,CPA742,7901768,B-HPB,A21N,VVNB,VHHH,Landed 21:46,2025-07-23T12:05:00.000+0000,,2025-07-23T12:23:33.000+0000,2025-07-23T14:10:00.000+0000,,2025-07-23T13:46:15.000+0000
    996286687,CX743,CPA743,7901768,B-HPB,A21N,VHHH,VVNB,Landed 17:51,2025-07-23T08:55:00.000+0000,,2025-07-23T09:21:44.000+0000,2025-07-23T11:05:00.000+0000,,2025-07-23T10:51:39.000+0000
    996244655,CX608,CPA608,7901768,B-HPB,A21N,VDPP,VHHH,Landed 14:51,2025-07-23T04:25:00.000+0000,,2025-07-23T04:39:01.000+0000,2025-07-23T07:15:00.000+0000,,2025-07-23T06:51:29.000+0000
    996213423,CX607,CPA607,7901768,B-HPB,A21N,VHHH,VDPP,Landed 10:04,2025-07-23T00:35:00.000+0000,,2025-07-23T01:00:29.000+0000,2025-07-23T03:15:00.000+0000,,2025-07-23T03:04:00.000+0000
    996039556,CX926,CPA926,7901768,B-HPB,A21N,RPVM,VHHH,Landed 21:47,2025-07-22T11:15:00.000+0000,,2025-07-22T11:25:42.000+0000,2025-07-22T14:15:00.000+0000,,2025-07-22T13:47:05.000+0000
    996004405,CX925,CPA925,7901768,B-HPB,A21N,VHHH,RPVM,Landed 17:56,2025-07-22T07:15:00.000+0000,,2025-07-22T07:41:27.000+0000,2025-07-22T10:05:00.000+0000,,2025-07-22T09:56:45.000+0000
    995970644,CX906,CPA906,7901768,B-HPB,A21N,RPLL,VHHH,Landed 13:10,2025-07-22T02:45:00.000+0000,,2025-07-22T03:31:12.000+0000,2025-07-22T05:15:00.000+0000,,2025-07-22T05:10:58.000+0000
    995937230,CX907,CPA907,7901768,B-HPB,A21N,VHHH,RPLL,Landed 09:42,2025-07-21T23:20:00.000+0000,,2025-07-21T23:55:22.000+0000,2025-07-22T01:35:00.000+0000,,2025-07-22T01:42:25.000+0000
    995808068,CX963,CPA963,7901768,B-HPB,A21N,ZSHC,VHHH,Landed 23:06,2025-07-21T11:35:00.000+0000,,2025-07-21T13:02:20.000+0000,2025-07-21T14:20:00.000+0000,,2025-07-21T15:06:00.000+0000
    995766910,CX962,CPA962,7901768,B-HPB,A21N,VHHH,ZSHC,Landed 19:12,2025-07-21T08:00:00.000+0000,,2025-07-21T09:22:59.000+0000,2025-07-21T10:20:00.000+0000,,2025-07-21T11:12:56.000+0000
            INFO     wrote 10 rows to `<_io.BufferedWriter           utils.py:229
                        name='<stdout>'>`
    ```

### `playback`

Dump the historical track playback data.

=== "Shell"

    ```sh
    fr24 playback --help
    fr24 playback --flight-id 2d81a27 -o playback.parquet
    ```

=== "Help Output"

    ```console
    --8<-- "docs/usage/cli_output.txt:fr24_playback"
    ```

### `nearest-flights`, `live-flights-status`, `flight-details`, `top-flights`, `playback-flight`

Dump various gRPC-based flight data.

```sh
fr24 nearest-flights --lat 22.3 --lon 113.9
fr24 live-flights-status --flight-ids 3963916d 3963a803
fr24 flight-details --flight-id 3963916d
fr24 top-flights --limit 5
fr24 playback-flight --flight-id 3963916d --timestamp "2025-07-24T00:00:00"
```

```console
--8<-- "docs/usage/cli_output.txt:fr24_nearest-flights"
```

```console
--8<-- "docs/usage/cli_output.txt:fr24_live-flights-status"
```

```console
--8<-- "docs/usage/cli_output.txt:fr24_flight-details"
```

```console
--8<-- "docs/usage/cli_output.txt:fr24_top-flights"
```

```console
--8<-- "docs/usage/cli_output.txt:fr24_playback-flight"
```

### `tui`

Start the Text User Interface.

```sh
fr24 tui
```
