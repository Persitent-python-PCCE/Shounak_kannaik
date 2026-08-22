"""
Database Seeding Script.

Populates initial seed data across:
- Venues, Sections (with prices), and Seats
- Users (Admin & Customer accounts)
- Payment Modes
- Genres & Event Types
- Events & Event-Genre mappings
- Event Schedules (linking Events to Venues)
- Sample User Documents

(Note: payment_statuses and booking_statuses are intentionally excluded)
"""

from datetime import datetime, timedelta, timezone
from werkzeug.security import generate_password_hash
from app import create_app
from config.settings import DevelopmentConfig
from config.database import db
from models.user import User
from models.venue import Venue, Section, Seat
from models.genre import Genre
from models.event import EventType, Event
from models.schedule import EventSchedule
from models.payment import PaymentMode
from models.document import UserDocument
from common.roles import Role


def seed_database():
    """Seed initial testing data into the database."""
    app = create_app(DevelopmentConfig)

    with app.app_context():
        print("--- Starting Database Seeding ---")

        # =========================================================
        # 1. Seed Users (Admin & Customer)
        # =========================================================
        users_data = [
            {
                "username": "admin",
                "email": "admin@ticketmaster.in",
                "password": "AdminPassword123!",
                "phone_no": "9820012345",
                "role": Role.ADMIN,
            },
            {
                "username": "shounak",
                "email": "shounak@example.com",
                "password": "Password123!",
                "phone_no": "9819987654",
                "role": Role.CUSTOMER,
            },
            {
                "username": "rohit_sharma",
                "email": "rohit.s@example.com",
                "password": "Password123!",
                "phone_no": "9811122334",
                "role": Role.CUSTOMER,
            },
        ]

        seeded_users = {}
        for u_data in users_data:
            user = db.session.execute(
                db.select(User).where(User.username == u_data["username"])
            ).scalar_one_or_none()

            if not user:
                user = User(
                    username=u_data["username"],
                    email=u_data["email"],
                    password_hash=generate_password_hash(u_data["password"]),
                    phone_no=u_data["phone_no"],
                    role=u_data["role"],
                    is_active=True,
                )
                db.session.add(user)
                db.session.flush()
                print(f"  + Seeded user: {user.username} ({user.role})")
            else:
                print(f"  - User exists: {user.username}")
            seeded_users[user.username] = user

        # =========================================================
        # 2. Seed Payment Modes
        # =========================================================
        payment_modes_data = [
            {"mode_name": "UPI", "description": "Instant payment via Google Pay, PhonePe, Paytm"},
            {"mode_name": "Credit Card", "description": "Visa, MasterCard, RuPay, Amex cards"},
            {"mode_name": "Debit Card", "description": "Direct bank debit card transaction"},
            {"mode_name": "Net Banking", "description": "Direct bank portal payment for major Indian banks"},
            {"mode_name": "Wallet", "description": "Digital wallet payments"},
        ]

        for pm_data in payment_modes_data:
            existing_pm = db.session.execute(
                db.select(PaymentMode).where(PaymentMode.mode_name == pm_data["mode_name"])
            ).scalar_one_or_none()

            if not existing_pm:
                pm = PaymentMode(
                    mode_name=pm_data["mode_name"],
                    description=pm_data["description"],
                )
                db.session.add(pm)
                print(f"  + Seeded PaymentMode: {pm.mode_name}")
            else:
                print(f"  - PaymentMode exists: {existing_pm.mode_name}")

        # =========================================================
        # 3. Seed Genres
        # =========================================================
        genres_data = [
            {"genre_name": "Bollywood", "description": "Hindi film music, live concerts, and soundtrack performances"},
            {"genre_name": "Rock", "description": "Classic, indie, and alternative rock music shows"},
            {"genre_name": "Cricket", "description": "International matches, T20 leagues, and domestic fixtures"},
            {"genre_name": "Stand-up Comedy", "description": "Live solo specials and comedy club line-ups"},
            {"genre_name": "Theatre & Drama", "description": "Stage plays, musicals, and classical dramatic performances"},
            {"genre_name": "EDM", "description": "Electronic dance music festivals and DJ concerts"},
            {"genre_name": "Classical Music", "description": "Indian classical, Hindustani, Carnatic, and orchestral performances"},
        ]

        seeded_genres = {}
        for g_data in genres_data:
            genre = db.session.execute(
                db.select(Genre).where(Genre.genre_name == g_data["genre_name"])
            ).scalar_one_or_none()

            if not genre:
                genre = Genre(
                    genre_name=g_data["genre_name"],
                    description=g_data["description"],
                )
                db.session.add(genre)
                db.session.flush()
                print(f"  + Seeded Genre: {genre.genre_name}")
            else:
                print(f"  - Genre exists: {genre.genre_name}")
            seeded_genres[genre.genre_name] = genre

        # =========================================================
        # 4. Seed Event Types
        # =========================================================
        event_types_data = [
            {"type_name": "Concert", "description": "Live musical tours, stadium shows, and orchestra events"},
            {"type_name": "Sports", "description": "Live sporting tournaments and stadium matches"},
            {"type_name": "Comedy Show", "description": "Stand-up comedy tours and open mics"},
            {"type_name": "Theatre Play", "description": "Auditorium theatrical acts and dramas"},
            {"type_name": "Festival", "description": "Multi-stage cultural, food, and music festivals"},
        ]

        seeded_types = {}
        for t_data in event_types_data:
            e_type = db.session.execute(
                db.select(EventType).where(EventType.type_name == t_data["type_name"])
            ).scalar_one_or_none()

            if not e_type:
                e_type = EventType(
                    type_name=t_data["type_name"],
                    description=t_data["description"],
                )
                db.session.add(e_type)
                db.session.flush()
                print(f"  + Seeded EventType: {e_type.type_name}")
            else:
                print(f"  - EventType exists: {e_type.type_name}")
            seeded_types[e_type.type_name] = e_type

        # =========================================================
        # 5. Seed Venues, Sections with Prices, and Seats
        # =========================================================
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
                        "description": "East pavilion prime view",
                        "price": 1200.00,
                        "seats": [
                            {"row": "A", "number": f"{i}", "seat_type": "Regular"}
                            for i in range(1, 21)
                        ],
                    },
                    {
                        "name": "Sunil Gavaskar Pavilion",
                        "description": "Covered lower tier near pitch",
                        "price": 3500.00,
                        "seats": [
                            {"row": "B", "number": f"{i}", "seat_type": "Premium"}
                            for i in range(1, 16)
                        ],
                    },
                    {
                        "name": "President's Box",
                        "description": "VIP air-conditioned corporate suite",
                        "price": 12000.00,
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
                        "name": "East Stand General",
                        "description": "Open-air energetic atmosphere seating",
                        "price": 800.00,
                        "seats": [
                            {"row": "ES-1", "number": f"{i}", "seat_type": "Regular"}
                            for i in range(1, 31)
                        ],
                    },
                    {
                        "name": "South Pavilion Tier 1",
                        "description": "Ground floor prime seats behind bowler's arm",
                        "price": 4000.00,
                        "seats": [
                            {"row": "SP-A", "number": f"{i}", "seat_type": "Premium"}
                            for i in range(1, 21)
                        ],
                    },
                    {
                        "name": "Club Lounge",
                        "description": "Luxury hospitality suite with buffet",
                        "price": 15000.00,
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
                        "name": "Balcony Center",
                        "description": "Elevated panoramic auditorium view",
                        "price": 1800.00,
                        "seats": [
                            {"row": "BAL-1", "number": f"{i}", "seat_type": "Regular"}
                            for i in range(1, 26)
                        ],
                    },
                    {
                        "name": "Plenary Hall - Front Stalls",
                        "description": "Front stage view with acoustic engineering",
                        "price": 5500.00,
                        "seats": [
                            {"row": "Stall-A", "number": f"{i}", "seat_type": "VIP"}
                            for i in range(1, 16)
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
                        "name": "North Stand General",
                        "description": "Public entrance seating area",
                        "price": 999.00,
                        "seats": [
                            {"row": "N-1", "number": f"{i}", "seat_type": "Regular"}
                            for i in range(1, 26)
                        ],
                    },
                    {
                        "name": "West Stand Platinum",
                        "description": "Prime grandstand covered seating",
                        "price": 4500.00,
                        "seats": [
                            {"row": "W-1", "number": f"{i}", "seat_type": "Premium"}
                            for i in range(1, 21)
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
                        "price": 2500.00,
                        "seats": [
                            {"row": "ORC-A", "number": f"{i}", "seat_type": "Premium"}
                            for i in range(1, 16)
                        ],
                    },
                    {
                        "name": "Royal Box",
                        "description": "Private premier box seating",
                        "price": 8000.00,
                        "seats": [
                            {"row": "BOX-1", "number": f"{i}", "seat_type": "VIP"}
                            for i in range(1, 9)
                        ],
                    },
                ],
            },
        ]

        seeded_venues = {}
        for v_data in venues_data:
            venue = db.session.execute(
                db.select(Venue).where(Venue.name == v_data["name"])
            ).scalar_one_or_none()

            if not venue:
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
                        price=s_data.get("price", 0.00),
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

                print(f"  + Seeded Venue: {venue.name} ({venue.city}) with priced sections & seats")
            else:
                # Update existing section prices if needed
                for s_data in v_data.get("sections", []):
                    existing_sec = db.session.execute(
                        db.select(Section).where(
                            Section.venue_id == venue.id,
                            Section.name == s_data["name"],
                        )
                    ).scalar_one_or_none()
                    if existing_sec:
                        existing_sec.price = s_data.get("price", 0.00)
                print(f"  * Updated section prices for venue: {venue.name}")

            seeded_venues[venue.name] = venue

        # =========================================================
        # 6. Seed Events and Link Genres
        # =========================================================
        events_data = [
            {
                "name": "A.R. Rahman Live in Concert - Symphony of Joy",
                "about": "Oscar-winning maestro A.R. Rahman brings his full orchestra and world-class vocalists for a 3-hour musical spectacle.",
                "event_type": "Concert",
                "age_rating": "All Ages",
                "poster_image_path": "/static/uploads/posters/ar_rahman_live.jpg",
                "genres": ["Bollywood", "Classical Music"],
            },
            {
                "name": "IPL 2026: Mumbai Indians vs Chennai Super Kings",
                "about": "The ultimate El Clasico of Indian cricket at the iconic Wankhede Stadium.",
                "event_type": "Sports",
                "age_rating": "All Ages",
                "poster_image_path": "/static/uploads/posters/mi_vs_csk.jpg",
                "genres": ["Cricket"],
            },
            {
                "name": "Zakir Khan - Tathastu Live Special",
                "about": "Sakht Launda Zakir Khan brings his blockbuster comedy special filled with nostalgia, laughter, and emotional storytelling.",
                "event_type": "Comedy Show",
                "age_rating": "16+",
                "poster_image_path": "/static/uploads/posters/zakir_khan_live.jpg",
                "genres": ["Stand-up Comedy"],
            },
            {
                "name": "Mughal-e-Azam: The Grand Musical",
                "about": "Broadway-style Indian musical extravaganza directed by Feroz Abbas Khan with live Kathak performances.",
                "event_type": "Theatre Play",
                "age_rating": "12+",
                "poster_image_path": "/static/uploads/posters/mughal_e_azam.jpg",
                "genres": ["Theatre & Drama", "Classical Music"],
            },
            {
                "name": "Sunburn Arena feat. Martin Garrix",
                "about": "World's #1 DJ Martin Garrix headlining the Sunburn Arena tour with jaw-dropping visual effects and laser shows.",
                "event_type": "Concert",
                "age_rating": "18+",
                "poster_image_path": "/static/uploads/posters/martin_garrix_sunburn.jpg",
                "genres": ["EDM", "Rock"],
            },
        ]

        seeded_events = {}
        for e_data in events_data:
            event = db.session.execute(
                db.select(Event).where(Event.name == e_data["name"])
            ).scalar_one_or_none()

            e_type = seeded_types.get(e_data["event_type"])
            if not event:
                event = Event(
                    name=e_data["name"],
                    about=e_data["about"],
                    event_type_id=e_type.id if e_type else None,
                    age_rating=e_data["age_rating"],
                    poster_image_path=e_data["poster_image_path"],
                )
                # Associate genres
                for g_name in e_data.get("genres", []):
                    genre_obj = seeded_genres.get(g_name)
                    if genre_obj and genre_obj not in event.genres:
                        event.genres.append(genre_obj)

                db.session.add(event)
                db.session.flush()
                print(f"  + Seeded Event: {event.name} (Genres: {', '.join(e_data['genres'])})")
            else:
                print(f"  - Event exists: {event.name}")
            seeded_events[event.name] = event

        # =========================================================
        # 7. Seed Event Schedules (Showtimes / Slots)
        # =========================================================
        base_time = datetime.now(timezone.utc) + timedelta(days=7)

        schedules_data = [
            {
                "event_name": "A.R. Rahman Live in Concert - Symphony of Joy",
                "venue_name": "Jio World Convention Centre",
                "start_datetime": base_time.replace(hour=18, minute=30, second=0, microsecond=0),
                "end_datetime": base_time.replace(hour=22, minute=0, second=0, microsecond=0),
                "status": "Scheduled",
            },
            {
                "event_name": "IPL 2026: Mumbai Indians vs Chennai Super Kings",
                "venue_name": "Wankhede Stadium",
                "start_datetime": (base_time + timedelta(days=3)).replace(hour=19, minute=30, second=0, microsecond=0),
                "end_datetime": (base_time + timedelta(days=3)).replace(hour=23, minute=30, second=0, microsecond=0),
                "status": "Scheduled",
            },
            {
                "event_name": "Zakir Khan - Tathastu Live Special",
                "about": "Live standup show",
                "venue_name": "NCPA - Jamshed Bhabha Theatre",
                "start_datetime": (base_time + timedelta(days=5)).replace(hour=20, minute=0, second=0, microsecond=0),
                "end_datetime": (base_time + timedelta(days=5)).replace(hour=22, minute=0, second=0, microsecond=0),
                "status": "Scheduled",
            },
            {
                "event_name": "Mughal-e-Azam: The Grand Musical",
                "venue_name": "NCPA - Jamshed Bhabha Theatre",
                "start_datetime": (base_time + timedelta(days=8)).replace(hour=17, minute=0, second=0, microsecond=0),
                "end_datetime": (base_time + timedelta(days=8)).replace(hour=20, minute=0, second=0, microsecond=0),
                "status": "Scheduled",
            },
            {
                "event_name": "Sunburn Arena feat. Martin Garrix",
                "venue_name": "Jawaharlal Nehru Stadium",
                "start_datetime": (base_time + timedelta(days=12)).replace(hour=16, minute=0, second=0, microsecond=0),
                "end_datetime": (base_time + timedelta(days=12)).replace(hour=23, minute=0, second=0, microsecond=0),
                "status": "Scheduled",
            },
        ]

        for s_info in schedules_data:
            ev = seeded_events.get(s_info["event_name"])
            vn = seeded_venues.get(s_info["venue_name"])
            if ev and vn:
                existing_sch = db.session.execute(
                    db.select(EventSchedule).where(
                        EventSchedule.event_id == ev.id,
                        EventSchedule.venue_id == vn.id,
                        EventSchedule.start_datetime == s_info["start_datetime"],
                    )
                ).scalar_one_or_none()

                if not existing_sch:
                    sch = EventSchedule(
                        event_id=ev.id,
                        venue_id=vn.id,
                        start_datetime=s_info["start_datetime"],
                        end_datetime=s_info["end_datetime"],
                        status=s_info["status"],
                    )
                    db.session.add(sch)
                    print(f"  + Seeded Schedule: '{ev.name}' at '{vn.name}' on {s_info['start_datetime'].strftime('%Y-%m-%d %H:%M')}")
                else:
                    print(f"  - Schedule exists: '{ev.name}' at '{vn.name}'")

        # =========================================================
        # 8. Seed Sample User Documents (KYC)
        # =========================================================
        customer = seeded_users.get("shounak")
        if customer:
            docs_data = [
                {
                    "user_id": customer.id,
                    "doc_type": "AADHAAR_CARD",
                    "file_path": "/static/uploads/id_docs/shounak_aadhaar.pdf",
                    "verified": True,
                },
                {
                    "user_id": customer.id,
                    "doc_type": "PAN_CARD",
                    "file_path": "/static/uploads/id_docs/shounak_pan.pdf",
                    "verified": False,
                },
            ]

            for d_data in docs_data:
                existing_doc = db.session.execute(
                    db.select(UserDocument).where(
                        UserDocument.user_id == d_data["user_id"],
                        UserDocument.doc_type == d_data["doc_type"],
                    )
                ).scalar_one_or_none()

                if not existing_doc:
                    doc = UserDocument(
                        user_id=d_data["user_id"],
                        doc_type=d_data["doc_type"],
                        file_path=d_data["file_path"],
                        verified=d_data["verified"],
                    )
                    db.session.add(doc)
                    print(f"  + Seeded UserDocument: {doc.doc_type} for user '{customer.username}'")
                else:
                    print(f"  - UserDocument exists: {existing_doc.doc_type}")

        # Commit all seeded data
        db.session.commit()
        print("\n--- Database Seeding Completed Successfully! ---")


if __name__ == "__main__":
    seed_database()
