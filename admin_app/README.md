# 📊 Lion Delivery - Admin App

Flutter app for platform administration.

## Features
- 📈 Real-time dashboard
- 📦 Order management
- 🏪 Restaurant management
- 🚗 Driver management
- 📦 Inventory control
- ⭐ Loyalty program
- ⚙️ System settings
- 🌐 Arabic/English

## Setup

```bash
flutter pub get
flutter run
```

## Access
Only users with `admin` or `super_admin` role can login.

## Structure
```
lib/
├── main.dart
└── app/
    ├── core/
    ├── routes/
    └── modules/
        ├── splash/
        ├── auth/
        ├── home/
        ├── orders/
        ├── restaurants/
        ├── drivers/
        ├── inventory/
        ├── loyalty/
        ├── settings/
        └── stats/
```
