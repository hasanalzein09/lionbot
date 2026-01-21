from fastapi import APIRouter
from app.api.v1.endpoints import (
    webhook, login, restaurants, menus, orders, branches, users, stats,
    settings, websocket, loyalty, driver_assignment, inventory, notifications,
    customers, cart, reviews, favorites, addresses, coupons, search, reorder,
    delivery, cancellation, scheduling, referrals, analytics, tips,
    notification_preferences, support, banners, customizations, health,
    live_tracking, working_hours, exports, payouts, audit, webhooks_external,
    notification_templates, faq, app_config, receipts, driver_earnings,
    dashboard_stats, feature_flags, public
)

api_router = APIRouter()

# Public API (No authentication required) - For liondelivery-saida.com website
api_router.include_router(public.router, prefix="/public", tags=["public"])

# Auth
api_router.include_router(login.router, tags=["login"])

# WhatsApp
api_router.include_router(webhook.router, tags=["whatsapp"])

# Core Resources
api_router.include_router(restaurants.router, prefix="/restaurants", tags=["restaurants"])
api_router.include_router(branches.router, prefix="/branches", tags=["branches"])
api_router.include_router(menus.router, prefix="/menus", tags=["menus"])
api_router.include_router(orders.router, prefix="/orders", tags=["orders"])

# Users & Drivers
api_router.include_router(users.router, prefix="/users", tags=["users"])

# Customer App - Core
api_router.include_router(customers.router, prefix="/customers", tags=["customers"])
api_router.include_router(cart.router, prefix="/cart", tags=["cart"])
api_router.include_router(reviews.router, prefix="/reviews", tags=["reviews"])
api_router.include_router(favorites.router, prefix="/favorites", tags=["favorites"])
api_router.include_router(addresses.router, prefix="/addresses", tags=["addresses"])

# Customer App - Premium Features
api_router.include_router(search.router, prefix="/search", tags=["search"])
api_router.include_router(coupons.router, prefix="/coupons", tags=["coupons"])
api_router.include_router(reorder.router, prefix="/reorder", tags=["reorder"])
api_router.include_router(delivery.router, prefix="/delivery", tags=["delivery"])
api_router.include_router(cancellation.router, prefix="/orders/cancel", tags=["cancellation"])

# Enterprise Features
api_router.include_router(scheduling.router, prefix="/scheduling", tags=["scheduling"])
api_router.include_router(referrals.router, prefix="/referrals", tags=["referrals"])
api_router.include_router(analytics.router, prefix="/analytics", tags=["analytics"])
api_router.include_router(tips.router, prefix="/tips", tags=["tips"])
api_router.include_router(notification_preferences.router, prefix="/notification-preferences", tags=["preferences"])
api_router.include_router(support.router, prefix="/support", tags=["support"])

# Home & Marketing
api_router.include_router(banners.router, prefix="/banners", tags=["banners"])

# Menu Customizations
api_router.include_router(customizations.router, prefix="/customizations", tags=["customizations"])

# Live Tracking
api_router.include_router(live_tracking.router, prefix="/tracking", tags=["tracking"])

# System Health
api_router.include_router(health.router, prefix="/health", tags=["health"])

# Restaurant Operations
api_router.include_router(working_hours.router, prefix="/working-hours", tags=["working-hours"])
api_router.include_router(payouts.router, prefix="/payouts", tags=["payouts"])

# Admin & Reports
api_router.include_router(exports.router, prefix="/exports", tags=["exports"])
api_router.include_router(audit.router, prefix="/audit", tags=["audit"])
api_router.include_router(webhooks_external.router, prefix="/webhooks", tags=["webhooks"])
api_router.include_router(notification_templates.router, prefix="/notification-templates", tags=["templates"])
api_router.include_router(dashboard_stats.router, prefix="/dashboard", tags=["dashboard"])

# App Configuration & Help
api_router.include_router(app_config.router, prefix="/app", tags=["app-config"])
api_router.include_router(faq.router, prefix="/faq", tags=["faq"])
api_router.include_router(receipts.router, prefix="/receipts", tags=["receipts"])
api_router.include_router(feature_flags.router, prefix="/features", tags=["features"])

# Driver APIs
api_router.include_router(driver_earnings.router, prefix="/driver/earnings", tags=["driver-earnings"])

# Statistics
api_router.include_router(stats.router, prefix="/stats", tags=["statistics"])

# System Settings
api_router.include_router(settings.router, prefix="/settings", tags=["settings"])

# WebSocket Real-time
api_router.include_router(websocket.router, tags=["websocket"])

# Loyalty Program
api_router.include_router(loyalty.router, prefix="/loyalty", tags=["loyalty"])

# Driver Assignment
api_router.include_router(driver_assignment.router, prefix="/drivers/assignment", tags=["driver-assignment"])

# Inventory Management
api_router.include_router(inventory.router, prefix="/inventory", tags=["inventory"])

# Push Notifications
api_router.include_router(notifications.router, prefix="/notifications", tags=["notifications"])
