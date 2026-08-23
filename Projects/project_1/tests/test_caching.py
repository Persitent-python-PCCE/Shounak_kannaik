"""
Unit and integration tests for service-level caching and invalidation.
"""

import pytest
from unittest.mock import MagicMock
from service.event_service import EventService
from service.venue_service import VenueService
from service.payment_service import PaymentService
from models.event import Event
from models.venue import Venue
from config.cache import cache


def test_event_service_caching_and_invalidation(app):
    """Test that EventService memoizes get_all_events and invalidates on mutations."""
    with app.app_context():
        cache.clear()
        mock_dao = MagicMock()
        mock_dao.get_all_events.return_value = ["event_1", "event_2"]
        mock_dao.create_event.return_value = MagicMock(id=1)

        service = EventService(mock_dao)

        # First call should hit the DAO
        result1 = service.get_all_events()
        assert result1 == ["event_1", "event_2"]
        assert mock_dao.get_all_events.call_count == 1

        # Second call should be served from cache without calling DAO again
        result2 = service.get_all_events()
        assert result2 == ["event_1", "event_2"]
        assert mock_dao.get_all_events.call_count == 1

        # Mutate: create an event
        service.create_event({"name": "New Concert", "event_type_id": 1})
        assert mock_dao.create_event.call_count == 1

        # Subsequent call should fetch fresh data from DAO because cache was invalidated
        mock_dao.get_all_events.return_value = ["event_1", "event_2", "event_3"]
        result3 = service.get_all_events()
        assert result3 == ["event_1", "event_2", "event_3"]
        assert mock_dao.get_all_events.call_count == 2


def test_event_service_delete_invalidation(app):
    """Test that deleting an event clears the cached events list."""
    with app.app_context():
        cache.clear()
        mock_dao = MagicMock()
        fake_event = MagicMock()
        mock_dao.get_by_id.return_value = fake_event
        mock_dao.get_all_events.return_value = ["event_1"]

        service = EventService(mock_dao)

        # Call get_all_events to cache it
        assert service.get_all_events() == ["event_1"]
        assert mock_dao.get_all_events.call_count == 1

        # Cached call
        assert service.get_all_events() == ["event_1"]
        assert mock_dao.get_all_events.call_count == 1

        # Delete event
        service.delete_event(1)
        assert mock_dao.delete_event.call_count == 1

        # Next call hits DAO again
        mock_dao.get_all_events.return_value = []
        assert service.get_all_events() == []
        assert mock_dao.get_all_events.call_count == 2


def test_venue_service_caching_and_invalidation(app):
    """Test that VenueService caches get_all_venues and clears on create/update/delete."""
    with app.app_context():
        cache.clear()
        mock_dao = MagicMock()
        mock_dao.get_all_venues.return_value = ["venue_1"]
        mock_dao.create_venue.return_value = MagicMock(id=1)

        service = VenueService(mock_dao)

        # Cache get_all_venues
        res1 = service.get_all_venues()
        assert res1 == ["venue_1"]
        assert mock_dao.get_all_venues.call_count == 1

        # Cached hit
        res2 = service.get_all_venues()
        assert res2 == ["venue_1"]
        assert mock_dao.get_all_venues.call_count == 1

        # Invalidate via create
        service.create_venue({"name": "Grand Hall", "capacity": 500})
        assert mock_dao.create_venue.call_count == 1

        # Cache miss after invalidation
        mock_dao.get_all_venues.return_value = ["venue_1", "venue_2"]
        res3 = service.get_all_venues()
        assert res3 == ["venue_1", "venue_2"]
        assert mock_dao.get_all_venues.call_count == 2


def test_payment_service_caching(app):
    """Test that PaymentService caches payment modes and statuses."""
    with app.app_context():
        cache.clear()
        mock_dao = MagicMock()
        mock_dao.get_all_payment_modes.return_value = ["CARD", "UPI"]
        mock_dao.get_all_payment_statuses.return_value = ["SUCCESS", "FAILED"]

        service = PaymentService(mock_dao)

        # First call
        modes1 = service.get_all_payment_modes()
        assert modes1 == ["CARD", "UPI"]
        assert mock_dao.get_all_payment_modes.call_count == 1

        # Second call (cached)
        modes2 = service.get_all_payment_modes()
        assert modes2 == ["CARD", "UPI"]
        assert mock_dao.get_all_payment_modes.call_count == 1

        # Statuses
        st1 = service.get_all_payment_statuses()
        assert st1 == ["SUCCESS", "FAILED"]
        assert mock_dao.get_all_payment_statuses.call_count == 1

        st2 = service.get_all_payment_statuses()
        assert st2 == ["SUCCESS", "FAILED"]
        assert mock_dao.get_all_payment_statuses.call_count == 1
