# Authentication

By default, the client is not authenticated. You can check the status using the [CLI](./cli.md):

=== "Shell"

    ```sh
    fr24 auth show
    ```

=== "Output"

    ```
    warning: not authenticated
    help: provide your credentials in environment variables, either:
    - `fr24_username` and `fr24_password`, or
    - `fr24_subscription_key` and `fr24_token`
    help: alternatively, create a template configuration file at
    `/home/user/.config/fr24/fr24.conf` with the command `fr24 auth create`.
    ```

You should be authenticated if you would like to access more history or use the data for commercial purposes.

Set the following environment variables:

- `fr24_username` and `fr24_password`: (not recommended[^1]); OR
- `fr24_subscription_key` and `fr24_token`[^2];

## Config File

Alternatively, you can also create a configuration file in the [config directory](./directories.md).

An example of it can be found at [`fr24.example.conf`](https://github.com/abc8747/fr24/blob/master/fr24.example.conf), and can be generated with the command:

=== "Shell"

    ```sh
    fr24 auth create
    ```

=== "Output"

    ```
    success: created template configuration file at /home/user/.config/fr24/fr24.conf
    ```

Examples:

=== "username + password"

    ```ini
    [global]
    username=example13@example.com
    password=example13
    ```

=== "subscription_key + token"

    ```ini
    [global]
    subscription_key=dQw4w9WgXcQdQw4w9WgXcQdQw4w9WgXcQdQw4w9WgXcQ
    token=eyq2IlMJ5ip3ElLJ5aMKWmqT9fo3MyrJ91n25iq3EbMKW1oTImLJ5xp29xo2x=
    ```

[^1]: When the [FR24 class][fr24.FR24]' context is entered, a request is automatically made to retrieve the OAuth tokens
[^2]: `fr24_token` should be a JWT with the `exp` claim in a month, while `fr24_subscription_key` should be the shorter one. `fr24_token` is optional but live feed will fail without it. Be sure to update the JWT in time.
