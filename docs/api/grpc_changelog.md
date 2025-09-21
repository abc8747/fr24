# Changelog

All known changes of the gRPC messages are documented here.

Client versions are usually updated every 5 days, most frequently on Mon/Tue 10am.
This list is not exhaustive.

## `25.261.0637` (2025-09-18)
- add field: `FlightDetailsResponse.positionBuffer`, `FollowFlightResponse.positionBuffer`, `TrailPoint.source`

## `25.135.1104` (2025-05-15)
- add field: `Icon.CONC`
- add message: `FlightProgress`, `FlightDetailsRequest`, `FlightDetailsResponse`, `PlaybackFlightRequest`, `PlaybackFlightResponse`

## `25.056.2130` (2025-02-25)
- rename field: `ExtendedFlightInfo.timestamp`
- add field: `Flight.timestamp_ms`

## `24.353.1121` (2024-12-19)

- rename fields: `AirlineFilterType::OPERATED_AS`, `Stats.sources`
- add field: `Schedule.progress_pct`, `ExtendedFlightInfo.server_time_ms`
- fix field type: `FlightProgress.progress_pct`

## `24.333.0902` (2024-11-28)

- add field: `Flight.position_buffer`
- add message: `RecentPosition`, `PositionBuffer`
- add field: `FlightStage::DIVERSION`

## `24.288.0818` (2024-10-14)
- rename fields: `FlightStage::ASCENDING`, `FlightStage::DESCENDING`

## `24.200.1841` (2024-07-18)
- add field: `FlightProgress.progress_pct`
- add message: `HistoricTrailRequest`

## `24.184.2001` (2024-07-02)
- add field: `FlightProgress.delay_status`

## `24.171.1153` (2024-06-19)
- update message: `FlightProgress`
- update message: `FollowFlightRequest.restriction_mode`

## `24.169.0808` (2024-06-17)

- rename fields: `RestrictionVisibility`
- add message: `Duration`, `Tick`
- add message: `RadarHistoryRecord`
- add message: `FetchSearchIndexRequest`, `FetchSearchIndexResponse`
- add message: `ImageInfo`, `AircraftInfo`, `Point`, `Coordinate`, `Fix`, `AltArrival`, `FlightPlan`, `ScheduleInfo`, `FlightStage`, `FlightProgress`, `ExtendedFlightInfo`, `TrailPoint`
- add message: `LiveTrailRequest`, `LiveTrailResponse`
- add message: `FollowedFlight`, `TopFlightsRequest`, `TopFlightsResponse`

## `23.108.1135` (2023-04-18)

- gRPC endpoint introduced.

