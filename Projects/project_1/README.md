# Ticket Booking Application

A production-grade Flask ticket-booking application implementing strict Layered Architecture (DAO → Service → Controller) with Constructor Dependency Injection, Application Factory Pattern, and Flask-Migrate database versioning.

---

## 🏛️ Architectural Pattern

This project strictly adheres to the 4-layer architecture pattern:

1. **Models (`models/`)**: Plain `db.Model` subclasses with `to_dict()` serialization methods.
2. **DAOs (`dao/`)**: Data Access Objects holding **no constructor arguments**, using the global `db` extension directly. Every method is instance-based (`self`), and this is the **ONLY** layer allowed to execute SQLAlchemy queries (`db.session`, `Model.query`).
3. **Services (`service/`)**: Business logic layer receiving DAO dependencies via **Constructor Injection** (`def __init__(self, some_dao)`). Services never instantiate DAOs directly, ensuring complete unit testability with mock/fake DAOs.
4. **Controllers (`controller/`)**: Plain Flask Blueprint route handlers. Each controller instantiates its Service + DAO **once at module level** as stateless singletons. Route functions delegate exclusively to the Service layer.

---

## 📁 Project Structure

```
ticket-booking-app/
├── app.py                      # Application Factory (create_app)
├── config/
│   ├── __init__.py
│   ├── database.py             # SQLAlchemy, Migrate, LoginManager instances
│   └── settings.py             # Config, DevelopmentConfig, TestingConfig
├── models/
│   ├── __init__.py             # Re-exports all models
│   ├── user.py                 # User (UserMixin, db.Model)
│   ├── event.py                # Event
│   ├── genre.py                # Genre
│   ├── venue.py                # Venue, Section, Seat
│   ├── schedule.py             # EventSchedule
│   ├── booking.py              # Booking, BookingItem
│   ├── payment.py              # PaymentMode, PaymentStatus
│   └── document.py             # UserDocument
├── dao/
│   ├── __init__.py
│   ├── user_dao.py             # UserDAO
│   ├── event_dao.py            # EventDAO
│   ├── venue_dao.py            # VenueDAO
│   ├── booking_dao.py          # BookingDAO
│   └── payment_dao.py          # PaymentDAO
├── service/
│   ├── __init__.py
│   ├── auth_service.py         # AuthService(user_dao)
│   ├── event_service.py        # EventService(event_dao)
│   ├── booking_service.py      # BookingService(booking_dao)
│   └── admin_service.py        # AdminService(user_dao)
├── controller/
│   ├── __init__.py
│   ├── auth_controller.py      # /auth (login, register)
│   ├── event_controller.py     # /events (event catalog)
│   ├── booking_controller.py   # /bookings (reservations)
│   ├── admin_controller.py     # /admin (user & system admin)
│   └── api_controller.py       # /api (general/legacy API)
├── common/
│   ├── __init__.py
│   ├── decorators.py           # @login_required, @admin_required
│   ├── file_utils.py           # Upload helpers
│   ├── validators.py           # Input validation helpers
│   └── exceptions.py           # SeatUnavailableError, DuplicateBookingError
├── forms/
│   ├── __init__.py
│   ├── auth_forms.py           # LoginForm, RegisterForm
│   ├── event_forms.py          # EventForm
│   └── booking_forms.py        # BookingForm
├── templates/
│   ├── base.html
│   ├── auth/login.html
│   ├── events/list.html
│   ├── bookings/list.html
│   └── admin/dashboard.html
├── static/
│   ├── css/style.css
│   ├── js/
│   └── uploads/
│       ├── posters/
│       └── id_docs/
├── tests/
│   ├── __init__.py
│   ├── conftest.py             # Testing fixtures (create_app(TestingConfig))
│   ├── test_auth.py
│   ├── test_rbac.py
│   ├── test_events.py
│   ├── test_bookings.py
│   ├── test_seat_availability.py
│   ├── test_file_upload.py
│   └── test_api_errors.py
├── docs/
│   └── architecture_explainer.md # Detailed architectural decisions & rationale
├── .env.example
├── .gitignore
├── requirements.txt
├── seed.py
└── README.md
```

---

## 🚀 Setup and Installation

### 1. Create and Activate Virtual Environment
```bash
python -m venv .venv
# On Windows:
.venv\Scripts\activate
# On Linux/macOS:
source .venv/bin/activate
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Environment Configuration
Copy the example environment file and configure your database credentials:
```bash
cp .env.example .env
```
Edit `.env` with your MySQL connection string:
```ini
SQLALCHEMY_DATABASE_URI=mysql+pymysql://root:password@localhost/ticket_booking_db
SECRET_KEY=your-secret-key-here
```

### 4. Database Migrations
Initialize and run Flask-Migrate migrations:
```bash
flask db init
flask db migrate -m "Initial migration"
flask db upgrade
```

### 5. Seed Initial Data (Optional)
```bash
python seed.py
```

### 6. Run the Application
```bash
python app.py
# Or using the Flask CLI:
flask run
```

### 7. Run Test Suite
```bash
pytest tests/ -v
```
