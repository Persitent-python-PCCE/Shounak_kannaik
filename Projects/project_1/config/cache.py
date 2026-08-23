"""
Cache configuration and initialization module.

Initializes the Flask-Caching Cache instance without binding to a specific app instance.
It is bound during application factory execution via cache.init_app(app).
"""

from flask_caching import Cache

cache = Cache()
