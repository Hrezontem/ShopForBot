import os
import sys
from pathlib import Path


def main():
    BACK_DIR = Path(__file__).resolve().parent
    if str(BACK_DIR) not in sys.path:
        sys.path.insert(0, str(BACK_DIR))

    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django."
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
