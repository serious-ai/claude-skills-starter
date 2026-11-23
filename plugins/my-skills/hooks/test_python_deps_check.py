#!/usr/bin/env python3
"""Tests for python_deps_check.py. Run: python3 test_python_deps_check.py

Dry mode only, so no test ever installs a package.
"""
import json, os, shutil, subprocess, sys, tempfile, unittest

HERE = os.path.dirname(os.path.abspath(__file__))
HOOK = os.path.join(HERE, "python_deps_check.py")
sys.path.insert(0, HERE)
import python_deps_check as pdc  # noqa: E402


class PythonDeps(unittest.TestCase):
    def setUp(self):
        self.root = tempfile.mkdtemp(prefix="pydeps-test-")

    def tearDown(self):
        shutil.rmtree(self.root)

    def run_hook(self, modules):
        deps = os.path.join(self.root, "deps.json")
        json.dump({"modules": modules}, open(deps, "w"))
        env = dict(os.environ, PYTHON_DEPS_FILE=deps, PYTHON_DEPS_DRY="1")
        return subprocess.run([sys.executable, HOOK], env=env, capture_output=True, text=True, timeout=60)

    def test_silent_when_everything_imports(self):
        r = self.run_hook({"json": "json", "os": "os"})
        self.assertEqual(r.returncode, 0)
        self.assertEqual(r.stdout, "")

    def test_reports_missing_module_by_pip_name(self):
        r = self.run_hook({"json": "json", "no_such_module_xyz": "no-such-package"})
        self.assertEqual(r.returncode, 0)
        self.assertIn("no-such-package", r.stdout)
        self.assertNotIn("json", r.stdout.split("missing")[1])

    def test_finds_dist_info_without_metadata(self):
        good = os.path.join(self.root, "good-1.0.dist-info")
        bad = os.path.join(self.root, "cffi-2.1.1.dist-info", "licenses")
        os.makedirs(good)
        open(os.path.join(good, "METADATA"), "w").close()
        os.makedirs(bad)
        self.assertEqual(pdc.broken_dist_infos([self.root]),
                         [os.path.join(self.root, "cffi-2.1.1.dist-info")])

    def test_bad_deps_file_never_blocks(self):
        env = dict(os.environ, PYTHON_DEPS_FILE=os.path.join(self.root, "missing.json"), PYTHON_DEPS_DRY="1")
        r = subprocess.run([sys.executable, HOOK], env=env, capture_output=True, text=True, timeout=30)
        self.assertEqual(r.returncode, 0)
        self.assertIn("check itself failed", r.stdout)


if __name__ == "__main__":
    unittest.main()
