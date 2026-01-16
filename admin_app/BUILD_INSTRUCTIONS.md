# Admin App Build Instructions

## Building with Environment Configuration

The API URL and other sensitive configuration are now passed at build time, not hardcoded in the source code.

### Development Build

```bash
flutter run --dart-define=API_BASE_URL=https://lionbot-backend-426202982674.me-west1.run.app/api/v1
```

### Release APK Build

```bash
flutter build apk --release \
  --dart-define=API_BASE_URL=https://lionbot-backend-426202982674.me-west1.run.app/api/v1 \
  --dart-define=DEBUG_MODE=false \
  --dart-define=POLLING_INTERVAL=15
```

### Release App Bundle (for Play Store)

```bash
flutter build appbundle --release \
  --dart-define=API_BASE_URL=https://lionbot-backend-426202982674.me-west1.run.app/api/v1 \
  --dart-define=DEBUG_MODE=false
```

## Available Configuration Options

| Variable | Description | Default |
|----------|-------------|---------|
| `API_BASE_URL` | Backend API URL | (required) |
| `DEBUG_MODE` | Enable debug logging | false |
| `POLLING_INTERVAL` | Notification polling interval (seconds) | 15 |
| `REQUEST_TIMEOUT` | HTTP request timeout (seconds) | 30 |
| `DEFAULT_PAGE_SIZE` | Items per page for pagination | 50 |
| `FCM_ORDERS_TOPIC` | FCM topic for order notifications | admin_orders |
| `NOTIFICATION_CHANNEL_ID` | Android notification channel ID | orders_channel |

## Creating a Build Script

Create a file `build.sh` (don't commit to git):

```bash
#!/bin/bash
flutter build apk --release \
  --dart-define=API_BASE_URL=https://your-api-url.com/api/v1 \
  --dart-define=DEBUG_MODE=false
```

Then run: `chmod +x build.sh && ./build.sh`
