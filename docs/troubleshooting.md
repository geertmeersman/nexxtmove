# Troubleshooting

## Enable debug logging

Go to Settings → Devices & Services, click the triple dots for the Nexxtmove integration and click **Enable Debug Logging**.

![enable-debug-logging](https://raw.githubusercontent.com/geertmeersman/nexxtmove/main/images/screenshots/enable-debug-logging.gif)

## Disable debug logging and download logs

Once debug logging is enabled, reproduce the issue. Then disable debug logging — it will automatically prompt you to download the log file. Please provide this file when reporting an issue.

![disable-debug-logging](https://raw.githubusercontent.com/geertmeersman/nexxtmove/main/images/screenshots/disable-debug-logging.gif)

## Rate limiting

Nexxtmove applies a rate limiter: each client gets a burst of 15 requests, replenished at 1 per minute. When the rate limit is hit, the integration automatically backs off and reduces the update interval to 20 minutes. You will see a warning in the logs:

```
WARNING Rate limited, backing off
```

This is normal behaviour and will resolve automatically.
