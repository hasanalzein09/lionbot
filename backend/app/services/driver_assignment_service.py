from typing import List, Optional
from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timedelta
import math

from app.models.user import User
from app.models.order import Order, OrderStatus


class DriverAssignmentService:
    """
    Smart driver assignment service that automatically assigns 
    the best available driver based on multiple factors.
    """
    
    # Weights for scoring algorithm
    WEIGHT_DISTANCE = 0.4
    WEIGHT_RATING = 0.25
    WEIGHT_AVAILABILITY = 0.2
    WEIGHT_WORKLOAD = 0.15
    
    # Constants
    MAX_ASSIGNMENT_DISTANCE_KM = 10
    MAX_ACTIVE_ORDERS_PER_DRIVER = 3
    
    def __init__(self, db: AsyncSession):
        self.db = db

    async def find_best_driver(
        self, 
        pickup_lat: float, 
        pickup_lng: float,
        order_value: float = 0,
        priority: str = "normal"
    ) -> Optional[User]:
        """
        Find the best available driver for an order.
        
        Args:
            pickup_lat: Restaurant latitude
            pickup_lng: Restaurant longitude
            order_value: Order total (higher value = prioritize top drivers)
            priority: "normal", "high", "urgent"
        
        Returns:
            Best matched driver or None if no drivers available
        """
        # Get all active drivers
        active_drivers = await self._get_active_drivers()
        
        if not active_drivers:
            return None
        
        # Score each driver
        scored_drivers = []
        for driver in active_drivers:
            score = await self._calculate_driver_score(
                driver, 
                pickup_lat, 
                pickup_lng,
                order_value,
                priority
            )
            if score > 0:
                scored_drivers.append((driver, score))
        
        if not scored_drivers:
            return None
        
        # Sort by score (highest first) and return best match
        scored_drivers.sort(key=lambda x: x[1], reverse=True)
        return scored_drivers[0][0]

    async def _get_active_drivers(self) -> List[User]:
        """Get all online and available drivers."""
        result = await self.db.execute(
            select(User)
            .where(User.role == "driver")
            .where(User.is_active == True)
            .where(User.last_latitude != None)
            .where(User.last_longitude != None)
        )
        return result.scalars().all()

    async def _calculate_driver_score(
        self,
        driver: User,
        pickup_lat: float,
        pickup_lng: float,
        order_value: float,
        priority: str
    ) -> float:
        """Calculate assignment score for a driver (0-100)."""
        
        # 1. Distance Score (closer = better)
        distance = self._haversine_distance(
            driver.last_latitude, driver.last_longitude,
            pickup_lat, pickup_lng
        )
        
        if distance > self.MAX_ASSIGNMENT_DISTANCE_KM:
            return 0  # Too far, skip this driver
        
        distance_score = max(0, 100 - (distance / self.MAX_ASSIGNMENT_DISTANCE_KM * 100))
        
        # 2. Rating Score (if available)
        rating_score = (driver.average_rating or 4.0) * 20  # Convert 5-star to 100
        
        # 3. Availability Score (fewer active orders = better)
        active_orders = await self._get_driver_active_orders_count(driver.id)
        
        if active_orders >= self.MAX_ACTIVE_ORDERS_PER_DRIVER:
            return 0  # Driver is at capacity
        
        availability_score = 100 - (active_orders / self.MAX_ACTIVE_ORDERS_PER_DRIVER * 100)
        
        # 4. Workload Balance Score (fair distribution)
        today_deliveries = await self._get_driver_today_deliveries(driver.id)
        workload_score = max(0, 100 - (today_deliveries * 5))  # Penalty for high workload
        
        # Calculate weighted final score
        final_score = (
            distance_score * self.WEIGHT_DISTANCE +
            rating_score * self.WEIGHT_RATING +
            availability_score * self.WEIGHT_AVAILABILITY +
            workload_score * self.WEIGHT_WORKLOAD
        )
        
        # Bonus for priority orders
        if priority == "urgent":
            # Prefer experienced drivers for urgent orders
            final_score *= 1.2
        elif priority == "high" and order_value > 100:
            # Prefer top-rated drivers for high-value orders
            final_score *= 1.1
        
        return final_score

    async def _get_driver_active_orders_count(self, driver_id: int) -> int:
        """Get count of driver's currently active orders."""
        result = await self.db.execute(
            select(func.count(Order.id))
            .where(Order.driver_id == driver_id)
            .where(Order.status.in_([
                OrderStatus.ACCEPTED,
                OrderStatus.PREPARING,
                OrderStatus.READY,
                OrderStatus.OUT_FOR_DELIVERY
            ]))
        )
        return result.scalar() or 0

    async def _get_driver_today_deliveries(self, driver_id: int) -> int:
        """Get count of driver's deliveries today."""
        today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        result = await self.db.execute(
            select(func.count(Order.id))
            .where(Order.driver_id == driver_id)
            .where(Order.status == OrderStatus.DELIVERED)
            .where(Order.created_at >= today_start)
        )
        return result.scalar() or 0

    @staticmethod
    def _haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Calculate the great circle distance between two points in km."""
        R = 6371  # Earth's radius in kilometers
        
        lat1_rad = math.radians(lat1)
        lat2_rad = math.radians(lat2)
        delta_lat = math.radians(lat2 - lat1)
        delta_lon = math.radians(lon2 - lon1)
        
        a = (math.sin(delta_lat / 2) ** 2 +
             math.cos(lat1_rad) * math.cos(lat2_rad) *
             math.sin(delta_lon / 2) ** 2)
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        
        return R * c

    async def auto_assign_order(self, order_id: int) -> Optional[User]:
        """
        Automatically assign a driver to an order.
        Updates the order with the assigned driver.
        """
        # Get order details
        result = await self.db.execute(
            select(Order).where(Order.id == order_id)
        )
        order = result.scalars().first()
        
        if not order or order.driver_id:
            return None  # Order not found or already assigned
        
        # Get restaurant location (assuming order has restaurant relationship)
        pickup_lat = order.restaurant.latitude if order.restaurant else 0
        pickup_lng = order.restaurant.longitude if order.restaurant else 0
        
        # Find best driver
        driver = await self.find_best_driver(
            pickup_lat=pickup_lat,
            pickup_lng=pickup_lng,
            order_value=float(order.total_amount),
            priority="high" if order.total_amount > 100 else "normal"
        )
        
        if driver:
            order.driver_id = driver.id
            order.status = OrderStatus.OUT_FOR_DELIVERY
            await self.db.commit()
            
            # TODO: Send notification to driver
            
        return driver
