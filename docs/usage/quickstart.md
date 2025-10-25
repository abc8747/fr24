# Library Quickstart

Most code is developed using asynchronous programming, enabling parallel execution of multiple queries and achieve high performance.

Here is a quick example in case you are not familiar with this code style:

=== "Python Script"

    ```py
    --8<-- "docs/usage/scripts/00_introduction.py:script"
    ```
    
    1. Wrap your code in an `async` function
    2. `fetch()` is an asynchronous method - we need to `await` it
    3. `main()` returns a coroutine object which does not run immediately - we need to run it on the event loop. If you are using Jupyter, a bare `await main()` would do as well.

=== "`result`"

    ```py
    --8<-- "docs/usage/scripts/00_introduction.py:result"
    ```

=== "`result.to_proto()`"

    ```py
    --8<-- "docs/usage/scripts/00_introduction.py:result-proto"
    ```

=== "`result.to_dict()`"

    ```py
    --8<-- "docs/usage/scripts/00_introduction.py:result-dict"
    ```

=== "`result.to_polars()`"

    ```
    --8<-- "docs/usage/scripts/00_introduction.py:result-polars"
    ```

The following sections will break down what each line does under the hood.

## Initialisation

=== "`example.py`"

    ```py hl_lines="5"
    --8<-- "docs/usage/scripts/00_introduction.py:script-1"
    ```

When `FR24()` is first initialised, it creates an unauthenticated [HTTPX client](https://www.python-httpx.org/async/) under the hood. It also manages authentication (subscription key and tokens).

!!! question "How to authenticate?"

    ```py
    --8<-- "docs/usage/scripts/00_introduction.py:login"
    ```

    See [authentication](./authentication.md) for more details.

!!! question "How to pass in my own HTTPX client?"

    To share clients across code, pass it into the [fr24.FR24][] constructor.

    ```py
    --8<-- "docs/usage/scripts/00_introduction.py:client-sharing"
    ```

The `async with` statement ensures that it is properly authenticated by calling the login endpoint (if necessary).

## Data Fetching

Next, `fr24` contains multiple *services*, each of which [implements the `fetch` method][fr24.service.SupportsFetch]:

=== "`example.py`"

    ```py hl_lines="6"
    --8<-- "docs/usage/scripts/00_introduction.py:script-2"
    ```

=== "`result`"

    ```py
    --8<-- "docs/usage/scripts/00_introduction.py:result"
    ```

=== "`result.response.content`"

    ```
    --8<-- "docs/usage/scripts/00_introduction.py:result-response-content"
    ```

It returns a [wrapped context and response][fr24.service.LiveFeedResult], which contains:

- the [context related to the request][fr24.grpc.LiveFeedParams] under `result.request`;
- the raw [HTTPX response](https://www.python-httpx.org/api/#response) under `result.response`:
    - the **raw bytes under `result.response.content`**
    - the HTTP status under `result.response.status_code`
    - the response headers under `result.response.headers`

As you can see, the raw bytes seem to be jarbled, somewhat resembling records of aircraft. In fact, the live feed API uses [gRPC over HTTP2](https://github.com/grpc/grpc/blob/master/doc/PROTOCOL-HTTP2.md) and [protocol buffers](https://protobuf.dev/programming-guides/proto3/), a compact binary serialisation protocol.

A further decoding step is needed.

## Conversion to other formats

The `result` implements:

- [the `to_proto` method][fr24.proto.SupportsToProto], parsing it into a **protobuf message**
- [the `to_dict` method][fr24.utils.SupportsToDict], parsing it into a **Python dictionary**;
- [the `to_polars` method][fr24.utils.SupportsToPolars], parsing and transforming it into a **polars DataFrame**.

=== "`example.py`"

    ```py hl_lines="8-10"
    --8<-- "docs/usage/scripts/00_introduction.py:script-3"
    ```

=== "`result.to_proto()`"

    ```py
    --8<-- "docs/usage/scripts/00_introduction.py:result-proto"
    ```

=== "`result.to_dict()`"

    ```py
    --8<-- "docs/usage/scripts/00_introduction.py:result-dict"
    ```
=== "`result.to_polars()`"

    ```
    --8<-- "docs/usage/scripts/00_introduction.py:result-polars"
    ```

[Polars](https://docs.pola.rs/user-guide/getting-started/) is a dataframe library that implements the [Arrow](https://arrow.apache.org/docs/index.html) columnar data storage format. Under the hood, `to_polars` utilises a [strongly typed schema][fr24.types.cache.live_feed_schema] to reduce memory.

If you wish, you can [convert the `polars` DataFrame into `pandas`](https://docs.pola.rs/api/python/stable/reference/dataframe/api/polars.DataFrame.to_pandas.html).

!!! warning

    `to_polars` tries to convert a *list of records* in the `result` into a 2D table. Extra metadata that does not fit in a table (e.g. airline information in the [flight list service][fr24.service.FlightListService]) **will be discarded**.

## Writing to a file

You can write the data in JSON format:

=== "`example.py`"

    ```py hl_lines="2 9-10"
    --8<-- "docs/usage/scripts/00_introduction.py:script-4"
    ```

Alternatively, you can serialize the tabular form of the data in the [Parquet](https://parquet.apache.org/) data format.

`result` [implements the `write_table` method][fr24.service.SupportsWriteTable], which can be used to write to a file on the disk or a buffer, in the `parquet` or `csv` format:

=== "`example.py`"

    ```py hl_lines="2 9-10 12-14"
    --8<-- "docs/usage/scripts/00_introduction.py:script-5"
    ```

    1. If the `format` is not specified, it defaults to `parquet`.
    2. You must specify `format="csv"` - `write_table` does **not** infer from the file extension of the given path. 

## Caching

### Writing

You can also write the table into a [cache][fr24.cache.FR24Cache]:

=== "`example.py`"

    ```py hl_lines="4 6 12"
    --8<-- "docs/usage/scripts/00_introduction.py:script-6"
    ```

    1. More information about the location of the default cache can be found [here](./directories.md). You can also check the location by [running `fr24 dirs` in the shell](./cli.md).
    
    2. In this case, the file is written to `{cache_dir}/feed/{timestamp}.parquet`.

Files will be organised in the cache, with the structure shown [here](./examples.md#overview):

It should resemble the following on Linux:

```
$ tree $HOME/.cache/fr24/feed
/home/user/.cache/fr24
├── feed
│   └── 1711911907.parquet
├── flight_list
│   ├── flight
│   │   └── CX8747.parquet
│   └── reg
│       └── B-HUJ.parquet
└── playback
    └── 2d81a27.parquet
```

These directories are created automatically when `FR24Cache` is initialised.

### Reading

`FR24Cache` resembles the `FR24` service class. You list all cached files under a collection with the `glob` method and lazily load the file with the `scan_table` method:

=== "`example.py`"

    ```py hl_lines="5 7 11"
    --8<-- "docs/usage/scripts/00_introduction.py:script-7"
    ```

=== "Output"

    ```
    --8<-- "docs/usage/scripts/00_introduction.py:output-7"
    --8<-- "docs/usage/scripts/00_introduction.py:result-polars"
    ```

## Notes

See the [examples gallery](./examples.md) to learn more.

Intersphinx for this project could be found [here](https://abc8747.github.io/fr24/objects.inv).
