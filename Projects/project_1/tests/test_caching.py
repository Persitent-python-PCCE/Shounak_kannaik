
import pytest
from unittest.mock import MagicMock
from service.event_service import EventService
from service.venue_service import VenueService
from service.payment_service import PaymentService
from models.event import Event
from models.venue import Venue
from config.cache import cache


def test_event_service_caching_and_invalidation(app):
    with app.app_context():
        cache.clear()
        mock_dao = MagicMock()
        mock_dao.get_all_events.return_value = ["event_1", "event_2"]
        mock_dao.create_event.return_value = MagicMock(id=1)

        service = EventService(mock_dao)


        result1 = service.get_all_events()
        assert result1 == ["event_1", "event_2"]
        assert mock_dao.get_all_events.call_count == 1


        result2 = service.get_all_events()
        assert result2 == ["event_1", "event_2"]
        assert mock_dao.get_all_events.call_count == 1


        service.create_event({"name": "New Concert", "event_type_id": 1})
        assert mock_dao.create_event.call_count == 1


        mock_dao.get_all_events.return_value = ["event_1", "event_2", "event_3"]
        result3 = service.get_all_events()
        assert result3 == ["event_1", "event_2", "event_3"]
        assert mock_dao.get_all_events.call_count == 2


def test_event_service_delete_invalidation(app):
    with app.app_context():
        cache.clear()
        mock_dao = MagicMock()
        fake_event = MagicMock()
        mock_dao.get_by_id.return_value = fake_event
        mock_dao.get_all_events.return_value = ["event_1"]

        service = EventService(mock_dao)


        assert service.get_all_events() == ["event_1"]
        assert mock_dao.get_all_events.call_count == 1


        assert service.get_all_events() == ["event_1"]
        assert mock_dao.get_all_events.call_count == 1


        service.delete_event(1)
        assert mock_dao.delete_event.call_count == 1


        mock_dao.get_all_events.return_value = []
        assert service.get_all_events() == []
        assert mock_dao.get_all_events.call_count == 2


def test_venue_service_caching_and_invalidation(app):
    with app.app_context():
        cache.clear()
        mock_dao = MagicMock()
        mock_dao.get_all_venues.return_value = ["venue_1"]
        mock_dao.create_venue.return_value = MagicMock(id=1)

        service = VenueService(mock_dao)


        res1 = service.get_all_venues()
        assert res1 == ["venue_1"]
        assert mock_dao.get_all_venues.call_count == 1


        res2 = service.get_all_venues()
        assert res2 == ["venue_1"]
        assert mock_dao.get_all_venues.call_count == 1


        service.create_venue({"name": "Grand Hall", "capacity": 500})
        assert mock_dao.create_venue.call_count == 1


        mock_dao.get_all_venues.return_value = ["venue_1", "venue_2"]
        res3 = service.get_all_venues()
        assert res3 == ["venue_1", "venue_2"]
        assert mock_dao.get_all_venues.call_count == 2


def test_payment_service_caching(app):
    with app.app_context():
        cache.clear()
        mock_dao = MagicMock()
        mock_dao.get_all_payment_modes.return_value = ["CARD", "UPI"]
        mock_dao.get_all_payment_statuses.return_value = ["SUCCESS", "FAILED"]

        service = PaymentService(mock_dao)


        modes1 = service.get_all_payment_modes()
        assert modes1 == ["CARD", "UPI"]
        assert mock_dao.get_all_payment_modes.call_count == 1


        modes2 = service.get_all_payment_modes()
        assert modes2 == ["CARD", "UPI"]
        assert mock_dao.get_all_payment_modes.call_count == 1


        st1 = service.get_all_payment_statuses()
        assert st1 == ["SUCCESS", "FAILED"]
        assert mock_dao.get_all_payment_statuses.call_count == 1

        st2 = service.get_all_payment_statuses()
        assert st2 == ["SUCCESS", "FAILED"]
        assert mock_dao.get_all_payment_statuses.call_count == 1
