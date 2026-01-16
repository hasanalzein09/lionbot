# 🛒 Lion Delivery - Customer App

Flutter app for ordering food from restaurants.

## Features
- 🏪 Browse restaurants & categories
- 🍔 View menus & add to cart
- 💳 Checkout (Cash on Delivery)
- 📦 Track orders in real-time
- ⭐ Loyalty points & rewards
- 🌐 Arabic/English

## Setup

```bash
flutter pub get
flutter run
```

## API Configuration
Edit `lib/app/core/services/api_service.dart`:
```dart
static const String baseUrl = 'YOUR_BACKEND_URL/api/v1';
```

## Firebase Setup
1. Create Firebase project
2. Add iOS/Android apps
3. Download `google-services.json` (Android)
4. Download `GoogleService-Info.plist` (iOS)

## Structure
```
lib/
├── main.dart
└── app/
    ├── core/
    │   ├── theme/
    │   ├── services/
    │   └── localization/
    ├── routes/
    └── modules/
        ├── splash/
        ├── auth/
        ├── home/
        ├── restaurant/
        ├── cart/
        ├── checkout/
        ├── orders/
        ├── profile/
        └── search/
```
