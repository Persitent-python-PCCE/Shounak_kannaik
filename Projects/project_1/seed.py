"""
Database Seeding Script.

Populates initial lookup data (venues, sections, seats, etc.)
for development and testing environments.
"""

from app import create_app
from config.settings import DevelopmentConfig
from config.database import db
from models.venue import Venue, Section, Seat


def seed_database():
    """Seed initial data into the database."""
    app = create_app(DevelopmentConfig)

    with app.app_context():
        print("Starting database seeding...")

        # Indian Venues Data (Stadiums, Auditoriums, Arenas, Convention Centres)
        venues_data = [
            {
                "name": "Wankhede Stadium",
                "address": "Vinoo Mankad Rd, Churchgate",
                "city": "Mumbai",
                "state": "Maharashtra",
                "country": "India",
                "capacity": 33108,
                "sections": [
                    {
                        "name": "Sachin Tendulkar Stand",
                        "description": "East pavilion premium view",
                        "seats": [
                            {"row": "A", "number": f"{i}", "seat_type": "Regular"}
                            for i in range(1, 21)
                        ],
                    },
                    {
                        "name": "Sunil Gavaskar Pavilion",
                        "description": "Covered lower tier near pitch",
                        "seats": [
                            {"row": "B", "number": f"{i}", "seat_type": "Premium"}
                            for i in range(1, 16)
                        ],
                    },
                    {
                        "name": "President's Box",
                        "description": "VIP air-conditioned corporate suite",
                        "seats": [
                            {"row": "VIP-1", "number": f"{i}", "seat_type": "VIP"}
                            for i in range(1, 11)
                        ],
                    },
                ],
            },
            {
                "name": "Narendra Modi Stadium",
                "address": "Stadium Rd, Motera",
                "city": "Ahmedabad",
                "state": "Gujarat",
                "country": "India",
                "capacity": 132000,
                "sections": [
                    {
                        "name": "South Pavilion Tier 1",
                        "description": "Ground floor prime seats behind bowler's arm",
                        "seats": [
                            {"row": "SP-A", "number": f"{i}", "seat_type": "Premium"}
                            for i in range(1, 21)
                        ],
                    },
                    {
                        "name": "East Stand General",
                        "description": "Open-air energetic atmosphere seating",
                        "seats": [
                            {"row": "ES-1", "number": f"{i}", "seat_type": "Regular"}
                            for i in range(1, 31)
                        ],
                    },
                    {
                        "name": "Club Lounge",
                        "description": "Luxury hospitality suite with buffet",
                        "seats": [
                            {"row": "CL", "number": f"{i}", "seat_type": "VIP"}
                            for i in range(1, 11)
                        ],
                    },
                ],
            },
            {
                "name": "Jio World Convention Centre",
                "address": "G Block, Bandra Kurla Complex, Bandra East",
                "city": "Mumbai",
                "state": "Maharashtra",
                "country": "India",
                "capacity": 16500,
                "sections": [
                    {
                        "name": "Plenary Hall - Front Stalls",
                        "description": "Front stage view with acoustic engineering",
                        "seats": [
                            {"row": "Stall-A", "number": f"{i}", "seat_type": "VIP"}
                            for i in range(1, 16)
                        ],
                    },
                    {
                        "name": "Balcony Center",
                        "description": "Elevated panoramic auditorium view",
                        "seats": [
                            {"row": "BAL-1", "number": f"{i}", "seat_type": "Regular"}
                            for i in range(1, 26)
                        ],
                    },
                ],
            },
            {
                "name": "Jawaharlal Nehru Stadium",
                "address": "Pragati Vihar, Bhishma Pitamah Marg",
                "city": "New Delhi",
                "state": "Delhi",
                "country": "India",
                "capacity": 60000,
                "sections": [
                    {
                        "name": "West Stand Platinum",
                        "description": "Prime grandstand covered seating",
                        "seats": [
                            {"row": "W-1", "number": f"{i}", "seat_type": "Premium"}
                            for i in range(1, 21)
                        ],
                    },
                    {
                        "name": "North Stand General",
                        "description": "Public entrance seating area",
                        "seats": [
                            {"row": "N-1", "number": f"{i}", "seat_type": "Regular"}
                            for i in range(1, 26)
                        ],
                    },
                ],
            },
            {
                "name": "NCPA - Jamshed Bhabha Theatre",
                "address": "NCPA Marg, Nariman Point",
                "city": "Mumbai",
                "state": "Maharashtra",
                "country": "India",
                "capacity": 1109,
                "sections": [
                    {
                        "name": "Orchestra",
                        "description": "Close to orchestra pit and stage",
                        "seats": [
                            {"row": "ORC-A", "number": f"{i}", "seat_type": "Premium"}
                            for i in range(1, 16)
                        ],
                    },
                    {
                        "name": "Royal Box",
                        "description": "Private premier box seating",
                        "seats": [
                            {"row": "BOX-1", "number": f"{i}", "seat_type": "VIP"}
                            for i in range(1, 9)
                        ],
                    },
                ],
            },
        ]

        for v_data in venues_data:
            existing = db.session.execute(
                db.select(Venue).where(Venue.name == v_data["name"])
            ).scalar_one_or_none()

            if not existing:
                venue = Venue(
                    name=v_data["name"],
                    address=v_data["address"],
                    city=v_data["city"],
                    state=v_data["state"],
                    country=v_data["country"],
                    capacity=v_data["capacity"],
                )
                db.session.add(venue)
                db.session.flush()

                for s_data in v_data.get("sections", []):
                    section = Section(
                        venue_id=venue.id,
                        name=s_data["name"],
                        description=s_data.get("description"),
                    )
                    db.session.add(section)
                    db.session.flush()

                    for st_data in s_data.get("seats", []):
                        seat = Seat(
                            section_id=section.id,
                            row=st_data["row"],
                            number=st_data["number"],
                            seat_type=st_data.get("seat_type", "Regular"),
                        )
                        db.session.add(seat)

                print(f"  + Seeded venue: {venue.name} ({venue.city}, {venue.state}) with sections & seats")
            else:
                print(f"  - Venue already exists: {existing.name}")

        db.session.commit()
        print("Database seeding completed successfully.")


if __name__ == "__main__":
    seed_database()
