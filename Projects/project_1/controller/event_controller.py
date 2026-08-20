"""
Event Controller.
"""

from flask import Blueprint, jsonify
from service.event_service import EventService
from dao.event_dao import EventDAO

event_controller = Blueprint("event_controller", __name__)
event_service = EventService(EventDAO())


@event_controller.route("/", methods=["GET"])
def get_events():
    """Endpoint to list all events."""
    events = event_service.get_all_events()
    return jsonify([event.to_dict() for event in events]), 200
