
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


@admin_web.route("", methods=["GET"])
@admin_web.route("/", methods=["GET"])
@ui_role_required(Role.ADMIN)
def dashboard():
    return render_template("admin/dashboard.html")


@admin_web.route("/users", methods=["GET"])
@ui_role_required(Role.ADMIN)
def manage_users():
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
    try:
        user = admin_service.user_dao.get_by_id(user_id)
        username = user.username if user else f"ID {user_id}"
        admin_service.delete_user(user_id)
        flash(f"User '{username}' was deleted successfully.", "info")
    except ValueError as e:
        flash(str(e), "danger")
    return redirect(url_for("admin_web.manage_users"))


@admin_web.route("/events", methods=["GET"])
@ui_role_required(Role.ADMIN)
def manage_events():
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
    form = EventForm()
    event_types = event_service.get_all_event_types()
    form.event_type_id.choices = [(0, "-- Select Category --")] + [(et.id, et.type_name) for et in event_types]

    genres = event_service.get_all_genres()
    form.genre_ids.choices = [(g.id, g.genre_name) for g in genres]

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
    form = EventForm()
    event_types = event_service.get_all_event_types()
    form.event_type_id.choices = [(0, "-- Select Category --")] + [(et.id, et.type_name) for et in event_types]

    genres = event_service.get_all_genres()
    form.genre_ids.choices = [(g.id, g.genre_name) for g in genres]

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

        if form.genre_ids.data:
            event_service.set_genres_for_event(event.id, form.genre_ids.data)

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
    try:
        event = event_service.get_event_by_id(event_id)
    except ValueError as e:
        flash(str(e), "danger")
        return redirect(url_for("admin_web.manage_events"))

    event_types = event_service.get_all_event_types()
    venues = venue_service.get_all_venues()
    genres = event_service.get_all_genres()
    current_genre_ids = [g.id for g in event_service.get_genres_for_event(event_id)]

    form = EventForm(
        name=event.name,
        about=event.about,
        event_type_id=event.event_type_id or 0,
        age_rating=event.age_rating,
        genre_ids=current_genre_ids
    )
    form.event_type_id.choices = [(0, "-- Select Category --")] + [(et.id, et.type_name) for et in event_types]
    form.genre_ids.choices = [(g.id, g.genre_name) for g in genres]
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
    form = EventForm()
    event_types = event_service.get_all_event_types()
    form.event_type_id.choices = [(0, "-- Select Category --")] + [(et.id, et.type_name) for et in event_types]
    genres = event_service.get_all_genres()
    form.genre_ids.choices = [(g.id, g.genre_name) for g in genres]
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
        event_service.set_genres_for_event(event_id, form.genre_ids.data or [])
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
    try:
        event_service.delete_event(event_id)
        flash("Event deleted successfully.", "info")
    except ValueError as e:
        flash(str(e), "danger")
    return redirect(url_for("admin_web.manage_events"))


@admin_web.route("/venues", methods=["GET"])
@ui_role_required(Role.ADMIN)
def manage_venues():
    venues = venue_service.get_all_venues()
    return render_template("admin/venue_list.html", venues=venues)


@admin_web.route("/venues/new", methods=["GET"])
@ui_role_required(Role.ADMIN)
def create_venue_form():
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
    try:
        venue_service.delete_venue(venue_id)
        flash("Venue deleted successfully.", "info")
    except ValueError as e:
        flash(str(e), "danger")
    return redirect(url_for("admin_web.manage_venues"))


@admin_web.route("/schedules/new", methods=["GET"])
@ui_role_required(Role.ADMIN)
def create_schedule_form():
    form = ScheduleForm()
    events = event_service.get_all_events()
    venues = venue_service.get_all_venues()
    form.event_id.choices = [(e.id, e.name) for e in events]
    form.venue_id.choices = [(v.id, f"{v.name} ({v.city})") for v in venues]
    return render_template("admin/schedule_form.html", form=form)


@admin_web.route("/schedules", methods=["POST"])
@ui_role_required(Role.ADMIN)
def create_schedule_ui():
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


@admin_web.route("/bookings", methods=["GET"])
@ui_role_required(Role.ADMIN)
def manage_bookings():
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
