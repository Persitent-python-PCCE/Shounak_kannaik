

def test_get_events(client):
    response = client.get("/events/")
    assert response.status_code == 200
    assert isinstance(response.get_json(), list)


def test_dao_and_service_event_pagination(app):
    from dao.event_dao import EventDAO
    from service.event_service import EventService
    from models.event import Event, EventType
    from config.database import db

    with app.app_context():
        dao = EventDAO()
        service = EventService(dao)


        et = EventType(type_name="Festival", description="Festival events")
        db.session.add(et)
        db.session.commit()


        for i in range(1, 15):
            e = Event(name=f"Paginated Concert {i:02d}", event_type_id=et.id, age_rating="All Ages")
            dao.create_event(e)


        pagination = dao.get_all_events(page=1, per_page=5)
        assert len(pagination.items) == 5
        assert pagination.total >= 14
        assert pagination.pages >= 3
        assert pagination.has_next is True
        assert pagination.has_prev is False


        page2 = dao.get_all_events(page=2, per_page=5)
        assert len(page2.items) == 5
        assert page2.has_prev is True


        svc_pag = service.get_all_events_paginated(page=1, per_page=6)
        assert len(svc_pag.items) == 6
        assert svc_pag.page == 1


        filtered_pag = service.filter_events({"name": "Paginated Concert"}, page=1, per_page=4)
        assert len(filtered_pag.items) == 4
        assert filtered_pag.total == 14
        assert filtered_pag.pages == 4
