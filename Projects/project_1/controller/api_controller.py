
from flask import Blueprint, jsonify
from service.event_service import EventService
from dao.event_dao import EventDAO

api_controller = Blueprint("api_controller", __name__)
event_service = EventService(EventDAO())


@api_controller.route("/events", methods=["GET"])
def get_events():
    events = event_service.get_all_events()
    return jsonify([event.to_dict() for event in events])
