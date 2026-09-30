import os
import subprocess


def test_frontend_javascript_unit_tests():
    """Runs frontend unit tests with Node.js test runner."""
    frontend_test_dir = os.path.join(os.path.dirname(__file__), "frontend")
    test_files = [
        os.path.join(frontend_test_dir, f)
        for f in os.listdir(frontend_test_dir)
        if f.endswith(".test.js")
    ]
    assert len(test_files) > 0, "No frontend test files found"

    cmd = ["node", "--test"] + test_files
    result = subprocess.run(cmd, capture_output=True, text=True)

    assert (
        result.returncode == 0
    ), f"Frontend tests failed!\nSTDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}"
