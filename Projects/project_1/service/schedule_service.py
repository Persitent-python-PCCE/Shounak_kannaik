
from datetime import datetime
from models.schedule import EventSchedule


class ScheduleService:

    def __init__(self, schedule_dao):
        self.schedule_dao = schedule_dao

    def get_all_schedules(self):
        return self.schedule_dao.get_all_schedules()

    def get_schedule_by_id(self, schedule_id):
        schedule = self.schedule_dao.get_by_id(schedule_id)
        if not schedule:
            raise ValueError("Schedule not found.")
        return schedule

    def get_schedules_for_event(self, event_id):
        return self.schedule_dao.get_schedules_by_event_id(event_id)

    def get_schedules_for_venue(self, venue_id):
        return self.schedule_dao.get_schedules_by_venue_id(venue_id)

    def filter_schedules(self, filters: dict):
        cleaned_filters = {}
        if filters.get("event_id"):
            try:
                cleaned_filters["event_id"] = int(str(filters.get("event_id")).strip())
            except ValueError:
                raise ValueError("event_id must be a valid integer.")
        if filters.get("venue_id"):
            try:
                cleaned_filters["venue_id"] = int(str(filters.get("venue_id")).strip())
            except ValueError:
                raise ValueError("venue_id must be a valid integer.")
        if filters.get("status"):
            cleaned_filters["status"] = str(filters.get("status")).strip()
        if filters.get("from_date"):
            try:
                cleaned_filters["from_date"] = datetime.fromisoformat(str(filters.get("from_date")).strip())
            except ValueError:
                raise ValueError("from_date must be a valid ISO format datetime (YYYY-MM-DDTHH:MM:SS).")
        if filters.get("to_date"):
            try:
                cleaned_filters["to_date"] = datetime.fromisoformat(str(filters.get("to_date")).strip())
            except ValueError:
                raise ValueError("to_date must be a valid ISO format datetime (YYYY-MM-DDTHH:MM:SS).")

        return self.schedule_dao.filter_schedules(cleaned_filters)

    def create_schedule(self, data):
        if not data.get("event_id") or not data.get("venue_id"):
            raise ValueError("event_id and venue_id are required fields.")
        if not data.get("start_datetime") or not data.get("end_datetime"):
            raise ValueError("start_datetime and end_datetime are required fields.")


        start_dt = data.get("start_datetime")
        if isinstance(start_dt, str):
            try:
                start_dt = datetime.fromisoformat(start_dt)
            except ValueError:
                raise ValueError("start_datetime must be a valid ISO format datetime (YYYY-MM-DDTHH:MM:SS).")

        end_dt = data.get("end_datetime")
        if isinstance(end_dt, str):
            try:
                end_dt = datetime.fromisoformat(end_dt)
            except ValueError:
                raise ValueError("end_datetime must be a valid ISO format datetime (YYYY-MM-DDTHH:MM:SS).")

        if start_dt >= end_dt:
            raise ValueError("start_datetime must be earlier than end_datetime.")

        schedule = EventSchedule(
            event_id=int(data.get("event_id")),
            venue_id=int(data.get("venue_id")),
            start_datetime=start_dt,
            end_datetime=end_dt,
            status=data.get("status", "Scheduled"),
        )
        return self.schedule_dao.create_schedule(schedule)

    def update_schedule(self, data):
        schedule_id = data.get("schedule_id")
        if not schedule_id:
            raise ValueError("schedule_id is required.")

        schedule = self.get_schedule_by_id(schedule_id)

        if "event_id" in data and data["event_id"] is not None:
            schedule.event_id = int(data["event_id"])
        if "venue_id" in data and data["venue_id"] is not None:
            schedule.venue_id = int(data["venue_id"])
        if "status" in data and data["status"] is not None:
            schedule.status = str(data["status"])

        if "start_datetime" in data and data["start_datetime"] is not None:
            start_dt = data["start_datetime"]
            if isinstance(start_dt, str):
                try:
                    start_dt = datetime.fromisoformat(start_dt)
                except ValueError:
                    raise ValueError("start_datetime must be a valid ISO format datetime.")
            schedule.start_datetime = start_dt

        if "end_datetime" in data and data["end_datetime"] is not None:
            end_dt = data["end_datetime"]
            if isinstance(end_dt, str):
                try:
                    end_dt = datetime.fromisoformat(end_dt)
                except ValueError:
                    raise ValueError("end_datetime must be a valid ISO format datetime.")
            schedule.end_datetime = end_dt

        if schedule.start_datetime >= schedule.end_datetime:
            raise ValueError("start_datetime must be earlier than end_datetime.")

        return self.schedule_dao.update_schedule(schedule)

    def delete_schedule(self, schedule_id):
        schedule = self.get_schedule_by_id(schedule_id)
        return self.schedule_dao.delete_schedule(schedule)
