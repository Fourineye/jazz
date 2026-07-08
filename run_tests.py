import unittest
import sys
import os

def run_all_tests():
    # Ensure the root directory is in the sys.path
    root_dir = os.path.dirname(os.path.abspath(__file__))
    if root_dir not in sys.path:
        sys.path.insert(0, root_dir)

    # Discover and run tests in the 'unit_tests' directory
    loader = unittest.TestLoader()
    suite = loader.discover(start_dir=os.path.join(root_dir, "unit_tests"), pattern="test_*.py")

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # Exit with code 0 if successful, 1 if failed
    sys.exit(0 if result.wasSuccessful() else 1)

if __name__ == "__main__":
    run_all_tests()
