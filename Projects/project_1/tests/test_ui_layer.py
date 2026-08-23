"""
Unit and Integration tests for the Parallel UI Layer (/ui).
"""

import io
from datetime import datetime, timedelta, timezone
import pytest
from models.user import User
from models.venue import Venue, Section, Seat
from models.event import Event, EventType
from models.schedule import EventSchedule
from models.payment import PaymentMode, PaymentStatus
from models.booking import BookingStatus
from config.database import db


@pytest.fixture
def ui_test_data(app):
    """Seed test entities required for UI testing and return their IDs."""
    with app.app_context():
        # Event type
        et = EventType(type_name="Concert", description="Live music concert")
        db.session.add(et)
        db.session.commit()

        # Event
        ev = Event(name="Rock Fest 2026", about="Annual rock show", event_type_id=et.id, age_rating="UA 16+")
        db.session.add(ev)
        db.session.commit()

        # Venue, Section, Seat
        venue = Venue(name="City Arena", address="123 Park Street", city="Mumbai", state="Maharashtra", country="India", capacity=200)
        db.session.add(venue)
        db.session.commit()

        section = Section(venue_id=venue.id, name="VIP", price=150.00)
        db.session.add(section)
        db.session.commit()

        seat1 = Seat(section_id=section.id, row="A", number="1", seat_type="VIP")
        seat2 = Seat(section_id=section.id, row="A", number="2", seat_type="VIP")
        db.session.add_all([seat1, seat2])
        db.session.commit()

        # Schedule
        start_time = datetime.now(timezone.utc) + timedelta(days=5)
        end_time = start_time + timedelta(hours=3)
        schedule = EventSchedule(
            event_id=ev.id,
            venue_id=venue.id,
            start_datetime=start_time,
            end_datetime=end_time,
            status="Scheduled"
        )
        db.session.add(schedule)

        # Payment Modes
        pm1 = PaymentMode(mode_name="Credit Card", description="Visa/Mastercard")
        pm2 = PaymentMode(mode_name="UPI", description="Instant QR / VPA")
        db.session.add_all([pm1, pm2])

        # Booking / Payment Statuses
        bs_res = BookingStatus(status_name="reserved")
        bs_conf = BookingStatus(status_name="confirmed")
        bs_canc = BookingStatus(status_name="cancelled")
        ps_pend = PaymentStatus(status_name="pending")
        ps_comp = PaymentStatus(status_name="completed")
        ps_ref = PaymentStatus(status_name="refunded")
        db.session.add_all([bs_res, bs_conf, bs_canc, ps_pend, ps_comp, ps_ref])

        db.session.commit()

        return {
            "event_id": ev.id,
            "event_name": ev.name,
            "venue_id": venue.id,
            "section_id": section.id,
            "seat1_id": seat1.id,
            "seat2_id": seat2.id,
            "schedule_id": schedule.id,
            "payment_mode_id": pm1.id
        }


def test_ui_public_events(client, ui_test_data):
    """Test public event browsing at /ui/events and /ui/events/<id>."""
    resp = client.get("/ui/events")
    assert resp.status_code == 200
    assert b"Rock Fest 2026" in resp.data

    ev_id = ui_test_data["event_id"]
    resp_detail = client.get(f"/ui/events/{ev_id}")
    assert resp_detail.status_code == 200
    assert b"City Arena" in resp_detail.data
    assert b"VIP" in resp_detail.data


def test_ui_register_and_login_flow(client):
    """Test user registration with file upload and cookie-based login."""
    # 1. GET Registration page
    resp = client.get("/ui/register")
    assert resp.status_code == 200
    assert b"Customer Registration" in resp.data

    # 2. POST Registration with ID document
    dummy_pdf = (io.BytesIO(b"%PDF-1.4 dummy file content"), "id_card.pdf")
    resp_reg = client.post(
        "/ui/register",
        data={
            "username": "new_ui_user",
            "email": "ui_user@example.com",
            "password": "Password123!",
            "confirm_password": "Password123!",
            "phone_no": "9876543210",
            "doc_type": "Govt ID",
            "id_document": dummy_pdf
        },
        content_type="multipart/form-data",
        follow_redirects=True
    )
    assert resp_reg.status_code == 200
    assert b"Registration successful" in resp_reg.data

    # 3. POST Login
    resp_login = client.post(
        "/ui/login",
        data={
            "username": "new_ui_user",
            "password": "Password123!"
        },
        follow_redirects=False
    )
    assert resp_login.status_code == 302
    assert "access_token_cookie" in resp_login.headers.get("Set-Cookie", "")


def test_ui_booking_and_payment_qr_flow(client, app, customer_user, auth_service, ui_test_data):
    """Test creating booking, viewing QR code, completing payment, and checking history."""
    token = auth_service.generate_token(customer_user)
    client.set_cookie("access_token_cookie", token)

    schedule_id = ui_test_data["schedule_id"]
    seat_id = ui_test_data["seat1_id"]
    pm_id = ui_test_data["payment_mode_id"]

    # 1. Create booking
    resp_book = client.post(
        "/ui/bookings",
        data={
            "schedule_id": str(schedule_id),
            "seat_ids": [str(seat_id)],
            "payment_mode_id": str(pm_id)
        },
        follow_redirects=True
    )
    assert resp_book.status_code == 200
    assert b"Select Payment Method" in resp_book.data or b"Pay" in resp_book.data

    # 2. Get the created booking
    with app.app_context():
        from models.booking import Booking
        booking = Booking.query.filter_by(user_id=customer_user.id).first()
        assert booking is not None
        booking_id = booking.id

    resp_pay = client.post(
        "/ui/payments",
        data={
            "booking_id": str(booking_id),
            "payment_mode_id": str(pm_id)
        }
    )
    assert resp_pay.status_code == 200
    assert b"Scan QR to Complete Payment" in resp_pay.data
    assert b"data:image/png;base64," in resp_pay.data

    # 3. Simulate QR scan / complete payment
    resp_complete = client.post(
        f"/ui/payments/{booking_id}/complete",
        follow_redirects=True
    )
    assert resp_complete.status_code == 200
    assert b"Confirmed" in resp_complete.data
    assert b"Completed" in resp_complete.data

    # 4. View booking history
    resp_hist = client.get("/ui/bookings")
    assert resp_hist.status_code == 200
    assert b"Rock Fest 2026" in resp_hist.data


def test_ui_admin_access_control_and_crud(client, app, admin_user, customer_user, auth_service, ui_test_data):
    """Test RBAC protection and admin management for venues and events."""
    # Customer forbidden from admin
    cust_token = auth_service.generate_token(customer_user)
    client.set_cookie("access_token_cookie", cust_token)
    resp_forbidden = client.get("/ui/admin")
    assert resp_forbidden.status_code == 403

    # Admin access allowed
    admin_token = auth_service.generate_token(admin_user)
    client.set_cookie("access_token_cookie", admin_token)
    resp_admin = client.get("/ui/admin")
    assert resp_admin.status_code == 200
    assert b"Admin Dashboard" in resp_admin.data

    # Admin create venue
    resp_create_venue = client.post(
        "/ui/admin/venues",
        data={
            "name": "New Admin Arena",
            "address": "456 High St",
            "city": "Delhi",
            "state": "Delhi",
            "country": "India",
            "capacity": "1000"
        },
        follow_redirects=True
    )
    assert resp_create_venue.status_code == 200
    assert b"New Admin Arena" in resp_create_venue.data


def test_ui_password_validation_and_confirmation(client):
    """Test password complexity enforcement and confirm password matching."""
    dummy_pdf = (io.BytesIO(b"%PDF-1.4 dummy"), "id_doc.pdf")

    # 1. Weak password (missing uppercase and special char)
    resp_weak = client.post(
        "/ui/register",
        data={
            "username": "weak_user",
            "email": "weak@example.com",
            "password": "password123",
            "confirm_password": "password123",
            "id_document": dummy_pdf
        },
        content_type="multipart/form-data",
        follow_redirects=True
    )
    assert resp_weak.status_code == 200
    assert b"Password must contain at least 1 capital letter" in resp_weak.data

    # 2. Mismatched confirm password
    dummy_pdf2 = (io.BytesIO(b"%PDF-1.4 dummy"), "id_doc.pdf")
    resp_mismatch = client.post(
        "/ui/register",
        data={
            "username": "mismatch_user",
            "email": "mismatch@example.com",
            "password": "Password123!",
            "confirm_password": "DifferentPassword123!",
            "id_document": dummy_pdf2
        },
        content_type="multipart/form-data",
        follow_redirects=True
    )
    assert resp_mismatch.status_code == 200
    assert b"Passwords must match" in resp_mismatch.data


def test_ui_phone_number_validation(client, admin_user, customer_user, auth_service):
    """Test non-numeric phone number rejection in registration and admin edit forms."""
    # 1. Registration form with non-numeric phone
    dummy_pdf = (io.BytesIO(b"%PDF-1.4 dummy"), "id_doc.pdf")
    resp_reg = client.post(
        "/ui/register",
        data={
            "username": "bad_phone_user",
            "email": "badphone_ui@example.com",
            "password": "Password123!",
            "confirm_password": "Password123!",
            "phone_no": "invalid_phone_text",
            "id_document": dummy_pdf
        },
        content_type="multipart/form-data",
        follow_redirects=True
    )
    assert resp_reg.status_code == 200
    assert b"Please enter a valid numeric phone number" in resp_reg.data

    # 2. Admin edit form with non-numeric phone
    admin_token = auth_service.generate_token(admin_user)
    client.set_cookie("access_token_cookie", admin_token)

    resp_edit = client.post(
        f"/ui/admin/users/{customer_user.id}",
        data={
            "username": customer_user.username,
            "email": customer_user.email,
            "phone_no": "invalid_edit_phone",
            "role": "customer"
        },
        follow_redirects=True
    )
    assert resp_edit.status_code == 200
    assert b"Please enter a valid numeric phone number" in resp_edit.data


def test_ui_admin_login_redirect_and_dashboard_cards(client, admin_user, customer_user):
    """Test admin redirect to dashboard vs customer redirect, and 4 dashboard cards."""
    # 1. Admin login redirects to admin dashboard
    resp_admin_login = client.post(
        "/ui/login",
        data={"username": admin_user.username, "password": "AdminPass123!"},
        follow_redirects=False
    )
    assert resp_admin_login.status_code == 302
    assert "/ui/admin" in resp_admin_login.headers.get("Location", "")

    # 2. Customer login redirects to events page
    resp_cust_login = client.post(
        "/ui/login",
        data={"username": customer_user.username, "password": "Password123!"},
        follow_redirects=False
    )
    assert resp_cust_login.status_code == 302
    assert "/ui/events" in resp_cust_login.headers.get("Location", "")


def test_ui_admin_analytics_and_management_pages(client, admin_user, auth_service):
    """Test all 4 admin management pages render analytics metrics correctly."""
    admin_token = auth_service.generate_token(admin_user)
    client.set_cookie("access_token_cookie", admin_token)

    # 1. Dashboard contains 4 cards
    resp_dash = client.get("/ui/admin")
    assert resp_dash.status_code == 200
    assert b"User Management" in resp_dash.data
    assert b"Event Management" in resp_dash.data
    assert b"Venue Management" in resp_dash.data
    assert b"Booking Management" in resp_dash.data

    # 2. User Management page + Analytics + Edit Action Link
    resp_users = client.get("/ui/admin/users")
    assert resp_users.status_code == 200
    assert b"User Management" in resp_users.data
    assert b"Total Users" in resp_users.data
    assert b"Customers" in resp_users.data
    assert b"Admins" in resp_users.data
    assert b"Edit" in resp_users.data

    # 3. Event Management page + Analytics (only 2 queries: total events, trending event)
    resp_events = client.get("/ui/admin/events")
    assert resp_events.status_code == 200
    assert b"Events Management" in resp_events.data
    assert b"Total Events" in resp_events.data
    assert b"Current Trending Event" in resp_events.data
    assert b"Active Schedules" not in resp_events.data

    # 4. Venue Management page (analytics removed)
    resp_venues = client.get("/ui/admin/venues")
    assert resp_venues.status_code == 200
    assert b"Venues Management" in resp_venues.data
    assert b"Total System Capacity" not in resp_venues.data
    assert b"Total Sections" not in resp_venues.data

    # 5. Booking Management page + Analytics
    resp_bookings = client.get("/ui/admin/bookings")
    assert resp_bookings.status_code == 200
    assert b"System Bookings Oversight" in resp_bookings.data
    assert b"Total Bookings" in resp_bookings.data
    assert b"Total Revenue" in resp_bookings.data


def test_ui_admin_edit_user_flow(client, admin_user, customer_user, auth_service, app):
    """Test admin editing user details, toggling active status, and deleting user."""
    admin_token = auth_service.generate_token(admin_user)
    client.set_cookie("access_token_cookie", admin_token)

    # 1. Access edit user form
    resp_get = client.get(f"/ui/admin/users/{customer_user.id}/edit")
    assert resp_get.status_code == 200
    assert b"Edit User Details" in resp_get.data
    assert b"Delete User" in resp_get.data
    assert customer_user.username.encode() in resp_get.data

    # 2. Submit user update with active status turned OFF (is_active omitted / unchecked)
    resp_post = client.post(
        f"/ui/admin/users/{customer_user.id}",
        data={
            "username": customer_user.username,
            "email": "updated_customer@example.com",
            "phone_no": "+919876543210",
            "role": "customer"
            # is_active checkbox not sent when unchecked in browser
        },
        follow_redirects=True
    )
    assert resp_post.status_code == 200
    assert b"updated successfully" in resp_post.data
    assert b"updated_customer@example.com" in resp_post.data

    # 3. Verify in database that is_active is now False
    with app.app_context():
        from models.user import User
        from config.database import db
        updated_user = db.session.get(User, customer_user.id)
        assert updated_user.email == "updated_customer@example.com"
        assert updated_user.phone_no == "+919876543210"
        assert updated_user.is_active is False

    # 4. Test deleting user
    resp_del = client.post(
        f"/ui/admin/users/{customer_user.id}/delete",
        follow_redirects=True
    )
    assert resp_del.status_code == 200
    assert b"deleted successfully" in resp_del.data

    with app.app_context():
        deleted_user = db.session.get(User, customer_user.id)
        assert deleted_user is None


def test_ui_venue_dynamic_sections_and_seat_generation(client, admin_user, auth_service, app):
    """Test venue creation with dynamic sections and backend row (A, B) and seat (A1, A2) generation."""
    admin_token = auth_service.generate_token(admin_user)
    client.set_cookie("access_token_cookie", admin_token)

    # POST venue creation with 2 sections (Balcony: 2 rows x 3 seats, Orchestra: 2 rows x 4 seats)
    resp = client.post(
        "/ui/admin/venues",
        data={
            "name": "Grand Symphony Hall",
            "address": "100 Music Lane",
            "city": "Bengaluru",
            "state": "Karnataka",
            "country": "India",
            "capacity": "",  # Auto-calculated
            "section_name[]": ["Balcony", "Orchestra"],
            "section_price[]": ["150.00", "250.00"],
            "row_count[]": ["2", "2"],
            "seats_per_row[]": ["3", "4"]
        },
        follow_redirects=True
    )
    assert resp.status_code == 200
    assert b"Grand Symphony Hall" in resp.data
    assert b"Balcony (6 seats)" in resp.data
    assert b"Orchestra (8 seats)" in resp.data

    with app.app_context():
        from models.venue import Venue, Section, Seat
        venue = Venue.query.filter_by(name="Grand Symphony Hall").first()
        assert venue is not None
        assert venue.capacity == 14  # (2*3) + (2*4) = 6 + 8 = 14 seats
        assert len(venue.sections) == 2

        balcony = Section.query.filter_by(venue_id=venue.id, name="Balcony").first()
        assert balcony is not None
        assert len(balcony.seats) == 6
        seat_numbers = [s.number for s in balcony.seats]
        assert "A1" in seat_numbers
        assert "A2" in seat_numbers
        assert "A3" in seat_numbers
        assert "B1" in seat_numbers
        assert "B2" in seat_numbers
        assert "B3" in seat_numbers


def test_ui_event_creation_with_inline_schedule(client, admin_user, auth_service, ui_test_data, app):
    """Test creating an event with inline venue and schedule creation."""
    admin_token = auth_service.generate_token(admin_user)
    client.set_cookie("access_token_cookie", admin_token)

    venue_id = ui_test_data["venue_id"]

    resp = client.post(
        "/ui/admin/events",
        data={
            "name": "Live Rock Concert 2026",
            "about": "A massive rock concert featuring top bands.",
            "event_type_id": 1,
            "age_rating": "UA 16+",
            "venue_id": venue_id,
            "start_datetime": "2026-11-20T19:00",
            "end_datetime": "2026-11-20T22:00"
        },
        follow_redirects=True
    )
    assert resp.status_code == 200
    assert b"Live Rock Concert 2026" in resp.data

    with app.app_context():
        from models.event import Event
        from models.schedule import EventSchedule
        ev = Event.query.filter_by(name="Live Rock Concert 2026").first()
        assert ev is not None
        sched = EventSchedule.query.filter_by(event_id=ev.id, venue_id=venue_id).first()
        assert sched is not None
        assert sched.start_datetime.isoformat() == "2026-11-20T19:00:00"


def test_ui_navbar_active_highlighting(client, admin_user, customer_user):
    """Test that the navbar highlights the active navigation menu item with bold text."""
    # 1. Public browsing -> Browse Events is active and bold
    resp_events = client.get("/ui/events")
    assert resp_events.status_code == 200
    assert b'class="nav-link active fw-bold text-white" href="/ui/events"' in resp_events.data

    # 2. Customer user on My Bookings -> My Bookings is active and bold
    client.post(
        "/ui/login",
        data={"username": customer_user.username, "password": "Password123!"}
    )
    resp_bookings = client.get("/ui/bookings")
    assert resp_bookings.status_code == 200
    assert b'class="nav-link active fw-bold text-white" href="/ui/bookings"' in resp_bookings.data

    # 3. Admin user on Admin Dashboard -> Admin Dashboard is active and bold
    client.post(
        "/ui/login",
        data={"username": admin_user.username, "password": "AdminPass123!"}
    )
    resp_admin = client.get("/ui/admin")
    assert resp_admin.status_code == 200
    assert b'class="nav-link active fw-bold text-white"' in resp_admin.data
    assert b'Admin Dashboard</a>' in resp_admin.data


def test_ui_error_pages_html_rendering(client):
    """Test that UI/browser requests receive rendered HTML error pages (404, 403, 500)."""
    # 1. UI 404 page renders templates/404.html
    resp_404 = client.get("/ui/non_existent_page")
    assert resp_404.status_code == 404
    assert b"Page Not Found" in resp_404.data
    assert b"404" in resp_404.data
    assert b"Return to Events" in resp_404.data

    # 2. Browser request to non-existent route with text/html Accept header
    resp_browser_404 = client.get("/random_browser_url", headers={"Accept": "text/html,application/xhtml+xml"})
    assert resp_browser_404.status_code == 404
    assert b"Page Not Found" in resp_browser_404.data

    # 3. API route non-existent returns JSON 404
    resp_api_404 = client.get("/events/non_existent_api_call", headers={"Accept": "application/json"})
    assert resp_api_404.status_code == 404
    assert resp_api_404.is_json
    assert resp_api_404.get_json()["status"] == 404

