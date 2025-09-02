import os
import django
import pytest
from django.core.management import call_command


def pytest_configure():
    # Use sqlite for tests and generate migrations before DB setup
    os.environ.setdefault("USE_SQLITE_FOR_TESTS", "1")
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
    django.setup()
    try:
        call_command("makemigrations", "accounts", "billing", "chat", verbosity=0, interactive=False)
    except Exception:
        # In case migrations already exist or no changes
        pass

