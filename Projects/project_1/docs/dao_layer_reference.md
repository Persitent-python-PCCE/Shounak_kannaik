# DAO Layer Reference Guide

This document provides a comprehensive technical overview of the Data Access Object (DAO) layer implemented in the Flask ticket-booking application.

---

## 1. Architectural Role of the DAO Layer

In this application's layered architecture:
```
Controller (HTTP routing / serialization)
   └── Service (Business logic orchestration / validation / transactions)
         └── DAO (Direct SQLAlchemy queries / CRUD / isolation)
               └── Database (MySQL / SQLite)
```

The DAO layer is the **sole component** permitted to access SQLAlchemy's `db.session`, construct `db.select()` queries, and invoke persistence methods (`add`, `delete`, `commit`, `rollback`). No Service or Controller should ever execute database queries directly.

---

## 2. Overview of Implemented DAOs

| DAO File | Class Name | Models Covered | Methods | Primary Responsibilities |
|---|---|---|:---:|---|
| [`user_dao.py`](file:///c:/Users/samy4/OneDrive/Desktop/Python_Again/revature/Projects/project_1/dao/user_dao.py) | `UserDAO` | `User` | 7 | User identity lookup, registration, auth verification, profile updates. |
| [`venue_dao.py`](file:///c:/Users/samy4/OneDrive/Desktop/Python_Again/revature/Projects/project_1/dao/venue_dao.py) | `VenueDAO` | `Venue` | 7 | Venue CRUD, multi-criteria filtering by name, city, state, capacity. |
| [`event_dao.py`](file:///c:/Users/samy4/OneDrive/Desktop/Python_Again/revature/Projects/project_1/dao/event_dao.py) | `EventDAO` | `Event`, `EventType`, `Genre`, `event_genres` | 11 | Event lifecycle, category and genre lookups, junction table mapping, event search. |
| [`payment_dao.py`](file:///c:/Users/samy4/OneDrive/Desktop/Python_Again/revature/Projects/project_1/dao/payment_dao.py) | `PaymentDAO` | `PaymentMode`, `PaymentStatus` | 5 | Read-only access to lookup tables for payment channels and transaction statuses. |
| [`booking_dao.py`](file:///c:/Users/samy4/OneDrive/Desktop/Python_Again/revature/Projects/project_1/dao/booking_dao.py) | `BookingDAO` | `Booking`, `BookingItem`, `BookingStatus` | 9 | Booking lookups, basic CRUD, status management, transactional booking stub. |
| [`document_dao.py`](file:///c:/Users/samy4/OneDrive/Desktop/Python_Again/revature/Projects/project_1/dao/document_dao.py) | `DocumentDAO` | `UserDocument` | 6 | Storage, lookup, update, and deletion of KYC/verification documents. |

---

## 3. Standardization Conventions Enforced

All newly generated DAOs strictly follow these patterns:

1. **SQLAlchemy 2.0 Query Style**:
   - Reads: `db.session.execute(db.select(Model).where(...)).scalars().all()`
   - Unique lookups: `db.session.execute(db.select(Model).where(...)).scalar_one_or_none()`
   - Primary key fetches: `db.session.get(Model, id)`
   - Legacy `Model.query.all()` / `filter_by()` is deprecated across new code.

2. **Standardized Mutation Signatures**:
   - `create_*(entity)` / `save_*(entity)`: `db.session.add(entity)` $\rightarrow$ `commit()` $\rightarrow$ `return entity`
   - `update_*(entity)`: `db.session.commit()` $\rightarrow$ `return entity` (caller mutates attributes on the attached entity before calling)
   - `delete_*(entity)`: `db.session.delete(entity)` $\rightarrow$ `commit()` $\rightarrow$ `return True`

3. **Explicit Junction Joins**:
   - When joining through core `Table` objects (such as `event_genres`), queries specify explicit `ON` conditions (e.g., `Event.id == event_genres.c.event_id`) to avoid `AmbiguousForeignKeysError`.

4. **ORM Relationship Association**:
   - Many-to-many relationship writes (e.g. `add_genre_to_event`) use the ORM collection `event.genres.append(genre)` with duplicate membership checks, allowing SQLAlchemy's unit of work to handle junction row insertion cleanly.

5. **Multi-Criteria Dynamic Search**:
   - Encapsulated within unified `filter_*(filters: dict)` methods dynamically chaining `.where()` clauses, preventing method proliferation.

---

## 4. Key Design Decisions

### A. Aggregate DAO Scope for Events (`EventDAO`)
`EventType` and `Genre` are auxiliary lookup tables tightly coupled to the `Event` domain. Rather than generating microscopic single-method DAOs for each lookup, `EventDAO` acts as an aggregate data access boundary for the Event domain.

### B. Dedicated `DocumentDAO`
Although `UserDocument` belongs to a user, it is separated from `UserDAO` to keep `UserDAO` focused purely on authentication, identity, and profile data. User document uploads often have distinct retention policies and storage lifecycles.

### C. Read-Focused `PaymentDAO`
`PaymentMode` (UPI, Net Banking, Credit Card) and `PaymentStatus` (Pending, Success, Failed) are seeded reference data. Write operations on these tables are typically administrative migrations, so `PaymentDAO` exposes read queries only. (Detailed financial ledger entries via `PaymentTransaction` will be added in a future phase).

---

## 5. The `create_booking_with_items` Implementation Notice

`BookingDAO.create_booking_with_items` is intentionally left as a stub raising `NotImplementedError`:

```python
def create_booking_with_items(self, booking, items):
    # TODO: implement manually — requires SELECT FOR UPDATE row locking
    # on seats, atomic commit of Booking + BookingItem rows, and rollback
    # on any seat conflict. Not auto-generated on purpose.
    raise NotImplementedError
```

### Why this is deferred:
Ticket reservation is a high-concurrency transactional boundary. An enterprise-grade implementation requires:
1. Pessimistic row locking (`with_for_update()`) on seat rows or schedule allocations to prevent double-booking.
2. Checking seat availability against active reservations and pending holds.
3. Atomic insertion of `Booking` header and all child `BookingItem` rows in a single database transaction.
4. Clean rollback and distinct domain exception on concurrency conflicts.

---

## 6. Next Steps

With all DAOs in place, the application is ready for:
1. **Service Layer Expansion**: Implementing `EventService`, `BookingService`, and `VenueService` to encapsulate business rules and validation.
2. **Controller Wiring**: Exposing REST endpoints with request parsing and response formatting.
