#!/usr/bin/env python
# -*- coding: utf-8 -*-
from unittest import defaultTestLoader as TestLoader
try:
    from colour_runner.runner import ColourTextTestRunner as TextTestRunner
except ImportError:
    from unittest import TextTestRunner as TextTestRunner
try:
    import coverage
    coverage_available = True
except ImportError:
    coverage_available = False


if __name__ == "__main__":
    if coverage_available:
        cov = coverage.coverage()
        cov.start()
    TextTestRunner(verbosity=2).run(TestLoader.discover('unittests'))
    if coverage_available:
        cov.stop()
        cov.save()

        print("Total coverage: {}%".format(cov.html_report()))
