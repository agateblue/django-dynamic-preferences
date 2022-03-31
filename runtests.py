import sys, os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "tests.settings")

    try:
        import django

        setup = django.setup
    except AttributeError:
        pass
    else:
        setup()

    from django_nose import NoseTestSuiteRunner
except ImportError:
    import traceback

    traceback.print_exc()
    raise ImportError("To fix this error, run: pip install -r requirements-test.txt")

import logging

logging.disable(logging.WARNING)
logging.captureWarnings(True)


def run_tests(*test_args):
    if not test_args:
        test_args = ["tests"]

    # Run tests
    test_runner = NoseTestSuiteRunner(verbosity=1)

    failures = test_runner.run_tests(test_args)

    if failures:
        sys.exit(failures)


if __name__ == "__main__":
    run_tests(*sys.argv[1:])
