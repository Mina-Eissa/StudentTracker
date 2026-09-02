import os

from .settings import *  # noqa: F401,F403

# Tests run against a local/disposable Postgres, never against the real
# Supabase project — pytest-django creates and destroys a test database on
# every run, which you do not want happening to a shared, hosted database.
#
# Quickest way to get one running locally:
#   docker run -d -p 5432:5432 -e POSTGRES_PASSWORD=postgres postgres:15
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.getenv("TEST_DB_NAME", "studenttracker_test"),
        "USER": os.getenv("TEST_DB_USER", "postgres"),
        "PASSWORD": os.getenv("TEST_DB_PASSWORD", "postgres"),
        "HOST": os.getenv("TEST_DB_HOST", "localhost"),
        "PORT": os.getenv("TEST_DB_PORT", "5432"),
    }
}
