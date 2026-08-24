# Flask Ticket-Booking Architecture Deep-Dive

This document provides a comprehensive explanation of the architectural decisions, design patterns, routing mechanisms, and database strategies implemented in this project.

---

## High-Level System Architecture

The application implements a strict **4-Layer Architecture**:

```
 ┌────────────────────────────────────────────────────────┐
 │                      Client / HTTP                     │
 └───────────────────────────┬────────────────────────────┘
                             │ (Request)
                             ▼
 ┌────────────────────────────────────────────────────────┐
 │                   Controller Layer                     │
 │  (controller/*.py - Flask Blueprints & Route Handlers) │
 └───────────────────────────┬────────────────────────────┘
                             │ Calls Service methods
                             ▼
 ┌────────────────────────────────────────────────────────┐
 │                     Service Layer                      │
 │     (service/*.py - Business Logic & Validation)       │
 └───────────────────────────┬────────────────────────────┘
                             │ Calls DAO methods (Injected)
                             ▼
 ┌────────────────────────────────────────────────────────┐
 │                   Data Access (DAO)                    │
 │       (dao/*.py - db.session / Query Execution)        │
 └───────────────────────────┬────────────────────────────┘
                             │ Queries & Persists
                             ▼
 ┌────────────────────────────────────────────────────────┐
 │                 Models & Database Layer                │
 │    (models/*.py - db.Model / MySQL via SQLAlchemy)     │
 └────────────────────────────────────────────────────────┘
```

---

## 1. Routing & URL Resolution (`url_prefix`)

### How Routes Are Constructed
Flask routes are namespaced by **Blueprint `url_prefix`** configurations inside `app.py`.

```
                    ┌────────────────────────┐
                    │    Incoming Request    │
                    └───────────┬────────────┘
                                │
                                ▼
         URL Prefix (app.py) + Route Path (controller)
```

#### Example Breakdown:
1. **In [`app.py`](file:///c:/Users/samy4/OneDrive/Desktop/Python_Again/revature/Projects/project_1/app.py)**:
   ```python
   app.register_blueprint(admin_controller, url_prefix="/admin")
   ```
   *Flask prefixes all routes inside `admin_controller` with `/admin`.*

2. **In [`controller/admin_controller.py`](file:///c:/Users/samy4/OneDrive/Desktop/Python_Again/revature/Projects/project_1/controller/admin_controller.py)**:
   ```python
   @admin_controller.route("/users", methods=["GET"])
   def get_users():
       ...
   ```

3. **Resolved URL**:
   $$\text{Prefix (} \texttt{/admin} \text{)} + \text{Route (} \texttt{/users} \text{)} = \mathbf{\texttt{http://127.0.0.1:5000/admin/users}}$$

### Registered Blueprint Prefixes:
| Blueprint | File | URL Prefix | Example Endpoint | Purpose |
| :--- | :--- | :--- | :--- | :--- |
| `admin_controller` | `controller/admin_controller.py` | `/admin` | `GET /admin/users` | Admin user management & system ops |
| `auth_controller` | `controller/auth_controller.py` | `/auth` | `POST /auth/login` | User authentication & registration |
| `event_controller` | `controller/event_controller.py` | `/events` | `GET /events/` | Event catalog & schedule listings |
| `booking_controller` | `controller/booking_controller.py` | `/bookings` | `POST /bookings/` | Ticket booking & reservation lifecycle |
| `api_controller` | `controller/api_controller.py` | `/api` | `GET /api/events` | General API integration endpoints |

---

## 2. Constructor Injection: Why Services Receive DAOs via `__init__`

### The Problem with Direct Instantiation
If a Service instantiates its DAO internally:
```python
# Anti-pattern: Hardcoded dependency
class BookingService:
    def __init__(self):
        self.booking_dao = BookingDAO()  # tightly coupled to real database!
```
Every time `BookingService` is instantiated, it is permanently tied to `BookingDAO`, which executes live queries against a real SQL database. This makes unit testing impossible without spinning up and tearing down a live database for every test.

### The Solution: Constructor Dependency Injection
```python
# Clean Architecture: Dependency Injection
class BookingService:
    def __init__(self, booking_dao):
        self.booking_dao = booking_dao
```
The Service does not care *how* data is fetched or saved; it only requires that `self.booking_dao` satisfies the contract (e.g., provides a `.save_booking()` method).

### Walkthrough: Fast Unit Testing with Fake DAOs
With constructor injection, you can test complex business logic without connecting to any database:

```python
# Fake DAO used strictly for unit testing
class FakeBookingDAO:
    def __init__(self):
        self.saved_bookings = []

    def get_by_id(self, booking_id):
        for b in self.saved_bookings:
            if b.id == booking_id:
                return b
        return None

    def save_booking(self, booking):
        booking.id = len(self.saved_bookings) + 1
        self.saved_bookings.append(booking)
        return booking


def test_booking_service_creation_unit():
    # 1. Instantiate the fake DAO (zero DB connection needed)
    fake_dao = FakeBookingDAO()

    # 2. Inject the fake DAO into the Service
    service = BookingService(fake_dao)

    # 3. Execute the service logic
    booking = service.create_booking({"schedule_id": 10, "seats": [1, 2]})

    # 4. Assert business logic outcome
    assert booking.id == 1
    assert len(fake_dao.saved_bookings) == 1
```

---

## 3. Module-Level Instantiation: Singletons & Stateless Architecture

### Why Instantiation Sits at Module Level
In controller files, Services and DAOs are instantiated **once at module load**:
```python
# In controller/admin_controller.py
admin_controller = Blueprint("admin_controller", __name__)
admin_service = AdminService(UserDAO())  # Created ONCE on module import

@admin_controller.route("/users", methods=["GET"])
def get_users():
    return jsonify([u.to_dict() for u in admin_service.get_all_users()]), 200
```

### Why Not Create a New Instance Per Request?
1. **Zero Allocation Overhead**: Creating new Python objects for every incoming HTTP request creates unnecessary memory overhead and garbage collection pauses under high concurrent traffic.
2. **Stateless Design**: DAOs and Services hold **no request-specific state**. Their only instance variables are references to lower-layer objects (`self.user_dao = user_dao`).
3. **Thread Safety**: Because DAOs use `db.session` (which in Flask-SQLAlchemy is a scoped session managed per thread/request context), calling methods on a shared `UserDAO` instance from concurrent requests is 100% thread-safe.

---

## 4. Environment Variables: Why Hardcoding DB Credentials Breaks Real Teams

Beyond basic credential security, hardcoding connection strings in source code breaks real-world team workflows and continuous deployment:

1. **Developer Environment Incompatibilities**:
   - Developer A runs MySQL on port `3306` with user `root`.
   - Developer B runs MySQL on port `3307` in Docker.
   - Developer C runs Linux/macOS with socket authentication.
   - *If hardcoded, developers would constantly overwrite each other's credentials in Git commits.*
2. **Multi-Stage Deployment Pipelines**:
   - **Local Dev**: `mysql://localhost/ticket_booking_db`
   - **CI / Automated Tests**: `sqlite:///:memory:`
   - **Staging / QA**: `mysql://qa-cluster.internal/ticket_qa`
   - **Production**: `mysql+pymysql://app_prod:SecretPass@prod-db.rds.amazonaws.com:3306/ticket_prod`
3. **Automated Secret Rotation**:
   - Cloud platforms (AWS Secrets Manager, HashiCorp Vault, Kubernetes Secrets) rotate database credentials periodically without modifying source code.

---

## 5. Application Factory Pattern (`create_app`)

### Why Use `create_app()` Instead of Flat `app = Flask(__name__)`?
- **Multiple Configurations**: Enables running the app under `DevelopmentConfig`, `TestingConfig` (in-memory SQLite), and `ProductionConfig` dynamically.
- **Test Isolation**: Each pytest test case can spin up a clean app instance with its own isolated in-memory database and tear it down cleanly after test completion.
- **Prevents Circular Imports**: Extensions (`db`, `migrate`, `login_manager`) are created unbound in [`config/database.py`](file:///c:/Users/samy4/OneDrive/Desktop/Python_Again/revature/Projects/project_1/config/database.py) and attached to the app instance inside `create_app()` via `.init_app(app)`.

> **Important**: The Application Factory pattern only changes **how the Flask app is initialized**. It does **not** change how DAO, Service, or Controller classes are written or used.

---

## 6. Database Migrations (Flask-Migrate / Alembic)

Instead of unversioned `db.create_all()` calls, the project uses **Flask-Migrate** to track schema evolution over time.

### Workflow:
1. **Define/Update Model**: Add columns or new models in [`models/`](file:///c:/Users/samy4/OneDrive/Desktop/Python_Again/revature/Projects/project_1/models/).
2. **Generate Migration**:
   ```bash
   flask db migrate -m "Description of changes"
   ```
3. **Apply to Database**:
   ```bash
   flask db upgrade
   ```
4. **Rollback (if needed)**:
   ```bash
   flask db downgrade
   ```
