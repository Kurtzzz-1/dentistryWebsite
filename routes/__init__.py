# This file makes the routes directory a Python package
# Import all route blueprints to make them available for import elsewhere
from routes.auth_routes import auth_bp  # noqa: F401
from routes.base_routes import base_bp  # noqa: F401
from routes.test_routes import test_bp  # noqa: F401
