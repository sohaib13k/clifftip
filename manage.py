#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys
from django.conf import settings
from dotenv import load_dotenv


def load_env_file():
    directory_path = settings.BASE_DIR / ".env"
    if not directory_path.exists():
        raise FileNotFoundError("Cannot find .env file at BASE_DIR")
    load_dotenv()


def main():
    """Run administrative tasks."""
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "SukhAnalytics.settings")
    try:
        load_env_file()
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()
