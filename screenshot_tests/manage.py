import os
import sys

if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "wagtail.tests.settings")
    os.environ.setdefault("REMOTE_USER_AUTH", "true")

    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)
