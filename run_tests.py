import unittest
import sys
import os

def run_all_tests():
    # Ensure the root directory is in the sys.path
    root_dir = os.path.dirname(os.path.abspath(__file__))
    if root_dir not in sys.path:
        sys.path.insert(0, root_dir)

    # Discover tests as the 'unit_tests' package so script paths like
    # "unit_tests.test_x.func" resolve to the same module the test runs in
    loader = unittest.TestLoader()
    suite = loader.discover(
        start_dir=os.path.join(root_dir, "unit_tests"), pattern="test_*.py", top_level_dir=root_dir
    )

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # Exit with code 0 if successful, 1 if failed
    sys.exit(0 if result.wasSuccessful() else 1)

if __name__ == "__main__":
    run_all_tests()
