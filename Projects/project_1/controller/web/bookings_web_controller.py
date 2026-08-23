"""
Bookings Web UI Controller.

Handles ticket reservation submission, booking history, booking details, and cancellations.
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, g
from service.booking_service import BookingService
from service.payment_service import PaymentService
from dao.booking_dao import BookingDAO
from dao.payment_dao import PaymentDAO
from common.ui_decorators import ui_login_required
from forms.payment_forms import PaymentForm

bookings_web = Blueprint("bookings_web", __name__)
booking_service = BookingService(BookingDAO(), PaymentDAO())
payment_service = PaymentService(PaymentDAO())


@bookings_web.route("/bookings", methods=["POST"])
@ui_login_required
def create_booking_ui():
    """Process seat reservation form submission."""
    user_id = g.current_user.get("user_id")
    schedule_id = request.form.get("schedule_id")
    raw_seat_ids = request.form.getlist("seat_ids")
    payment_mode_id = request.form.get("payment_mode_id")

    if not raw_seat_ids and request.form.get("seat_ids"):
        # Support comma-separated hidden field if used
        raw_seat_ids = [s.strip() for s in request.form.get("seat_ids").split(",") if s.strip()]

    if not schedule_id or not raw_seat_ids:
        flash("Please select a valid schedule and at least one seat.", "warning")
        return redirect(request.referrer or url_for("events_web.list_events"))

    try:
        seat_ids = [int(s) for s in raw_seat_ids]
        p_mode_id = int(payment_mode_id) if payment_mode_id else None

        booking = booking_service.create_booking(
            user_id=user_id,
            schedule_id=int(schedule_id),
            seat_ids=seat_ids,
            payment_mode_id=p_mode_id
        )

        flash("Seats temporarily reserved! Please proceed with payment to confirm your booking.", "success")
        return redirect(url_for("bookings_web.pay_booking_form", booking_id=booking.id))

    except ValueError as e:
        flash(str(e), "danger")
        return redirect(request.referrer or url_for("events_web.list_events"))
    except Exception as e:
        flash(f"Booking could not be completed: {str(e)}", "danger")
        return redirect(request.referrer or url_for("events_web.list_events"))


@bookings_web.route("/bookings", methods=["GET"])
@ui_login_required
def booking_history():
    """Display authenticated user's booking history."""
    user_id = g.current_user.get("user_id")
    bookings = booking_service.get_bookings_for_user(user_id)
    return render_template("bookings/history.html", bookings=bookings)


@bookings_web.route("/bookings/<int:booking_id>", methods=["GET"])
@ui_login_required
def booking_detail(booking_id):
    """Display individual booking confirmation and status."""
    try:
        booking = booking_service.get_booking_by_id(booking_id)
    except ValueError as e:
        flash(str(e), "danger")
        return redirect(url_for("bookings_web.booking_history"))

    user_id = g.current_user.get("user_id")
    user_role = g.current_user.get("role")
    if booking.user_id != user_id and user_role != "admin":
        return render_template("403.html"), 403

    return render_template("bookings/confirmation.html", booking=booking)


@bookings_web.route("/bookings/<int:booking_id>/cancel", methods=["POST"])
@ui_login_required
def cancel_booking_ui(booking_id):
    """Process booking cancellation enforcing the 1-hour cutoff."""
    user_id = g.current_user.get("user_id")
    user_role = g.current_user.get("role")

    try:
        booking_service.cancel_booking(booking_id=booking_id, user_id=user_id, role=user_role)
        flash("Booking cancelled successfully. Refund initiated.", "success")
    except ValueError as e:
        flash(str(e), "danger")
    except Exception as e:
        flash(f"Cancellation error: {str(e)}", "danger")

    return redirect(url_for("bookings_web.booking_history"))


@bookings_web.route("/bookings/<int:booking_id>/pay", methods=["GET"])
@ui_login_required
def pay_booking_form(booking_id):
    """Display payment mode selection form for a pending booking."""
    try:
        booking = booking_service.get_booking_by_id(booking_id)
    except ValueError as e:
        flash(str(e), "danger")
        return redirect(url_for("bookings_web.booking_history"))

    user_id = g.current_user.get("user_id")
    user_role = g.current_user.get("role")
    if booking.user_id != user_id and user_role != "admin":
        return render_template("403.html"), 403

    # Expiry / Status guard
    is_cancelled = booking.booking_status and booking.booking_status.status_name.lower() == "cancelled"
    is_expired = booking.payment_status and booking.payment_status.status_name.lower() == "expired"
    is_completed = booking.payment_status and booking.payment_status.status_name.lower() == "completed"

    if is_completed:
        flash("This booking is already paid and confirmed.", "info")
        return redirect(url_for("bookings_web.booking_detail", booking_id=booking.id))

    if is_cancelled or is_expired:
        flash("This booking reservation has expired (5-minute payment window elapsed). Please select your seats again.", "warning")
        return redirect(url_for("bookings_web.booking_history"))

    payment_modes = payment_service.get_all_payment_modes()
    form = PaymentForm(booking_id=booking.id)
    form.payment_mode_id.choices = [(pm.id, f"{pm.mode_name} ({pm.description or ''})") for pm in payment_modes]

    if booking.payment_mode_id:
        form.payment_mode_id.data = booking.payment_mode_id

    return render_template("bookings/pay.html", booking=booking, form=form)
