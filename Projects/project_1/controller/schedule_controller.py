"""
Schedule Controller.

Provides public endpoints for browsing, querying, and filtering event schedules and showtimes.
"""

from flask import Blueprint, request, jsonify
from service.schedule_service import ScheduleService
from dao.schedule_dao import ScheduleDAO

schedule_controller = Blueprint("schedule_controller", __name__)
schedule_service = ScheduleService(ScheduleDAO())


@schedule_controller.route("/", methods=["GET"])
def get_schedules():
    """Endpoint to list all event schedules or filter by criteria."""
    filters = request.args.to_dict()
    try:
        if filters:
            schedules = schedule_service.filter_schedules(filters)
        else:
            schedules = schedule_service.get_all_schedules()
        return jsonify([s.to_dict() for s in schedules]), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": "internal error occured"}), 500


@schedule_controller.route("/<int:schedule_id>", methods=["GET"])
def get_schedule_by_id(schedule_id):
    """Endpoint to get a specific event schedule by ID."""
    try:
        schedule = schedule_service.get_schedule_by_id(schedule_id)
        return jsonify(schedule.to_dict()), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 404
    except Exception as e:
        return jsonify({"error": "internal error occured"}), 500


@schedule_controller.route("/event/<int:event_id>", methods=["GET"])
def get_schedules_for_event(event_id):
    """Endpoint to get all schedules for a specific event."""
    try:
        schedules = schedule_service.get_schedules_for_event(event_id)
        return jsonify([s.to_dict() for s in schedules]), 200
    except Exception as e:
        return jsonify({"error": "internal error occured"}), 500


@schedule_controller.route("/venue/<int:venue_id>", methods=["GET"])
def get_schedules_for_venue(venue_id):
    """Endpoint to get all schedules for a specific venue."""
    try:
        schedules = schedule_service.get_schedules_for_venue(venue_id)
        return jsonify([s.to_dict() for s in schedules]), 200
    except Exception as e:
        return jsonify({"error": "internal error occured"}), 500
