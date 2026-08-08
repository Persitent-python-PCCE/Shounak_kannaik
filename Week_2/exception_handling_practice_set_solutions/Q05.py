def get_json_parser():
    """Use the faster 'orjson' library if installed, else fall back."""
    try:
        import orjson
        return orjson
    except ImportError:
        print('orjson not available -- falling back to standard json')
        import json
        return json


class ReportService:
    def __init__(self):
        self.connected = False

    def run_query(self):
        if not self.connected:
            raise RuntimeError("Database connection not established.")
        return "query results"


def generate_report(service):
    """TODO: call service.run_query() inside try/except RuntimeError,
    print the error message, and keep the program running."""
    try:
        service.run_query()
    except RuntimeError as e:
        print(e)


# --- Test cases ---
get_json_parser()
generate_report(ReportService())