"""
Admin Web UI Controller.

Provides administrative views and CRUD management for events, venues,
event schedules, users, and system-wide booking oversight with analytical metrics.
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash
from service.admin_service import AdminService
from service.event_service import EventService
from service.venue_service import VenueService
from service.schedule_service import ScheduleService
from service.booking_service import BookingService
from dao.user_dao import UserDAO
from dao.event_dao import EventDAO
from dao.venue_dao import VenueDAO
from dao.schedule_dao import ScheduleDAO
from dao.booking_dao import BookingDAO
from common.ui_decorators import ui_role_required
from common.roles import Role
from common.file_utils import validate_file, save_uploaded_file
from forms.auth_forms import UserEditForm
from forms.event_forms import EventForm
from forms.venue_forms import VenueForm
from forms.schedule_forms import ScheduleForm

admin_web = Blueprint("admin_web", __name__)
admin_service = AdminService(UserDAO())
event_service = EventService(EventDAO())
venue_service = VenueService(VenueDAO())
schedule_service = ScheduleService(ScheduleDAO())
booking_service = BookingService(BookingDAO())


# =========================================================================
# Admin Dashboard
# =========================================================================

@admin_web.route("", methods=["GET"])
@admin_web.route("/", methods=["GET"])
@ui_role_required(Role.ADMIN)
def dashboard():
    """Display admin main navigation dashboard with 4 cards."""
    return render_template("admin/dashboard.html")


# =========================================================================
# User Management
# =========================================================================

@admin_web.route("/users", methods=["GET"])
@ui_role_required(Role.ADMIN)
def manage_users():
    """List all registered users with analytical metrics."""
    users = admin_service.get_all_users()

    analytics = {
        "total_users": len(users),
        "admin_count": sum(1 for u in users if u.role and str(u.role).lower() == "admin"),
        "customer_count": sum(1 for u in users if not u.role or str(u.role).lower() == "customer"),
        "active_count": sum(1 for u in users if getattr(u, "is_active", True) is not False)
    }

    return render_template("admin/user_list.html", users=users, analytics=analytics)


@admin_web.route("/users/<int:user_id>/edit", methods=["GET"])
@ui_role_required(Role.ADMIN)
def edit_user_form(user_id):
    """Display form to edit user details."""
    user = admin_service.user_dao.get_by_id(user_id)
    if not user:
        flash("User not found.", "danger")
        return redirect(url_for("admin_web.manage_users"))

    form = UserEditForm(
        username=user.username,
        email=user.email,
        phone_no=user.phone_no or "",
        role=user.role or "customer",
        is_active=bool(user.is_active)
    )

    return render_template(
        "admin/user_form.html",
        form=form,
        user=user,
        action_url=url_for("admin_web.process_edit_user", user_id=user.id)
    )


@admin_web.route("/users/<int:user_id>", methods=["POST"])
@ui_role_required(Role.ADMIN)
def process_edit_user(user_id):
    """Update user details."""
    user = admin_service.user_dao.get_by_id(user_id)
    if not user:
        flash("User not found.", "danger")
        return redirect(url_for("admin_web.manage_users"))

    form = UserEditForm()
    if not form.validate_on_submit():
        return render_template(
            "admin/user_form.html",
            form=form,
            user=user,
            action_url=url_for("admin_web.process_edit_user", user_id=user.id)
        )

    try:
        data = {
            "user_id": user_id,
            "username": form.username.data.strip(),
            "email": form.email.data.strip(),
            "phone_no": form.phone_no.data.strip() if form.phone_no.data else None,
            "role": form.role.data,
            "is_active": form.is_active.data
        }
        admin_service.update_user(data)
        flash(f"User '{form.username.data.strip()}' updated successfully!", "success")
        return redirect(url_for("admin_web.manage_users"))
    except ValueError as e:
        flash(str(e), "danger")
        return render_template(
            "admin/user_form.html",
            form=form,
            user=user,
            action_url=url_for("admin_web.process_edit_user", user_id=user.id)
        )


@admin_web.route("/users/<int:user_id>/delete", methods=["POST"])
@ui_role_required(Role.ADMIN)
def delete_user_ui(user_id):
    """Delete a user account and associated resources."""
    try:
        user = admin_service.user_dao.get_by_id(user_id)
        username = user.username if user else f"ID {user_id}"
        admin_service.delete_user(user_id)
        flash(f"User '{username}' was deleted successfully.", "info")
    except ValueError as e:
        flash(str(e), "danger")
    return redirect(url_for("admin_web.manage_users"))


# =========================================================================
# Events Management (with inline schedule creation)
# =========================================================================

@admin_web.route("/events", methods=["GET"])
@ui_role_required(Role.ADMIN)
def manage_events():
    """List all events for management with 2 analytical metrics."""
    events = event_service.get_all_events()
    trending_event = event_service.get_trending_event_this_week()
    trending_event_name = trending_event.name if trending_event else "No trending event this week"

    analytics = {
        "total_events": len(events),
        "trending_event": trending_event_name
    }

    return render_template("admin/event_list.html", events=events, analytics=analytics)


@admin_web.route("/events/new", methods=["GET"])
@ui_role_required(Role.ADMIN)
def create_event_form():
    """Display event creation form with optional schedule fields."""
    form = EventForm()
    event_types = event_service.get_all_event_types()
    form.event_type_id.choices = [(0, "-- Select Category --")] + [(et.id, et.type_name) for et in event_types]

    venues = venue_service.get_all_venues()
    form.venue_id.choices = [(0, "-- No Schedule (Just Create Event) --")] + [(v.id, f"{v.name} ({v.city})") for v in venues]

    return render_template(
        "admin/event_form.html",
        form=form,
        is_edit=False,
        action_url=url_for("admin_web.process_create_event"),
        current_poster=None
    )


@admin_web.route("/events", methods=["POST"])
@ui_role_required(Role.ADMIN)
def process_create_event():
    """Create a new event and optional schedule."""
    form = EventForm()
    event_types = event_service.get_all_event_types()
    form.event_type_id.choices = [(0, "-- Select Category --")] + [(et.id, et.type_name) for et in event_types]

    venues = venue_service.get_all_venues()
    form.venue_id.choices = [(0, "-- No Schedule (Just Create Event) --")] + [(v.id, f"{v.name} ({v.city})") for v in venues]

    if not form.validate_on_submit():
        return render_template(
            "admin/event_form.html",
            form=form,
            is_edit=False,
            action_url=url_for("admin_web.process_create_event"),
            current_poster=None
        )

    poster_file = form.poster_image.data
    poster_path = None

    try:
        if poster_file and getattr(poster_file, "filename", None):
            validate_file(
                poster_file,
                allowed_extensions={"png", "jpg", "jpeg", "webp"},
                max_size_bytes=5 * 1024 * 1024,
                required=False
            )
            poster_path = save_uploaded_file(poster_file, "static/uploads/posters", prefix="event")

        event_data = {
            "name": form.name.data.strip(),
            "about": form.about.data.strip() if form.about.data else None,
            "event_type_id": form.event_type_id.data if form.event_type_id.data and form.event_type_id.data > 0 else None,
            "age_rating": form.age_rating.data,
            "poster_image_path": poster_path
        }
        event = event_service.create_event(event_data)

        # Check if schedule details were also provided
        if form.venue_id.data and form.venue_id.data > 0 and form.start_datetime.data and form.end_datetime.data:
            schedule_data = {
                "event_id": event.id,
                "venue_id": form.venue_id.data,
                "start_datetime": form.start_datetime.data.isoformat(),
                "end_datetime": form.end_datetime.data.isoformat(),
                "status": "Scheduled"
            }
            schedule_service.create_schedule(schedule_data)
            flash(f"Event '{event.name}' and schedule created successfully!", "success")
        else:
            flash(f"Event '{event.name}' created successfully!", "success")

        return redirect(url_for("admin_web.manage_events"))

    except ValueError as e:
        flash(str(e), "danger")
        return render_template(
            "admin/event_form.html",
            form=form,
            is_edit=False,
            action_url=url_for("admin_web.process_create_event"),
            current_poster=None
        )


@admin_web.route("/events/<int:event_id>/edit", methods=["GET"])
@ui_role_required(Role.ADMIN)
def edit_event_form(event_id):
    """Display event edit form prefilled with current event details."""
    try:
        event = event_service.get_event_by_id(event_id)
    except ValueError as e:
        flash(str(e), "danger")
        return redirect(url_for("admin_web.manage_events"))

    event_types = event_service.get_all_event_types()
    venues = venue_service.get_all_venues()

    form = EventForm(
        name=event.name,
        about=event.about,
        event_type_id=event.event_type_id or 0,
        age_rating=event.age_rating
    )
    form.event_type_id.choices = [(0, "-- Select Category --")] + [(et.id, et.type_name) for et in event_types]
    form.venue_id.choices = [(0, "-- None --")] + [(v.id, f"{v.name} ({v.city})") for v in venues]

    return render_template(
        "admin/event_form.html",
        form=form,
        is_edit=True,
        action_url=url_for("admin_web.process_edit_event", event_id=event.id),
        current_poster=event.poster_image_path
    )


@admin_web.route("/events/<int:event_id>", methods=["POST"])
@ui_role_required(Role.ADMIN)
def process_edit_event(event_id):
    """Update event details."""
    form = EventForm()
    event_types = event_service.get_all_event_types()
    form.event_type_id.choices = [(0, "-- Select Category --")] + [(et.id, et.type_name) for et in event_types]
    venues = venue_service.get_all_venues()
    form.venue_id.choices = [(0, "-- None --")] + [(v.id, f"{v.name} ({v.city})") for v in venues]

    if not form.validate_on_submit():
        return render_template(
            "admin/event_form.html",
            form=form,
            is_edit=True,
            action_url=url_for("admin_web.process_edit_event", event_id=event_id),
            current_poster=None
        )

    poster_file = form.poster_image.data

    try:
        event_data = {
            "event_id": event_id,
            "name": form.name.data.strip(),
            "about": form.about.data.strip() if form.about.data else None,
            "event_type_id": form.event_type_id.data if form.event_type_id.data and form.event_type_id.data > 0 else None,
            "age_rating": form.age_rating.data
        }

        if poster_file and getattr(poster_file, "filename", None):
            validate_file(
                poster_file,
                allowed_extensions={"png", "jpg", "jpeg", "webp"},
                max_size_bytes=5 * 1024 * 1024,
                required=False
            )
            poster_path = save_uploaded_file(poster_file, "static/uploads/posters", prefix="event")
            event_data["poster_image_path"] = poster_path

        event_service.update_event(event_data)
        flash("Event updated successfully!", "success")
        return redirect(url_for("admin_web.manage_events"))

    except ValueError as e:
        flash(str(e), "danger")
        return render_template(
            "admin/event_form.html",
            form=form,
            is_edit=True,
            action_url=url_for("admin_web.process_edit_event", event_id=event_id),
            current_poster=None
        )


@admin_web.route("/events/<int:event_id>/delete", methods=["POST"])
@ui_role_required(Role.ADMIN)
def delete_event_ui(event_id):
    """Delete an event."""
    try:
        event_service.delete_event(event_id)
        flash("Event deleted successfully.", "info")
    except ValueError as e:
        flash(str(e), "danger")
    return redirect(url_for("admin_web.manage_events"))


# =========================================================================
# Venues Management (with dynamic sections and auto seat generation)
# =========================================================================

@admin_web.route("/venues", methods=["GET"])
@ui_role_required(Role.ADMIN)
def manage_venues():
    """List all venues with section details."""
    venues = venue_service.get_all_venues()
    return render_template("admin/venue_list.html", venues=venues)


@admin_web.route("/venues/new", methods=["GET"])
@ui_role_required(Role.ADMIN)
def create_venue_form():
    """Display venue creation form."""
    form = VenueForm()
    return render_template(
        "admin/venue_form.html",
        form=form,
        is_edit=False,
        action_url=url_for("admin_web.process_create_venue")
    )


@admin_web.route("/venues", methods=["POST"])
@ui_role_required(Role.ADMIN)
def process_create_venue():
    """Create a new venue and automatically generate sections and seats."""
    form = VenueForm()
    if not form.validate_on_submit():
        return render_template(
            "admin/venue_form.html",
            form=form,
            is_edit=False,
            action_url=url_for("admin_web.process_create_venue")
        )

    try:
        venue_data = {
            "name": form.name.data.strip(),
            "address": form.address.data.strip(),
            "city": form.city.data.strip(),
            "state": form.state.data.strip(),
            "country": form.country.data.strip(),
            "capacity": int(form.capacity.data) if form.capacity.data else 0
        }

        # Parse dynamically submitted section arrays
        sec_names = request.form.getlist("section_name[]")
        sec_prices = request.form.getlist("section_price[]")
        row_counts = request.form.getlist("row_count[]")
        seats_per_rows = request.form.getlist("seats_per_row[]")

        sections_data = []
        for i in range(len(sec_names)):
            if sec_names[i].strip():
                try:
                    r_cnt = int(row_counts[i]) if i < len(row_counts) else 0
                    s_cnt = int(seats_per_rows[i]) if i < len(seats_per_rows) else 0
                    price_val = float(sec_prices[i]) if i < len(sec_prices) and sec_prices[i] else 0.0
                    sections_data.append({
                        "name": sec_names[i].strip(),
                        "price": price_val,
                        "row_count": r_cnt,
                        "seats_per_row": s_cnt
                    })
                except (ValueError, TypeError):
                    continue

        venue = venue_service.create_venue_with_layout(venue_data, sections_data)
        flash(f"Venue '{venue.name}' and seating layout created successfully!", "success")
        return redirect(url_for("admin_web.manage_venues"))

    except ValueError as e:
        flash(str(e), "danger")
        return render_template(
            "admin/venue_form.html",
            form=form,
            is_edit=False,
            action_url=url_for("admin_web.process_create_venue")
        )


@admin_web.route("/venues/<int:venue_id>/edit", methods=["GET"])
@ui_role_required(Role.ADMIN)
def edit_venue_form(venue_id):
    """Display venue edit form."""
    venue = venue_service.get_by_id(venue_id)
    if not venue:
        flash("Venue not found.", "danger")
        return redirect(url_for("admin_web.manage_venues"))

    form = VenueForm(
        name=venue.name,
        address=venue.address,
        city=venue.city,
        state=venue.state,
        country=venue.country,
        capacity=venue.capacity
    )
    return render_template(
        "admin/venue_form.html",
        form=form,
        is_edit=True,
        action_url=url_for("admin_web.process_edit_venue", venue_id=venue.id)
    )


@admin_web.route("/venues/<int:venue_id>", methods=["POST"])
@ui_role_required(Role.ADMIN)
def process_edit_venue(venue_id):
    """Update venue details."""
    form = VenueForm()
    if not form.validate_on_submit():
        return render_template(
            "admin/venue_form.html",
            form=form,
            is_edit=True,
            action_url=url_for("admin_web.process_edit_venue", venue_id=venue_id)
        )

    try:
        venue_data = {
            "venue_id": venue_id,
            "name": form.name.data.strip(),
            "address": form.address.data.strip(),
            "city": form.city.data.strip(),
            "state": form.state.data.strip(),
            "country": form.country.data.strip(),
            "capacity": int(form.capacity.data) if form.capacity.data else 0
        }
        venue_service.update_venue(venue_data)
        flash("Venue updated successfully!", "success")
        return redirect(url_for("admin_web.manage_venues"))
    except ValueError as e:
        flash(str(e), "danger")
        return render_template(
            "admin/venue_form.html",
            form=form,
            is_edit=True,
            action_url=url_for("admin_web.process_edit_venue", venue_id=venue_id)
        )


@admin_web.route("/venues/<int:venue_id>/delete", methods=["POST"])
@ui_role_required(Role.ADMIN)
def delete_venue_ui(venue_id):
    """Delete a venue."""
    try:
        venue_service.delete_venue(venue_id)
        flash("Venue deleted successfully.", "info")
    except ValueError as e:
        flash(str(e), "danger")
    return redirect(url_for("admin_web.manage_venues"))


# =========================================================================
# Schedules Management
# =========================================================================

@admin_web.route("/schedules/new", methods=["GET"])
@ui_role_required(Role.ADMIN)
def create_schedule_form():
    """Display schedule creation form."""
    form = ScheduleForm()
    events = event_service.get_all_events()
    venues = venue_service.get_all_venues()
    form.event_id.choices = [(e.id, e.name) for e in events]
    form.venue_id.choices = [(v.id, f"{v.name} ({v.city})") for v in venues]
    return render_template("admin/schedule_form.html", form=form)


@admin_web.route("/schedules", methods=["POST"])
@ui_role_required(Role.ADMIN)
def create_schedule_ui():
    """Create a new event schedule."""
    form = ScheduleForm()
    events = event_service.get_all_events()
    venues = venue_service.get_all_venues()
    form.event_id.choices = [(e.id, e.name) for e in events]
    form.venue_id.choices = [(v.id, f"{v.name} ({v.city})") for v in venues]

    if not form.validate_on_submit():
        return render_template("admin/schedule_form.html", form=form)

    try:
        schedule_data = {
            "event_id": form.event_id.data,
            "venue_id": form.venue_id.data,
            "start_datetime": form.start_datetime.data.isoformat(),
            "end_datetime": form.end_datetime.data.isoformat(),
            "status": form.status.data
        }
        schedule_service.create_schedule(schedule_data)
        flash("Event schedule created successfully!", "success")
        return redirect(url_for("admin_web.dashboard"))
    except ValueError as e:
        flash(str(e), "danger")
        return render_template("admin/schedule_form.html", form=form)


# =========================================================================
# Bookings Oversight
# =========================================================================

@admin_web.route("/bookings", methods=["GET"])
@ui_role_required(Role.ADMIN)
def manage_bookings():
    """View all bookings system-wide with analytical metrics."""
    bookings = booking_service.get_all_bookings()

    total_revenue = sum(
        float(b.total_amount or 0)
        for b in bookings
        if b.payment_status and str(b.payment_status.status_name).lower() == "completed"
    )

    analytics = {
        "total_bookings": len(bookings),
        "total_revenue": total_revenue,
        "confirmed_count": sum(
            1 for b in bookings
            if b.booking_status and str(b.booking_status.status_name).lower() == "confirmed"
        ),
        "pending_count": sum(
            1 for b in bookings
            if b.booking_status and str(b.booking_status.status_name).lower() == "reserved"
        )
    }

    return render_template("admin/manage_bookings.html", bookings=bookings, analytics=analytics)

