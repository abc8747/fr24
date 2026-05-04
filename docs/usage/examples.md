# Overview

- Live Feed: low-level [`live_feed`][fr24.grpc.live_feed], service [`LiveFeedService`][fr24.service.LiveFeedService], cache `feed/{timestamp_s}.parquet`
- Live Feed Playback: low-level [`live_feed_playback`][fr24.grpc.live_feed_playback], service [`LiveFeedPlaybackService`][fr24.service.LiveFeedPlaybackService], cache `feed/{timestamp_s}.parquet`
- Nearest Flights: low-level [`nearest_flights`][fr24.grpc.nearest_flights], service [`NearestFlightsService`][fr24.service.NearestFlightsService], cache `nearest_flights/{lon_x1e6}_{lat_x1e6}_{timestamp_s}.parquet`
- Live Flight Status: low-level [`live_flights_status`][fr24.grpc.live_flights_status], service [`LiveFlightsStatusService`][fr24.service.LiveFlightsStatusService], cache `live_flights_status/{timestamp_s}.parquet`
- Follow Flight: low-level [`follow_flight_stream`][fr24.grpc.follow_flight_stream], service [`FollowFlightService`][fr24.service.FollowFlightService]
- Top Flights: low-level [`top_flights`][fr24.grpc.top_flights], service [`TopFlightsService`][fr24.service.TopFlightsService], cache `top_flights/{timestamp_s}.parquet`
- Flight Details: low-level [`flight_details`][fr24.grpc.flight_details], service [`FlightDetailsService`][fr24.service.FlightDetailsService], cache `flight_details/{flight_id}_{timestamp_s}.parquet`
- Playback Flight: low-level [`playback_flight`][fr24.grpc.playback_flight], service [`PlaybackFlightService`][fr24.service.PlaybackFlightService], cache `playback_flight/{flight_id}_{timestamp_s}.parquet`

You can find even more usage examples under [`tests/`](https://github.com/abc8747/fr24/tree/master/tests).

[Skip to Low Level API](#low-level-api)

## `FR24` services

### Low-Level Live Feed

This example is covered in detail in the [quickstart](./quickstart.md).

=== "Jupyter cell"

    ```py
    --8<-- "docs/usage/scripts/14_live_feed.py:script"
    ```

=== "`result`"

    ```py
    --8<-- "docs/usage/scripts/14_live_feed.py:result"
    ```

=== "`result.to_dict()`"

    ```py
    --8<-- "docs/usage/scripts/14_live_feed.py:dict"
    ```

=== "`result.to_polars()`"

    ```
    --8<-- "docs/usage/scripts/14_live_feed.py:polars"
    ```

### Live Feed Playback

Fetches the live feed three days ago.

=== "Jupyter cell"

    ```py hl_lines="4"
    --8<-- "docs/usage/scripts/14_live_feed.py:script2"
    ```

=== "`result.to_polars()`"

    ```
    --8<-- "docs/usage/scripts/14_live_feed.py:polars2"
    ```

### Low-Level Nearest Flights

=== "Jupyter cell"

    ```py
    --8<-- "docs/usage/scripts/15_nearest_flights.py:script"
    ```

=== "`result`"

    ```py
    --8<-- "docs/usage/scripts/15_nearest_flights.py:result"
    ```

=== "`result.to_dict()`"

    ```py
    --8<-- "docs/usage/scripts/15_nearest_flights.py:dict"
    ```

=== "`result.to_polars()`"

    ```
    --8<-- "docs/usage/scripts/15_nearest_flights.py:polars"
    ```

### Low-Level Live Flight Status

Retrieve the flight status for the closest flights from a location.

=== "Jupyter cell"

    ```py
    --8<-- "docs/usage/scripts/16_live_flights_status.py:script"
    ```

=== "`result`"

    ```py
    --8<-- "docs/usage/scripts/16_live_flights_status.py:result"
    ```

=== "`result.to_dict()`"

    ```py
    --8<-- "docs/usage/scripts/16_live_flights_status.py:dict"
    ```

=== "`result.to_polars()`"

    ```
    --8<-- "docs/usage/scripts/16_live_flights_status.py:polars"
    ```

### Follow Flight

Stream real-time updates to the state vector of an aircraft.

!!! note

    This is a streaming service which endlessly yields the latest updates.

    Unlike other services, it does not offer a default serialisation strategy.
    For a local setup, consider inserting the updates into SQLite or another
    sink manually.

    The first packet contains useful initial metadata and will not be
    re-transmitted in subsequent updates.

!!! tip

    The server often sends state vector packets every 1-60 seconds, but
    `httpx` by default closes the stream after 5 seconds. The example below
    increases the timeout to avoid premature closure.

=== "Jupyter cell"

    ```py
    --8<-- "docs/usage/scripts/18_follow_flight.py:script"
    ```

=== "`result.to_proto()`"

    ```proto
    --8<-- "docs/usage/scripts/18_follow_flight.py:proto"
    ```

### Top Flights

=== "Jupyter cell"

    ```py
    --8<-- "docs/usage/scripts/19_top_flights.py:script"
    ```

=== "`result`"

    ```py
    --8<-- "docs/usage/scripts/19_top_flights.py:result"
    ```

=== "`result.to_dict()`"

    ```py
    --8<-- "docs/usage/scripts/19_top_flights.py:dict"
    ```

=== "`result.to_polars()`"

    ```
    --8<-- "docs/usage/scripts/19_top_flights.py:polars"
    ```

### Flight Details

Retrieve detailed information about a flight.

=== "Jupyter cell"

    ```py
    --8<-- "docs/usage/scripts/22_flight_details.py:script"
    ```

=== "`result`"

    ```py
    --8<-- "docs/usage/scripts/22_flight_details.py:result"
    ```

=== "`result.to_dict()`"

    ```py
    --8<-- "docs/usage/scripts/22_flight_details.py:dict"
    ```

=== "`result.to_polars()`"

    ```
    --8<-- "docs/usage/scripts/22_flight_details.py:polars"
    ```

### Playback Flight

Retrieve detailed historical flight information including complete trail.

=== "Jupyter cell"

    ```py
    --8<-- "docs/usage/scripts/16_playback_flight.py:script"
    ```

=== "`result`"

    ```py
    --8<-- "docs/usage/scripts/16_playback_flight.py:result"
    ```

=== "`result.to_dict()`"

    ```py
    --8<-- "docs/usage/scripts/16_playback_flight.py:dict"
    ```

=== "`result.to_polars()`"

    ```
    --8<-- "docs/usage/scripts/16_playback_flight.py:polars"
    ```

## Low Level API

For maximum control, you can also use `fr24` in a procedural style. You will
have to manage the headers and authentication yourself. It is highly
recommended to use [services](#fr24-services) instead.

### Live Feed

Demonstrates custom bounding boxes.

=== "Jupyter cell"

    ```py
    --8<-- "docs/usage/scripts/34_live_feed.py:script0"
    ```

    1. The type is a `Result[LiveFeedResponse, ProtoError]`, and `.unwrap()`
       raises an exception on error.

=== "Protobuf Output"

    ```proto
    --8<-- "docs/usage/scripts/34_live_feed.py:output0"
    ```

=== "Dictionary Output"

    ```py
    --8<-- "docs/usage/scripts/34_live_feed.py:script1"
    ```

### Nearest Flights

=== "Jupyter cell"

    ```py
    --8<-- "docs/usage/scripts/35_nearest_flights.py:script0"
    ```

=== "Protobuf Output"

    ```proto
    --8<-- "docs/usage/scripts/35_nearest_flights.py:output0"
    ```

### Live Flight Status

=== "Jupyter cell"

    ```py
    --8<-- "docs/usage/scripts/36_live_flights_status.py:script0"
    ```

=== "Protobuf Output"

    ```proto
    --8<-- "docs/usage/scripts/36_live_flights_status.py:output0"
    ```

### Search Index

!!! warning "Unstable API: returns empty `DATA` frame"

=== "Jupyter cell"

    ```py
    --8<-- "docs/usage/scripts/37_search_index.py:script0"
    ```

=== "Protobuf Output"

    ```
    --8<-- "docs/usage/scripts/37_search_index.py:output0"
    ```

### Low-Level Follow Flight

See [above](#follow-flight) for more information.

=== "Jupyter cell"

    ```py
    --8<-- "docs/usage/scripts/38_follow_flight.py:script0"
    ```

=== "Protobuf Output"

    ```proto
    --8<-- "docs/usage/scripts/38_follow_flight.py:output0"
    ```

### Low-Level Top Flights

=== "Jupyter cell"

    ```py
    --8<-- "docs/usage/scripts/39_top_flights.py:script0"
    ```

=== "Protobuf Output"

    ```proto
    --8<-- "docs/usage/scripts/39_top_flights.py:output0"
    ```

### Live Trail

!!! warning "Unstable API: returns empty `DATA` frame as of Sep 2024"

=== "Jupyter cell"

    ```py
    --8<-- "docs/usage/scripts/40_live_trail.py:script0"
    ```

=== "Protobuf Output"

    ```proto
    --8<-- "docs/usage/scripts/40_live_trail.py:output0"
    ```

### Historic Trail

!!! warning "Unstable API: gateway timeout"

=== "Jupyter cell"

    ```py
    --8<-- "docs/usage/scripts/41_historic_trail.py:script0"
    ```

=== "Protobuf Output"

    ```proto
    --8<-- "docs/usage/scripts/41_historic_trail.py:output0"
    ```

### Flight Details

=== "Jupyter cell"

    ```py
    --8<-- "docs/usage/scripts/42_flight_details.py:script0"
    ```

=== "Protobuf Output"

    ```proto
    --8<-- "docs/usage/scripts/42_flight_details.py:output0"
    ```

### Low-Level Playback Flight

=== "Jupyter cell"

    ```py
    --8<-- "docs/usage/scripts/43_playback_flight.py:script0"
    ```

=== "Protobuf Output"

    ```proto
    --8<-- "docs/usage/scripts/43_playback_flight.py:output0"
    ```
