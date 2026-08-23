"""
Payments Web UI Controller.

Handles payment initiation, dynamic QR code generation with python-qrcode,
and payment completion verification.
"""

import io
import base64
import qrcode
from flask import Blueprint, render_template, request, redirect, url_for, flash, g
from service.booking_service import BookingService
from service.payment_service import PaymentService
from dao.booking_dao import BookingDAO
from dao.payment_dao import PaymentDAO
from common.ui_decorators import ui_login_required
from forms.payment_forms import PaymentForm

payments_web = Blueprint("payments_web", __name__)
booking_service = BookingService(BookingDAO(), PaymentDAO())
payment_service = PaymentService(PaymentDAO())


def generate_qr_base64(data_string: str) -> str:
    """Generate an in-memory QR code image encoded as a base64 string."""
    qr = qrcode.QRCode(version=1, box_size=8, border=2)
    qr.add_data(data_string)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    return base64.b64encode(buffer.getvalue()).decode("utf-8")


@payments_web.route("/payments", methods=["POST"])
@ui_login_required
def process_payment_ui():
    """
    Process payment mode selection and display QR code for payment completion.
    """
    booking_id = request.form.get("booking_id")
    payment_mode_id = request.form.get("payment_mode_id")

    if not booking_id or not payment_mode_id:
        flash("Invalid payment selection parameters.", "danger")
        return redirect(url_for("bookings_web.booking_history"))

    try:
        booking = booking_service.get_booking_by_id(int(booking_id))
    except ValueError as e:
        flash(str(e), "danger")
        return redirect(url_for("bookings_web.booking_history"))

    user_id = g.current_user.get("user_id")
    user_role = g.current_user.get("role")
    if booking.user_id != user_id and user_role != "admin":
        return render_template("403.html"), 403

    # Update payment mode on the booking
    booking.payment_mode_id = int(payment_mode_id)
    BookingDAO().update_booking(booking)

    # Generate QR data pointing to the scan/completion endpoint
    payment_target_url = request.host_url.rstrip("/") + url_for(
        "payments_web.complete_payment_scan",
        booking_id=booking.id
    )
    qr_code_base64 = generate_qr_base64(payment_target_url)

    return render_template(
        "payments/qr_payment.html",
        booking=booking,
        qr_code_base64=qr_code_base64
    )


@payments_web.route("/payments/<int:booking_id>/qr", methods=["GET"])
@ui_login_required
def show_qr_page(booking_id):
    """Display the QR code payment screen for an existing pending booking."""
    try:
        booking = booking_service.get_booking_by_id(booking_id)
    except ValueError as e:
        flash(str(e), "danger")
        return redirect(url_for("bookings_web.booking_history"))

    user_id = g.current_user.get("user_id")
    user_role = g.current_user.get("role")
    if booking.user_id != user_id and user_role != "admin":
        return render_template("403.html"), 403

    payment_target_url = request.host_url.rstrip("/") + url_for(
        "payments_web.complete_payment_scan",
        booking_id=booking.id
    )
    qr_code_base64 = generate_qr_base64(payment_target_url)

    return render_template(
        "payments/qr_payment.html",
        booking=booking,
        qr_code_base64=qr_code_base64
    )


@payments_web.route("/payments/<int:booking_id>/complete", methods=["GET", "POST"])
def complete_payment_scan(booking_id):
    """
    Endpoint triggered upon QR scan (or user confirmation) to complete payment
    and confirm the booking transaction in the database.
    """
    try:
        booking = booking_service.confirm_payment(booking_id=booking_id)
        flash(f"Payment received successfully for Booking #{booking.booking_reference or booking.id}! Status is now Confirmed.", "success")
        return redirect(url_for("bookings_web.booking_detail", booking_id=booking.id))
    except ValueError as e:
        flash(str(e), "danger")
        return redirect(url_for("bookings_web.booking_history"))
    except Exception as e:
        flash(f"Payment verification failed: {str(e)}", "danger")
        return redirect(url_for("bookings_web.booking_history"))
