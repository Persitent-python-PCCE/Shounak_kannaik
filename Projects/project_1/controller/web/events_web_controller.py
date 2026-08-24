
from flask import Blueprint, render_template, request, flash, redirect, url_for
from service.event_service import EventService
from service.schedule_service import ScheduleService
from service.booking_service import BookingService
from service.payment_service import PaymentService
from dao.event_dao import EventDAO
from dao.schedule_dao import ScheduleDAO
from dao.booking_dao import BookingDAO
from dao.payment_dao import PaymentDAO

events_web = Blueprint("events_web", __name__)
event_service = EventService(EventDAO())
schedule_service = ScheduleService(ScheduleDAO())
booking_service = BookingService(BookingDAO())
payment_service = PaymentService(PaymentDAO())


@events_web.route("/events", methods=["GET"])
def list_events():
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 10, type=int)
    if per_page not in [5, 10, 15, 20]:
        per_page = 10
    if page < 1:
        page = 1

    filters = {k: v for k, v in request.args.items() if v and k not in ("page", "per_page")}
    try:
        if filters:
            pagination = event_service.filter_events(filters, page=page, per_page=per_page)
        else:
            pagination = event_service.get_all_events_paginated(page=page, per_page=per_page)
    except ValueError as e:
        flash(str(e), "warning")
        pagination = event_service.get_all_events_paginated(page=page, per_page=per_page)

    event_types = event_service.get_all_event_types()
    genres = event_service.get_all_genres()

    return render_template(
        "events/list.html",
        pagination=pagination,
        events=pagination.items,
        event_types=event_types,
        genres=genres,
        per_page=per_page
    )


@events_web.route("/events/<int:event_id>", methods=["GET"])
def event_detail(event_id):
    try:
        event = event_service.get_event_by_id(event_id)
    except ValueError as e:
        flash(str(e), "danger")
        return redirect(url_for("events_web.list_events"))

    schedules = schedule_service.get_schedules_for_event(event_id)
    genres = event_service.get_genres_for_event(event_id)
    payment_modes = payment_service.get_all_payment_modes()

    selected_schedule = None
    seat_sections = []
    booked_seat_ids = set()

    schedule_id_param = request.args.get("schedule_id")
    if schedule_id_param:
        try:
            selected_schedule = schedule_service.get_schedule_by_id(int(schedule_id_param))
            booked_seat_ids = booking_service.get_booked_seat_ids(selected_schedule.id)
            if selected_schedule.venue:
                seat_sections = selected_schedule.venue.sections
        except ValueError as e:
            flash(str(e), "warning")
    elif schedules:

        selected_schedule = schedules[0]
        booked_seat_ids = booking_service.get_booked_seat_ids(selected_schedule.id)
        if selected_schedule.venue:
            seat_sections = selected_schedule.venue.sections

    return render_template(
        "events/detail.html",
        event=event,
        schedules=schedules,
        selected_schedule=selected_schedule,
        seat_sections=seat_sections,
        booked_seat_ids=booked_seat_ids,
        genres=genres,
        payment_modes=payment_modes
    )
