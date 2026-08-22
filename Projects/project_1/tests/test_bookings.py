from datetime import datetime, timedelta, timezone
from decimal import Decimal
from config.database import db
from models.booking import Booking, BookingItem, BookingStatus
from models.payment import PaymentMode, PaymentStatus
from models.event import Event, EventType
from models.venue import Venue, Section, Seat
from models.schedule import EventSchedule


def setup_booking_fixtures(app):
    """Helper to setup test venue, section, seats, event, schedule, and statuses."""
    with app.app_context():
        # 1. Statuses
        reserved_status = BookingStatus(status_name="reserved")
        cancelled_status = BookingStatus(status_name="cancelled")
        pending_payment = PaymentStatus(status_name="pending")
        completed_payment = PaymentStatus(status_name="completed")
        refunded_payment = PaymentStatus(status_name="refunded")
        payment_mode = PaymentMode(mode_name="Credit Card", description="Credit Card Payment")
        db.session.add_all([
            reserved_status,
            cancelled_status,
            pending_payment,
            completed_payment,
            refunded_payment,
            payment_mode
        ])

        # 2. Venue, Section, Seats
        venue = Venue(
            name="Test Arena",
            address="123 Test St",
            city="Testville",
            state="TS",
            country="India",
            capacity=100
        )
        db.session.add(venue)
        db.session.flush()

        section = Section(venue_id=venue.id, name="VIP", description="VIP section", price=Decimal("250.00"))
        db.session.add(section)
        db.session.flush()

        seat1 = Seat(section_id=section.id, row="A", number="1", seat_type="VIP")
        seat2 = Seat(section_id=section.id, row="A", number="2", seat_type="VIP")
        db.session.add_all([seat1, seat2])

        # 3. Event & Schedule
        event_type = EventType(type_name="Concert")
        db.session.add(event_type)
        db.session.flush()

        event = Event(name="Rock Fest", event_type_id=event_type.id)
        db.session.add(event)
        db.session.flush()

        schedule = EventSchedule(
            event_id=event.id,
            venue_id=venue.id,
            start_datetime=datetime.now(timezone.utc) + timedelta(days=1),
            end_datetime=datetime.now(timezone.utc) + timedelta(days=1, hours=2),
            status="Scheduled"
        )
        db.session.add(schedule)
        db.session.commit()

        return {
            "schedule_id": schedule.id,
            "seat_ids": [seat1.id, seat2.id],
            "payment_mode_id": payment_mode.id,
            "event_id": event.id,
            "venue_id": venue.id,
            "cancelled_status_id": cancelled_status.id,
            "refunded_payment_id": refunded_payment.id,
        }


def test_get_bookings(client, customer_headers):
    """Test getting bookings list for authenticated user."""
    response = client.get("/bookings/", headers=customer_headers)
    assert response.status_code == 200
    assert isinstance(response.get_json(), list)


def test_get_bookings_unauthenticated(client):
    """Test getting bookings without auth fails with 401."""
    response = client.get("/bookings/")
    assert response.status_code == 401


def test_create_booking_success(app, client, customer_headers, customer_user):
    """Test creating a booking successfully."""
    fixtures = setup_booking_fixtures(app)
    
    payload = {
        "user_id": customer_user.id,
        "schedule_id": fixtures["schedule_id"],
        "seat_ids": fixtures["seat_ids"],
        "payment_mode_id": fixtures["payment_mode_id"]
    }
    response = client.post("/bookings/", json=payload, headers=customer_headers)
    assert response.status_code == 201
    
    data = response.get_json()
    assert "booking" in data
    assert data["booking"]["user_id"] == customer_user.id
    assert data["booking"]["total_amount"] == 500.0  # 2 seats * 250.00


def test_create_booking_conflict_active_reservation(app, client, customer_headers, customer_user):
    """Test creating a booking for seats already reserved within 5 minutes fails with 409."""
    fixtures = setup_booking_fixtures(app)
    
    payload = {
        "user_id": customer_user.id,
        "schedule_id": fixtures["schedule_id"],
        "seat_ids": fixtures["seat_ids"],
        "payment_mode_id": fixtures["payment_mode_id"]
    }
    # First booking succeeds
    res1 = client.post("/bookings/", json=payload, headers=customer_headers)
    assert res1.status_code == 201
    
    # Second booking for the same seats fails with 409
    res2 = client.post("/bookings/", json=payload, headers=customer_headers)
    assert res2.status_code == 409
    assert "already" in res2.get_json()["error"].lower()


def test_create_booking_lazy_expiry_success(app, client, customer_headers, customer_user):
    """Test that a pending booking older than 5 minutes allows new bookings (lazy expiry)."""
    fixtures = setup_booking_fixtures(app)
    
    payload = {
        "user_id": customer_user.id,
        "schedule_id": fixtures["schedule_id"],
        "seat_ids": fixtures["seat_ids"],
        "payment_mode_id": fixtures["payment_mode_id"]
    }
    # 1. First booking
    res1 = client.post("/bookings/", json=payload, headers=customer_headers)
    assert res1.status_code == 201
    booking_id = res1.get_json()["booking"]["id"]

    # 2. Manually backdate the created_at to 6 minutes ago
    with app.app_context():
        old_booking = db.session.get(Booking, booking_id)
        old_booking.created_at = datetime.now(timezone.utc) - timedelta(minutes=6)
        db.session.commit()

    # 3. New booking for same seats should now SUCCEED due to lazy expiry
    res2 = client.post("/bookings/", json=payload, headers=customer_headers)
    assert res2.status_code == 201


def test_cancel_booking_success(app, client, customer_headers, customer_user):
    """Test successfully cancelling a booking when event is > 1 hour away."""
    fixtures = setup_booking_fixtures(app)
    payload = {
        "user_id": customer_user.id,
        "schedule_id": fixtures["schedule_id"],
        "seat_ids": fixtures["seat_ids"],
        "payment_mode_id": fixtures["payment_mode_id"]
    }
    res = client.post("/bookings/", json=payload, headers=customer_headers)
    assert res.status_code == 201
    booking_id = res.get_json()["booking"]["id"]

    # Cancel the booking
    cancel_res = client.patch(f"/bookings/{booking_id}/cancel", headers=customer_headers)
    assert cancel_res.status_code == 200
    cancel_data = cancel_res.get_json()
    assert cancel_data["booking"]["booking_status_id"] == fixtures["cancelled_status_id"]
    assert cancel_data["booking"]["payment_status_id"] == fixtures["refunded_payment_id"]


def test_cancel_booking_within_one_hour_fails(app, client, customer_headers, customer_user):
    """Test that cancelling within 1 hour of event start fails with 400."""
    fixtures = setup_booking_fixtures(app)
    
    # Create a schedule starting in 30 minutes
    with app.app_context():
        soon_schedule = EventSchedule(
            event_id=fixtures["event_id"],
            venue_id=fixtures["venue_id"],
            start_datetime=datetime.now(timezone.utc) + timedelta(minutes=30),
            end_datetime=datetime.now(timezone.utc) + timedelta(hours=2),
            status="Scheduled"
        )
        db.session.add(soon_schedule)
        db.session.commit()
        soon_schedule_id = soon_schedule.id

    payload = {
        "user_id": customer_user.id,
        "schedule_id": soon_schedule_id,
        "seat_ids": fixtures["seat_ids"],
        "payment_mode_id": fixtures["payment_mode_id"]
    }
    res = client.post("/bookings/", json=payload, headers=customer_headers)
    assert res.status_code == 201
    booking_id = res.get_json()["booking"]["id"]

    # Attempt cancellation within 1 hour
    cancel_res = client.patch(f"/bookings/{booking_id}/cancel", headers=customer_headers)
    assert cancel_res.status_code == 400
    assert "1 hour" in cancel_res.get_json()["error"]


def test_cancel_booking_already_cancelled_fails(app, client, customer_headers, customer_user):
    """Test that cancelling an already-cancelled booking fails with 400."""
    fixtures = setup_booking_fixtures(app)
    payload = {
        "user_id": customer_user.id,
        "schedule_id": fixtures["schedule_id"],
        "seat_ids": fixtures["seat_ids"],
        "payment_mode_id": fixtures["payment_mode_id"]
    }
    res = client.post("/bookings/", json=payload, headers=customer_headers)
    assert res.status_code == 201
    booking_id = res.get_json()["booking"]["id"]

    # 1. First cancellation -> Success
    res1 = client.patch(f"/bookings/{booking_id}/cancel", headers=customer_headers)
    assert res1.status_code == 200

    # 2. Second cancellation -> 400
    res2 = client.patch(f"/bookings/{booking_id}/cancel", headers=customer_headers)
    assert res2.status_code == 400
    assert "already cancelled" in res2.get_json()["error"].lower()


def test_seats_available_after_cancellation(app, client, customer_headers, customer_user):
    """Test that cancelling a booking makes the seats immediately available for another user."""
    fixtures = setup_booking_fixtures(app)
    payload = {
        "user_id": customer_user.id,
        "schedule_id": fixtures["schedule_id"],
        "seat_ids": fixtures["seat_ids"],
        "payment_mode_id": fixtures["payment_mode_id"]
    }
    # 1. User books seats
    res = client.post("/bookings/", json=payload, headers=customer_headers)
    assert res.status_code == 201
    booking_id = res.get_json()["booking"]["id"]

    # 2. Immediate re-booking fails with 409
    res_conflict = client.post("/bookings/", json=payload, headers=customer_headers)
    assert res_conflict.status_code == 409

    # 3. User cancels the booking
    cancel_res = client.patch(f"/bookings/{booking_id}/cancel", headers=customer_headers)
    assert cancel_res.status_code == 200

    # 4. Now booking the same seats succeeds with 201!
    res_rebook = client.post("/bookings/", json=payload, headers=customer_headers)
    assert res_rebook.status_code == 201
