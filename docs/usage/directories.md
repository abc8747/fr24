Check the location of the config and cache directories with:

```sh
fr24 dirs
```

Here are possible outputs:

| OS      | Config File                                | Cache Directory                  |
| ------- | ------------------------------------------ | -------------------------------- |
| Linux   | `$HOME/.config/fr24/fr24.conf`             | `$HOME/.cache/fr24`              |
| macOS   | `$HOME/Library/Preferences/fr24.conf`      | `$HOME/Library/Caches/fr24`      |
| Windows | `%LOCALAPPDATA%\Acme\fr24\Cache\fr24.conf` | `%LOCALAPPDATA%\Acme\fr24\Cache` |

On Unix-based systems, you can override the configuration and cache directory with the environment variable `XDG_CACHE_HOME` and `XDG_CONFIG_HOME` respectively.
