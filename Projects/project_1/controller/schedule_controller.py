
from flask import Blueprint, request, jsonify
from service.schedule_service import ScheduleService
from dao.schedule_dao import ScheduleDAO

schedule_controller = Blueprint("schedule_controller", __name__)
schedule_service = ScheduleService(ScheduleDAO())


@schedule_controller.route("/", methods=["GET"])
def get_schedules():
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
    try:
        schedule = schedule_service.get_schedule_by_id(schedule_id)
        return jsonify(schedule.to_dict()), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 404
    except Exception as e:
        return jsonify({"error": "internal error occured"}), 500


@schedule_controller.route("/event/<int:event_id>", methods=["GET"])
def get_schedules_for_event(event_id):
    try:
        schedules = schedule_service.get_schedules_for_event(event_id)
        return jsonify([s.to_dict() for s in schedules]), 200
    except Exception as e:
        return jsonify({"error": "internal error occured"}), 500


@schedule_controller.route("/venue/<int:venue_id>", methods=["GET"])
def get_schedules_for_venue(venue_id):
    try:
        schedules = schedule_service.get_schedules_for_venue(venue_id)
        return jsonify([s.to_dict() for s in schedules]), 200
    except Exception as e:
        return jsonify({"error": "internal error occured"}), 500
