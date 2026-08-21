"""
Event Controller.

Provides public endpoints for browsing, searching, and filtering events, event types, and genres.
"""

from flask import Blueprint, request, jsonify
from service.event_service import EventService
from dao.event_dao import EventDAO

event_controller = Blueprint("event_controller", __name__)
event_service = EventService(EventDAO())


@event_controller.route("/", methods=["GET"])
def get_events():
    """Endpoint to list all events or filter by criteria."""
    filters = request.args.to_dict()
    try:
        if filters:
            events = event_service.filter_events(filters)
        else:
            events = event_service.get_all_events()
        return jsonify([event.to_dict() for event in events]), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": "internal error occured"}), 500


@event_controller.route("/types", methods=["GET"])
def get_event_types():
    """Endpoint to list all event types/categories."""
    try:
        types = event_service.get_all_event_types()
        return jsonify([t.to_dict() for t in types]), 200
    except Exception as e:
        return jsonify({"error": "internal error occured"}), 500


@event_controller.route("/genres", methods=["GET"])
def get_genres():
    """Endpoint to list all available genres."""
    try:
        genres = event_service.get_all_genres()
        return jsonify([g.to_dict() for g in genres]), 200
    except Exception as e:
        return jsonify({"error": "internal error occured"}), 500


@event_controller.route("/<int:event_id>", methods=["GET"])
def get_event_by_id(event_id):
    """Endpoint to get details of a specific event."""
    try:
        event = event_service.get_event_by_id(event_id)
        return jsonify(event.to_dict()), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 404
    except Exception as e:
        return jsonify({"error": "internal error occured"}), 500


@event_controller.route("/<int:event_id>/genres", methods=["GET"])
def get_genres_for_event(event_id):
    """Endpoint to get all genres associated with an event."""
    try:
        genres = event_service.get_genres_for_event(event_id)
        return jsonify([g.to_dict() for g in genres]), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 404
    except Exception as e:
        return jsonify({"error": "internal error occured"}), 500
