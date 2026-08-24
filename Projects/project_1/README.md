# Ticket Booking Application

A production-grade Flask ticket-booking platform implementing a strict 4-Layer Architecture (Models -> DAO -> Service -> Controller) with Constructor Dependency Injection, Application Factory Pattern, JWT Authentication with Role-Based Access Control, Dual Controller Subsystem (REST API with Swagger Docs + Web UI), Server-Side Pagination, Flask-Caching, and Flask-Migrate database versioning.

---

## Key Features

### 1. 4-Layer Clean Architecture
- **Strict Separation of Concerns**: Models -> Data Access Objects (DAO) -> Business Logic Services -> Controllers.
- **Constructor Dependency Injection**: Services receive DAOs through `__init__`, enabling complete testability and mock injection.
- **Stateless Singletons**: Controllers instantiate their respective Service and DAO at the module level.

### 2. Dual Controller Subsystem
- **REST API Endpoints**: JSON responses adhering to REST conventions for programmatic consumption.
  - Endpoints under `/auth`, `/events`, `/bookings`, `/admin`, `/venues`, `/schedules`, `/documents`, and `/payments`.
  - Interactive API documentation powered by Flasgger / Swagger 2.0 at `/apidocs/`.
- **Web UI (Server-Rendered HTML)**:
  - All web views namespaced under `/ui/` (e.g., `/ui/events`, `/ui/bookings`, `/ui/admin`).
  - Styled with Bootstrap 5, custom themes, and glassmorphism styling.
  - Active navigation menu link highlighting.
  - Toast and alert flash notifications for user actions.
  - Dedicated custom error templates (400, 401, 403, 404, 500) with automatic content negotiation (HTML for browsers, JSON for API clients).

### 3. Authentication & Role-Based Access Control (RBAC)
- **JWT Tokens**: Secure authentication utilizing JWTs with symmetric secret signing.
- **Dual Token Delivery**: Supported via `Authorization: Bearer <token>` headers (REST API) and secure `access_token_cookie` HttpOnly cookies (Web UI).
- **Role Enforcement**:
  - `admin`: Full system oversight, event creation/editing, venue configuration, user management, and booking analytics.
  - `customer`: Browse events, select seats, book tickets, view booking history, and manage uploaded KYC documents.
- **Route Protection**:
  - `@role_required(*roles)`: Returns standard JSON error payloads for unauthorized API requests.
  - `@ui_role_required(*roles)`: Redirects unauthenticated users to `/ui/login` with flash warnings.

### 4. Event Catalog & Server-Side Pagination
- **Browse & Filter**: Search events by name, event type, and date range.
- **Server-Side Pagination**: Flask-SQLAlchemy `db.paginate` pagination with deterministic ordering.
- **Configurable Page Size**: Choose between 5, 10, 15, or 20 events per page with filter retention across page transitions.
- **Multi-Genre Tagging**: Link multiple genres (e.g., Rock, Pop, EDM, Motorsport, Bollywood, Stand-up Comedy) to each event.

### 5. Seat Reservation & Booking Lifecycle
- **Interactive Venue Layouts**: Multi-section pricing (Regular, Premium, VIP) and individual seat rows.
- **Concurrency & Availability Checks**: Atomic validation of seat availability preventing double-booking race conditions.
- **Booking Items**: Multi-seat reservations captured under single order records with unique booking references.
- **Payment Processing**: Simulated payment workflows supporting UPI, Credit Card, Debit Card, Net Banking, and Wallets.

### 6. Admin Management Dashboard
- **Analytics Overview**: Real-time metric cards for total users, active events, total venues, confirmed bookings, and gross revenue.
- **Event Management**: Create and edit events with poster uploads and multi-genre selectors.
- **Venue & Seat Generator**: Create venues with dynamic section configurations (rows, seats per row, tiered pricing).
- **User Oversight**: View registered accounts, edit profiles, toggle active status, and delete users.
- **System Bookings Oversight**: Comprehensive table tracking booking statuses, timestamps, and customer details.

### 7. Performance & Caching
- **Flask-Caching Integration**: In-memory / Redis cache caching high-traffic query results (event listings, trending event calculations).
- **Targeted Cache Invalidation**: Automatic cache invalidation hooks triggered upon event updates, creations, and bookings.

---

## Architectural Pattern

```
 ┌────────────────────────────────────────────────────────┐
 │                 Client / Web Browser                   │
 └───────────────────────────┬────────────────────────────┘
                             │
            ┌────────────────┴────────────────┐
            ▼                                 ▼
   REST API (/events, ...)            Web UI (/ui/*)
   [JSON Controller]                  [Web Controller + Jinja2]
            │                                 │
            └────────────────┬────────────────┘
                             │ Calls Service Methods
                             ▼
 ┌────────────────────────────────────────────────────────┐
 │                     Service Layer                      │
 │     (service/*.py - Business Logic, Validation, Cache) │
 └───────────────────────────┬────────────────────────────┘
                             │ Injected DAO Instance
                             ▼
 ┌────────────────────────────────────────────────────────┐
 │                   Data Access (DAO)                    │
 │       (dao/*.py - SQLAlchemy Query Execution)          │
 └───────────────────────────┬────────────────────────────┘
                             │ Queries & Commits
                             ▼
 ┌────────────────────────────────────────────────────────┐
 │                 Models & Database Layer                │
 │    (models/*.py - db.Model / MySQL via SQLAlchemy)     │
 └────────────────────────────────────────────────────────┘
```

---

## Project Structure

```
ticket-booking-app/
├── app.py                      # Application Factory (create_app)
├── seed.py                     # Database Seeder (users, venues, genres, events, schedules)
├── requirements.txt            # Python dependencies
├── .env.example                # Sample environment configuration
├── config/
│   ├── __init__.py
│   ├── database.py             # SQLAlchemy db, Migrate, LoginManager instances
│   ├── settings.py             # Config, DevelopmentConfig, TestingConfig
│   └── swagger.py              # Flasgger Swagger configuration
├── models/
│   ├── __init__.py             # Re-exports all domain models
│   ├── user.py                 # User, Role enum
│   ├── event.py                # Event, EventType
│   ├── genre.py                # Genre, event_genres association table
│   ├── venue.py                # Venue, Section, Seat, SeatType enum
│   ├── schedule.py             # EventSchedule, ScheduleStatus enum
│   ├── booking.py              # Booking, BookingItem, BookingStatus enum
│   ├── payment.py              # PaymentMode, PaymentStatus enum
│   └── document.py             # UserDocument, DocumentType enum
├── dao/
│   ├── __init__.py
│   ├── user_dao.py             # UserDAO
│   ├── event_dao.py            # EventDAO (pagination, filtering, genres, trending)
│   ├── venue_dao.py            # VenueDAO (venues, sections, seats)
│   ├── schedule_dao.py         # ScheduleDAO (event schedules)
│   ├── booking_dao.py          # BookingDAO (bookings, items, reservations)
│   ├── payment_dao.py          # PaymentDAO (payment transactions)
│   └── document_dao.py         # DocumentDAO (user KYC documents)
├── service/
│   ├── __init__.py
│   ├── auth_service.py         # AuthService (tokens, user authentication)
│   ├── event_service.py        # EventService (event lifecycle, pagination, caching)
│   ├── venue_service.py        # VenueService (venues, dynamic seat builder)
│   ├── schedule_service.py     # ScheduleService (event schedule management)
│   ├── booking_service.py      # BookingService (concurrency, seat lock, reservation)
│   ├── payment_service.py      # PaymentService (payment handling)
│   ├── document_service.py     # DocumentService (KYC document handling)
│   └── admin_service.py        # AdminService (dashboard statistics, user oversight)
├── controller/
│   ├── __init__.py
│   ├── auth_controller.py      # /auth (API login, register)
│   ├── event_controller.py     # /events (API event catalog)
│   ├── venue_controller.py     # /venues (API venue listing)
│   ├── schedule_controller.py  # /schedules (API event schedules)
│   ├── booking_controller.py   # /bookings (API reservations)
│   ├── payment_controller.py   # /payments (API payment processing)
│   ├── document_controller.py  # /documents (API document uploads)
│   ├── admin_controller.py     # /admin (API admin management)
│   ├── api_controller.py       # /api (API health and discovery)
│   └── web/
│       ├── __init__.py
│       ├── auth_web_controller.py      # /ui/login, /ui/register, /ui/logout
│       ├── events_web_controller.py    # /ui/events (browse, filter, paginate)
│       ├── bookings_web_controller.py  # /ui/bookings (create booking, history)
│       ├── admin_web_controller.py     # /ui/admin (dashboard, events, venues, users)
│       ├── documents_web_controller.py # /ui/documents (KYC uploads)
│       └── payments_web_controller.py  # /ui/payments (payment checkout)
├── forms/
│   ├── __init__.py
│   ├── auth_forms.py           # LoginForm, RegisterForm, UserEditForm
│   ├── event_forms.py          # EventForm (with multi-genre selector)
│   └── booking_forms.py        # BookingForm, PaymentForm
├── common/
│   ├── __init__.py
│   ├── decorators.py           # @role_required (API), @ui_role_required (Web UI)
│   ├── file_utils.py           # File validation, MIME check, and storage
│   ├── validators.py           # Input validation helpers
│   └── exceptions.py           # Custom exception classes
├── templates/
│   ├── base.html               # Master layout with active navbar and alerts
│   ├── 403.html                # Custom Forbidden error page
│   ├── 404.html                # Custom Not Found error page
│   ├── 500.html                # Custom Server Error page
│   ├── auth/
│   │   ├── login.html
│   │   └── register.html
│   ├── events/
│   │   ├── list.html           # Event catalog with pagination controls
│   │   └── detail.html         # Event detail and schedule view
│   ├── bookings/
│   │   ├── list.html           # Customer booking history
│   │   ├── detail.html         # Booking itemized breakdown
│   │   └── seat_select.html    # Interactive seat selector
│   ├── admin/
│   │   ├── dashboard.html      # KPI analytics and quick actions
│   │   ├── event_list.html     # Admin event management table
│   │   ├── event_form.html     # Admin event create / edit form
│   │   ├── venue_list.html     # Admin venue management table
│   │   ├── venue_form.html     # Dynamic venue & section builder
│   │   ├── user_list.html      # Admin user management table
│   │   ├── user_form.html      # Admin user edit form
│   │   └── booking_list.html   # Admin system bookings oversight
│   ├── documents/
│   │   └── upload.html         # KYC document upload view
│   └── payments/
│       └── checkout.html       # Payment selection view
├── static/
│   ├── css/
│   │   └── style.css           # Custom styles, transitions, cards
│   ├── js/
│   │   └── main.js             # Client-side helpers
│   └── uploads/
│       ├── posters/            # Uploaded event poster images
│       └── id_docs/            # Uploaded user ID documents
├── swagger_specs/              # YAML OpenAPI specification files
│   ├── auth/
│   ├── events/
│   ├── venues/
│   ├── schedules/
│   ├── bookings/
│   ├── payments/
│   ├── documents/
│   ├── admin/
│   └── api/
├── tests/
│   ├── conftest.py             # Pytest fixtures and app factory configuration
│   ├── test_auth.py            # Authentication, JWT, and password hashing tests
│   ├── test_rbac.py            # Role-based access control tests
│   ├── test_events.py          # Event DAO, Service, and pagination tests
│   ├── test_bookings.py        # Booking creation and reservation tests
│   ├── test_seat_availability.py # Concurrency and seat conflict tests
│   ├── test_caching.py         # Flask-Caching memoization and invalidation tests
│   ├── test_file_upload.py     # File upload validation and security tests
│   ├── test_api_errors.py      # Error handler and exception handling tests
│   └── test_ui_layer.py        # Web UI routes, forms, pagination, and templates tests
└── docs/
    └── architecture_explainer.md # In-depth architectural documentation
```

---

## Setup and Installation

### 1. Prerequisites
- Python 3.10+
- MySQL Server 8.0+

### 2. Create and Activate Virtual Environment
```bash
# Clone the repository
cd ticket-booking-app

# Create virtual environment
python -m venv .venv

# Activate on Windows:
.venv\Scripts\activate

# Activate on Linux/macOS:
source .venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables
Copy `.env.example` to `.env` and set your database connection string and secret key:
```bash
cp .env.example .env
```

Edit `.env`:
```ini
FLASK_APP=app.py
FLASK_ENV=development
SECRET_KEY=your-secure-secret-key
JWT_SECRET_KEY=your-jwt-secret-key
SQLALCHEMY_DATABASE_URI=mysql+pymysql://root:password@localhost:3306/ticket_booking_db
CACHE_TYPE=SimpleCache
```

### 5. Initialize and Migrate Database
Run database migrations using Flask-Migrate:
```bash
flask db upgrade
```

### 6. Seed Sample Data
Populate the database with realistic events, venues, sections, priced seats, and schedules:
```bash
python seed.py
```

### 7. Run the Application
```bash
python app.py
```
The application will start at `http://127.0.0.1:5000/`.

---

## Accessing the Application

| Portal | URL | Description |
| :--- | :--- | :--- |
| **Browse Events (Web UI)** | `http://127.0.0.1:5000/ui/events` | Public event catalog with search & pagination |
| **User Login (Web UI)** | `http://127.0.0.1:5000/ui/login` | Login page for customers and admins |
| **User Registration (Web UI)**| `http://127.0.0.1:5000/ui/register` | Customer sign-up form |
| **Admin Dashboard (Web UI)** | `http://127.0.0.1:5000/ui/admin` | Management portal for events, venues, users |
| **Customer Bookings (Web UI)**| `http://127.0.0.1:5000/ui/bookings` | View booked tickets and reservation history |
| **Swagger API Documentation** | `http://127.0.0.1:5000/apidocs/` | Interactive OpenAPI documentation for REST endpoints |

---

## Seed User Accounts

| Username | Password | Role | Description |
| :--- | :--- | :--- | :--- |
| `admin` | `AdminPass123!` | Admin | System administrator with full access to `/ui/admin` |
| `shounak` | `Password123!` | Customer | Standard customer account for ticket bookings |
| `NewUser123` | `NewPass123!` | Customer | Additional test customer account |

---

## Running the Automated Test Suite

Execute the complete test suite using `pytest`:

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run specific test modules
pytest tests/test_ui_layer.py -v
pytest tests/test_events.py -v
pytest tests/test_bookings.py -v
```

### Test Coverage Summary
- **Unit & Integration Tests**: 57 automated tests passing.
- **Test Modules**:
  - `test_auth.py`: Password hashing, token generation, user authentication.
  - `test_rbac.py`: Role enforcement and permission validation.
  - `test_events.py`: DAO queries, service validation, server-side pagination.
  - `test_bookings.py`: Multi-seat booking workflows and state transitions.
  - `test_seat_availability.py`: Seat conflict prevention under concurrency.
  - `test_caching.py`: Flask-Caching memoization and mutation invalidation.
  - `test_file_upload.py`: File extension, MIME-type, and size security checks.
  - `test_api_errors.py`: Global HTTP error handlers and custom exceptions.
  - `test_ui_layer.py`: Web UI routes, navigation highlighting, server-side pagination controls, admin forms, and dynamic venue builder.
