"""
Event Service.

Handles business logic for event discovery, scheduling, and catalog management.
Receives DAOs via constructor injection to facilitate unit testing with mock DAOs.
"""


class EventService:
    """
    Service layer handling event operations.
    """

    def __init__(self, event_dao):
        """
        Constructor injection of the EventDAO dependency.

        :param event_dao: EventDAO instance (or fake/mock DAO in tests)
        """
        self.event_dao = event_dao

    def get_all_events(self):
        """
        Retrieve all available events.

        :return: list of Event instances
        """
        return self.event_dao.get_all()
