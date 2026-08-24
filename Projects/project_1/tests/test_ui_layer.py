
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
    with app.app_context():

        et = EventType(type_name="Concert", description="Live music concert")
        db.session.add(et)
        db.session.commit()


        ev = Event(name="Rock Fest 2026", about="Annual rock show", event_type_id=et.id, age_rating="UA 16+")
        db.session.add(ev)
        db.session.commit()


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


        pm1 = PaymentMode(mode_name="Credit Card", description="Visa/Mastercard")
        pm2 = PaymentMode(mode_name="UPI", description="Instant QR / VPA")
        db.session.add_all([pm1, pm2])


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
            "event_type_id": et.id,
            "venue_id": venue.id,
            "section_id": section.id,
            "seat1_id": seat1.id,
            "seat2_id": seat2.id,
            "schedule_id": schedule.id,
            "payment_mode_id": pm1.id
        }


def test_ui_public_events(client, ui_test_data):
    resp = client.get("/ui/events")
    assert resp.status_code == 200
    assert b"Rock Fest 2026" in resp.data

    ev_id = ui_test_data["event_id"]
    resp_detail = client.get(f"/ui/events/{ev_id}")
    assert resp_detail.status_code == 200
    assert b"City Arena" in resp_detail.data
    assert b"VIP" in resp_detail.data


def test_ui_register_and_login_flow(client):

    resp = client.get("/ui/register")
    assert resp.status_code == 200
    assert b"Customer Registration" in resp.data


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
    token = auth_service.generate_token(customer_user)
    client.set_cookie("access_token_cookie", token)

    schedule_id = ui_test_data["schedule_id"]
    seat_id = ui_test_data["seat1_id"]
    pm_id = ui_test_data["payment_mode_id"]


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


    resp_complete = client.post(
        f"/ui/payments/{booking_id}/complete",
        follow_redirects=True
    )
    assert resp_complete.status_code == 200
    assert b"Confirmed" in resp_complete.data
    assert b"Completed" in resp_complete.data


    resp_hist = client.get("/ui/bookings")
    assert resp_hist.status_code == 200
    assert b"Rock Fest 2026" in resp_hist.data


def test_ui_admin_access_control_and_crud(client, app, admin_user, customer_user, auth_service, ui_test_data):

    cust_token = auth_service.generate_token(customer_user)
    client.set_cookie("access_token_cookie", cust_token)
    resp_forbidden = client.get("/ui/admin")
    assert resp_forbidden.status_code == 403


    admin_token = auth_service.generate_token(admin_user)
    client.set_cookie("access_token_cookie", admin_token)
    resp_admin = client.get("/ui/admin")
    assert resp_admin.status_code == 200
    assert b"Admin Dashboard" in resp_admin.data


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
    dummy_pdf = (io.BytesIO(b"%PDF-1.4 dummy"), "id_doc.pdf")


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

    resp_admin_login = client.post(
        "/ui/login",
        data={"username": admin_user.username, "password": "AdminPass123!"},
        follow_redirects=False
    )
    assert resp_admin_login.status_code == 302
    assert "/ui/admin" in resp_admin_login.headers.get("Location", "")


    resp_cust_login = client.post(
        "/ui/login",
        data={"username": customer_user.username, "password": "Password123!"},
        follow_redirects=False
    )
    assert resp_cust_login.status_code == 302
    assert "/ui/events" in resp_cust_login.headers.get("Location", "")


def test_ui_admin_analytics_and_management_pages(client, admin_user, auth_service):
    admin_token = auth_service.generate_token(admin_user)
    client.set_cookie("access_token_cookie", admin_token)


    resp_dash = client.get("/ui/admin")
    assert resp_dash.status_code == 200
    assert b"User Management" in resp_dash.data
    assert b"Event Management" in resp_dash.data
    assert b"Venue Management" in resp_dash.data
    assert b"Booking Management" in resp_dash.data


    resp_users = client.get("/ui/admin/users")
    assert resp_users.status_code == 200
    assert b"User Management" in resp_users.data
    assert b"Total Users" in resp_users.data
    assert b"Customers" in resp_users.data
    assert b"Admins" in resp_users.data
    assert b"Edit" in resp_users.data


    resp_events = client.get("/ui/admin/events")
    assert resp_events.status_code == 200
    assert b"Events Management" in resp_events.data
    assert b"Total Events" in resp_events.data
    assert b"Current Trending Event" in resp_events.data
    assert b"Active Schedules" not in resp_events.data


    resp_venues = client.get("/ui/admin/venues")
    assert resp_venues.status_code == 200
    assert b"Venues Management" in resp_venues.data
    assert b"Total System Capacity" not in resp_venues.data
    assert b"Total Sections" not in resp_venues.data


    resp_bookings = client.get("/ui/admin/bookings")
    assert resp_bookings.status_code == 200
    assert b"System Bookings Oversight" in resp_bookings.data
    assert b"Total Bookings" in resp_bookings.data
    assert b"Total Revenue" in resp_bookings.data


def test_ui_admin_edit_user_flow(client, admin_user, customer_user, auth_service, app):
    admin_token = auth_service.generate_token(admin_user)
    client.set_cookie("access_token_cookie", admin_token)


    resp_get = client.get(f"/ui/admin/users/{customer_user.id}/edit")
    assert resp_get.status_code == 200
    assert b"Edit User Details" in resp_get.data
    assert b"Delete User" in resp_get.data
    assert customer_user.username.encode() in resp_get.data

    resp_post = client.post(
        f"/ui/admin/users/{customer_user.id}",
        data={
            "username": customer_user.username,
            "email": "updated_customer@example.com",
            "phone_no": "+919876543210",
            "role": "customer"
        },
        follow_redirects=True
    )
    assert resp_post.status_code == 200
    assert b"updated successfully" in resp_post.data
    assert b"updated_customer@example.com" in resp_post.data

    with app.app_context():
        from models.user import User
        from config.database import db
        updated_user = db.session.get(User, customer_user.id)
        assert updated_user.email == "updated_customer@example.com"
        assert updated_user.phone_no == "+919876543210"
        assert updated_user.is_active is False

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
    admin_token = auth_service.generate_token(admin_user)
    client.set_cookie("access_token_cookie", admin_token)

    resp = client.post(
        "/ui/admin/venues",
        data={
            "name": "Grand Symphony Hall",
            "address": "100 Music Lane",
            "city": "Bengaluru",
            "state": "Karnataka",
            "country": "India",
            "capacity": "",
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
        assert venue.capacity == 14
        assert len(venue.sections) == 2

        balcony = Section.query.filter_by(venue_id=venue.id, name="Balcony").first()
        assert balcony is not None
        assert len(balcony.seats) == 6
        seat_numbers = [s.number for s in balcony.seats]
        assert "BA1" in seat_numbers
        assert "BA2" in seat_numbers
        assert "BA3" in seat_numbers
        assert "BB1" in seat_numbers
        assert "BB2" in seat_numbers
        assert "BB3" in seat_numbers


def test_ui_event_creation_with_inline_schedule(client, admin_user, auth_service, ui_test_data, app):
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
    resp_events = client.get("/ui/events")
    assert resp_events.status_code == 200
    assert b'class="nav-link active fw-bold text-white" href="/ui/events"' in resp_events.data

    client.post(
        "/ui/login",
        data={"username": customer_user.username, "password": "Password123!"}
    )
    resp_bookings = client.get("/ui/bookings")
    assert resp_bookings.status_code == 200
    assert b'class="nav-link active fw-bold text-white" href="/ui/bookings"' in resp_bookings.data

    client.post(
        "/ui/login",
        data={"username": admin_user.username, "password": "AdminPass123!"}
    )
    resp_admin = client.get("/ui/admin")
    assert resp_admin.status_code == 200
    assert b'class="nav-link active fw-bold text-white"' in resp_admin.data
    assert b'Admin Dashboard</a>' in resp_admin.data


def test_ui_error_pages_html_rendering(client):
    resp_404 = client.get("/ui/non_existent_page")
    assert resp_404.status_code == 404
    assert b"Page Not Found" in resp_404.data
    assert b"404" in resp_404.data
    assert b"Return to Events" in resp_404.data

    resp_browser_404 = client.get("/random_browser_url", headers={"Accept": "text/html,application/xhtml+xml"})
    assert resp_browser_404.status_code == 404
    assert b"Page Not Found" in resp_browser_404.data


    resp_api_404 = client.get("/events/non_existent_api_call", headers={"Accept": "application/json"})
    assert resp_api_404.status_code == 404
    assert resp_api_404.is_json
    assert resp_api_404.get_json()["status"] == 404


def test_ui_events_server_side_pagination(client, app, ui_test_data):
    from dao.event_dao import EventDAO
    from models.event import Event

    with app.app_context():
        dao = EventDAO()

        for i in range(1, 13):
            dao.create_event(Event(
                name=f"Rock Fest Part {i}",
                event_type_id=ui_test_data["event_type_id"],
                age_rating="UA 16+"
            ))

    resp_default = client.get("/ui/events")
    assert resp_default.status_code == 200
    assert b"Browse Events" in resp_default.data
    assert b"Events per page:" in resp_default.data
    assert b'id="per_page_select"' in resp_default.data
    assert b"Showing" in resp_default.data
    assert b"Next &raquo;" in resp_default.data or b"Next" in resp_default.data

    resp_p1 = client.get("/ui/events?per_page=5&page=1")
    assert resp_p1.status_code == 200
    assert b"Rock Fest 2026" in resp_p1.data
    assert b"Rock Fest Part 1" in resp_p1.data
    assert b"Rock Fest Part 4" in resp_p1.data
    assert b"Showing <span class=\"fw-bold\">1</span> to <span class=\"fw-bold\">5</span>" in resp_p1.data

    resp_p2 = client.get("/ui/events?per_page=5&page=2")
    assert resp_p2.status_code == 200
    assert b"Rock Fest Part 5" in resp_p2.data
    assert b"Showing <span class=\"fw-bold\">6</span> to <span class=\"fw-bold\">10</span>" in resp_p2.data
    assert b"&laquo; Prev" in resp_p2.data

    resp_filtered = client.get("/ui/events?name=Rock+Fest+Part&per_page=5&page=1")
    assert resp_filtered.status_code == 200
    assert b"Rock Fest Part" in resp_filtered.data


def test_admin_create_and_edit_event_with_genres(client, app, admin_user, ui_test_data):
    from models.genre import Genre
    from models.event import Event
    from config.database import db

    with app.app_context():
        g1 = Genre(genre_name="Electronic", description="Electronic music")
        g2 = Genre(genre_name="Indie Pop", description="Indie pop music")
        db.session.add_all([g1, g2])
        db.session.commit()
        g1_id, g2_id = g1.id, g2.id

    client.post("/ui/login", data={"username": admin_user.username, "password": "AdminPass123!"})

    resp_get = client.get("/ui/admin/events/new")
    assert resp_get.status_code == 200
    assert b"Electronic" in resp_get.data
    assert b"Indie Pop" in resp_get.data

    resp_create = client.post(
        "/ui/admin/events",
        data={
            "name": "Coldplay Bangalore 2026",
            "about": "Coldplay live in Bangalore",
            "event_type_id": str(ui_test_data["event_type_id"]),
            "age_rating": "All Ages",
            "genre_ids": [str(g1_id), str(g2_id)],
            "venue_id": "0"
        },
        follow_redirects=True
    )
    assert resp_create.status_code == 200

    with app.app_context():
        ev = db.session.execute(db.select(Event).where(Event.name == "Coldplay Bangalore 2026")).scalar_one()
        assert len(ev.genres) == 2
        genre_names = {g.genre_name for g in ev.genres}
        assert "Electronic" in genre_names
        assert "Indie Pop" in genre_names
        ev_id = ev.id

    resp_edit = client.post(
        f"/ui/admin/events/{ev_id}",
        data={
            "name": "Coldplay Bangalore 2026 Updated",
            "about": "Coldplay live updated",
            "event_type_id": str(ui_test_data["event_type_id"]),
            "age_rating": "PG",
            "genre_ids": [str(g1_id)],
        },
        follow_redirects=True
    )
    assert resp_edit.status_code == 200

    with app.app_context():
        ev_updated = db.session.get(Event, ev_id)
        assert ev_updated.name == "Coldplay Bangalore 2026 Updated"
        assert len(ev_updated.genres) == 1
        assert ev_updated.genres[0].genre_name == "Electronic"
