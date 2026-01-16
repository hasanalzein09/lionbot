# 🦁 Lion Delivery Platform

## Complete Food Delivery Ecosystem

A full-stack food delivery platform with 4 mobile apps, WhatsApp bot integration, and comprehensive backend.

---

## 📱 Mobile Apps

| App | Directory | Description |
|-----|-----------|-------------|
| 🛒 Customer | `/customer_app/` | Order food, track deliveries |
| 🚗 Driver | `/mobile/` | Accept orders, GPS tracking |
| 📊 Admin | `/admin_app/` | Manage entire platform |
| 🍽️ Restaurant | `/restaurant_app/` | Manage orders & menu |

---

## 🚀 Quick Start

### Backend
```bash
cd backend
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your credentials
uvicorn app.main:app --reload
```

### Mobile Apps
```bash
# Customer App
cd customer_app && flutter pub get && flutter run

# Driver App
cd mobile && flutter pub get && flutter run

# Admin App
cd admin_app && flutter pub get && flutter run

# Restaurant App
cd restaurant_app && flutter pub get && flutter run
```

### Frontend Dashboard
```bash
cd frontend
npm install
npm run dev
```

---

## 🔥 Features

### Customer App
- Browse restaurants & categories
- Add to cart (Redis-based)
- Checkout with Cash on Delivery
- Track orders in real-time
- Loyalty points & rewards
- Arabic/English support

### Driver App
- Real-time order notifications (FCM)
- GPS tracking
- Google Maps integration
- Order status management
- Earnings tracking

### Admin App
- Dashboard with live stats
- Order management
- Restaurant management
- Driver management
- Inventory control
- Loyalty program settings

### Restaurant App
- Audio alerts for new orders
- Order status updates
- Menu management
- Daily stats

---

## 🔧 Tech Stack

### Backend
- **Framework**: FastAPI (Python)
- **Database**: PostgreSQL (Cloud SQL)
- **Cache**: Redis
- **Deployment**: Google Cloud Run
- **Push**: Firebase Cloud Messaging

### Mobile
- **Framework**: Flutter 3.x
- **State**: Riverpod
- **Storage**: Hive, Secure Storage
- **Maps**: Google Maps
- **Real-time**: WebSocket, FCM

### Frontend
- **Framework**: Next.js 15
- **Styling**: TailwindCSS
- **Charts**: Recharts

---

## 📡 API Endpoints

### Authentication
- `POST /login/access-token` - Login
- `POST /customers/register` - Customer registration

### Customer
- `GET /customers/my-orders` - My orders
- `GET /customers/my-orders/{id}/track` - Track order

### Cart
- `GET /cart` - Get cart
- `POST /cart/items` - Add to cart
- `POST /cart/checkout` - Place order (COD)

### Restaurants
- `GET /restaurants` - List restaurants
- `GET /menus?restaurant_id=X` - Get menu

### Orders
- `GET /orders` - List orders
- `PATCH /orders/{id}` - Update status

### Notifications
- `POST /notifications/register-token` - Register FCM
- `POST /notifications/send` - Send notification

---

## 🌐 Languages
- English (en_US)
- Arabic (ar_SA)

---

## 📄 License
Private - All rights reserved

---

Built with ❤️ by Lion Delivery Team
