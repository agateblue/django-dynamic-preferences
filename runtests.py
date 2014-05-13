import sys
import test_settings

from django.test.runner import DiscoverRunner
test_runner = DiscoverRunner(verbosity=1)
failures = test_runner.run_tests(['dynamic_preferences', ])
if failures:
    sys.exit(failures)