import time
from flask import request, g

def register_global_middleware(app):


    @app.before_request
    def start_timer():
        g.start_time = time.time()

    @app.after_request
    def log_and_secure_response(response):
        duration = 0
        if hasattr(g, "start_time"):
            duration_ms = round((time.time()-g.start_time)*1000, 2)

        ip = request.remote_addr
        method = request.method
        path = request.path
        status = response.status_code

        app.logger.info(f'[{method}] {path} | Status: {status} | Latency: {duration_ms}ms | IP:{ip}')

        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"

        return response
