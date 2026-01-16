import pytest
from unittest.mock import AsyncMock, MagicMock
from datetime import datetime

from app.services.driver_assignment_service import DriverAssignmentService


class TestDriverAssignmentService:
    """Unit tests for the driver assignment service."""

    @pytest.fixture
    def mock_db(self):
        """Create a mock database session."""
        return AsyncMock()
    
    @pytest.fixture
    def service(self, mock_db):
        """Create service instance with mock db."""
        return DriverAssignmentService(mock_db)

    def test_haversine_distance_same_location(self, service):
        """Test distance calculation for same location."""
        distance = service._haversine_distance(
            33.8938, 35.5018,  # Beirut
            33.8938, 35.5018   # Beirut
        )
        assert distance == 0.0

    def test_haversine_distance_known_cities(self, service):
        """Test distance between Beirut and Tripoli (~85km)."""
        distance = service._haversine_distance(
            33.8938, 35.5018,  # Beirut
            34.4360, 35.8497   # Tripoli
        )
        # Should be approximately 85km
        assert 80 < distance < 90

    def test_haversine_distance_short(self, service):
        """Test short distance calculation."""
        # Two points ~1km apart in Beirut
        distance = service._haversine_distance(
            33.8938, 35.5018,
            33.8848, 35.5018
        )
        # Should be ~1km
        assert 0.5 < distance < 2.0

    @pytest.mark.asyncio
    async def test_calculate_driver_score_too_far(self, service, mock_db):
        """Test that drivers too far away get score of 0."""
        mock_driver = MagicMock()
        mock_driver.last_latitude = 34.4360  # Tripoli
        mock_driver.last_longitude = 35.8497
        mock_driver.average_rating = 4.5
        mock_driver.id = 1

        # Mock active orders count
        mock_result = MagicMock()
        mock_result.scalar.return_value = 0
        mock_db.execute = AsyncMock(return_value=mock_result)

        score = await service._calculate_driver_score(
            mock_driver,
            pickup_lat=33.8938,  # Beirut
            pickup_lng=35.5018,
            order_value=50,
            priority="normal"
        )
        
        # Driver is ~85km away, max is 10km, should be 0
        assert score == 0

    @pytest.mark.asyncio
    async def test_calculate_driver_score_close_driver(self, service, mock_db):
        """Test scoring for a nearby driver."""
        mock_driver = MagicMock()
        mock_driver.last_latitude = 33.8948  # Very close
        mock_driver.last_longitude = 35.5028
        mock_driver.average_rating = 5.0
        mock_driver.id = 1

        # Mock: No active orders, no deliveries today
        mock_result = MagicMock()
        mock_result.scalar.return_value = 0
        mock_db.execute = AsyncMock(return_value=mock_result)

        score = await service._calculate_driver_score(
            mock_driver,
            pickup_lat=33.8938,
            pickup_lng=35.5018,
            order_value=50,
            priority="normal"
        )
        
        # Should have high score
        assert score > 80

    @pytest.mark.asyncio
    async def test_calculate_driver_score_at_capacity(self, service, mock_db):
        """Test that drivers at max capacity get score of 0."""
        mock_driver = MagicMock()
        mock_driver.last_latitude = 33.8948
        mock_driver.last_longitude = 35.5028
        mock_driver.average_rating = 5.0
        mock_driver.id = 1

        # Mock: 3 active orders (at capacity)
        mock_result = MagicMock()
        mock_result.scalar.return_value = 3  # MAX_ACTIVE_ORDERS_PER_DRIVER
        mock_db.execute = AsyncMock(return_value=mock_result)

        score = await service._calculate_driver_score(
            mock_driver,
            pickup_lat=33.8938,
            pickup_lng=35.5018,
            order_value=50,
            priority="normal"
        )
        
        assert score == 0

    @pytest.mark.asyncio
    async def test_urgent_priority_bonus(self, service, mock_db):
        """Test that urgent orders get priority bonus."""
        mock_driver = MagicMock()
        mock_driver.last_latitude = 33.8948
        mock_driver.last_longitude = 35.5028
        mock_driver.average_rating = 4.0
        mock_driver.id = 1

        mock_result = MagicMock()
        mock_result.scalar.return_value = 0
        mock_db.execute = AsyncMock(return_value=mock_result)

        normal_score = await service._calculate_driver_score(
            mock_driver,
            pickup_lat=33.8938,
            pickup_lng=35.5018,
            order_value=50,
            priority="normal"
        )

        urgent_score = await service._calculate_driver_score(
            mock_driver,
            pickup_lat=33.8938,
            pickup_lng=35.5018,
            order_value=50,
            priority="urgent"
        )
        
        # Urgent should have 1.2x multiplier
        assert urgent_score == pytest.approx(normal_score * 1.2, rel=0.01)


class TestDriverAssignmentWeights:
    """Test the scoring weight configuration."""

    def test_weights_sum_to_one(self):
        """Verify that all weights sum to 1.0."""
        total = (
            DriverAssignmentService.WEIGHT_DISTANCE +
            DriverAssignmentService.WEIGHT_RATING +
            DriverAssignmentService.WEIGHT_AVAILABILITY +
            DriverAssignmentService.WEIGHT_WORKLOAD
        )
        assert total == pytest.approx(1.0, rel=0.01)

    def test_distance_is_highest_weight(self):
        """Distance should be the most important factor."""
        assert DriverAssignmentService.WEIGHT_DISTANCE >= DriverAssignmentService.WEIGHT_RATING
        assert DriverAssignmentService.WEIGHT_DISTANCE >= DriverAssignmentService.WEIGHT_AVAILABILITY
        assert DriverAssignmentService.WEIGHT_DISTANCE >= DriverAssignmentService.WEIGHT_WORKLOAD
