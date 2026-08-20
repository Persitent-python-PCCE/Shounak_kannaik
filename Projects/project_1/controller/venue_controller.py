from flask import Blueprint, request, jsonify
from dao.venue_dao import VenueDAO
from service.venue_service import VenueService


venue_controller = Blueprint("venue_controller", __name__)
venue_service = VenueService(VenueDAO())

@venue_controller.route("/", methods=["GET"])
def get_venues():
    filters = request.args.to_dict()
    try:
        if filters:
            venues = venue_service.filter_venue(filters)
        else:
            venues = venue_service.get_all_venues()
        return jsonify([venue.to_dict() for venue in venues]), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": "internal error occured"}), 500

@venue_controller.route("/<int:venue_id>", methods=["GET"])
def get_venue_by_id(venue_id):
    try:
        venue = venue_service.get_by_id(venue_id)
        if not venue:
            return jsonify({"error": "Venue not found"}), 404
        return jsonify(venue.to_dict()), 200
    except Exception as e:
        return jsonify({"error": "internal error occured"}), 500
