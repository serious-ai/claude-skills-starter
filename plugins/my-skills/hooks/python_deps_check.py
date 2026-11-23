#!/usr/bin/env python3
"""SessionStart check: the default python3 can import every package in python_deps.json.

Homebrew moves python3 to a new minor version (3.14 to 3.15, say) with none of the old one's
packages, so every script that imports a third-party package breaks overnight. The first reinstall
can fail too: Homebrew can leave dist-info folders with no METADATA file in the new site-packages,
and pip then stops with "No package metadata was found".

This hook installs whatever is missing. If pip hits that metadata error, it reinstalls the Homebrew
formula behind each broken folder (or moves the folder aside when no formula owns it) and tries
again. It prints nothing when everything imports, and one line when it repaired something or could
not, so the session knows before it runs a script.

List your packages in python_deps.json as {"module name": "pip name"}.
Env, for tests: PYTHON_DEPS_FILE points at another list, PYTHON_DEPS_DRY=1 reports without installing.
"""
import glob, json, os, re, shutil, site, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
DEPS = os.environ.get("PYTHON_DEPS_FILE", os.path.join(HERE, "python_deps.json"))
DRY = os.environ.get("PYTHON_DEPS_DRY") == "1"


def missing(modules):
    """Modules the interpreter cannot import, checked in a fresh process so a new user site counts."""
    out = {}
    for mod, pkg in modules.items():
        r = subprocess.run([sys.executable, "-c", f"import {mod}"], capture_output=True, timeout=30)
        if r.returncode != 0:
            out[mod] = pkg
    return out


def broken_dist_infos(dirs):
    """dist-info folders with no METADATA file, the thing that makes pip refuse to resolve."""
    return sorted(di for d in dirs for di in glob.glob(os.path.join(d, "*.dist-info"))
                  if not os.path.exists(os.path.join(di, "METADATA")))


def site_dirs():
    dirs = list(site.getsitepackages()) + [site.getusersitepackages()]
    return [d for d in dirs if os.path.isdir(d)]


def pip_install(pkgs):
    r = subprocess.run([sys.executable, "-m", "pip", "install", "--user", "--break-system-packages",
                        "--quiet", "--disable-pip-version-check", *pkgs],
                       capture_output=True, text=True, timeout=240)
    return r.returncode, (r.stdout + r.stderr).strip()


def repair_broken(paths):
    brew = shutil.which("brew") or "/opt/homebrew/bin/brew"
    names = []
    for p in paths:
        name = re.sub(r"-[^-]+\.dist-info$", "", os.path.basename(p)).lower()
        if os.path.exists(brew) and subprocess.run([brew, "list", "--formula", name],
                                                   capture_output=True).returncode == 0:
            subprocess.run([brew, "reinstall", name], capture_output=True, timeout=300)
        if os.path.exists(p):
            shutil.move(p, p + ".broken")
        names.append(name)
    return names


def main():
    modules = json.load(open(DEPS))["modules"]
    miss = missing(modules)
    if not miss:
        return 0
    ver = sys.version.split()[0]
    pkgs = sorted(set(miss.values()))
    if DRY:
        print(f"Python deps: python3 {ver} is missing {', '.join(pkgs)}.")
        return 0
    rc, out = pip_install(pkgs)
    fixed = []
    if rc != 0 and "No package metadata" in out:
        fixed = repair_broken(broken_dist_infos(site_dirs()))
        rc, out = pip_install(pkgs)
    still = missing(modules)
    if still:
        last = out.splitlines()[-1] if out else "no output"
        print(f"Python deps: python3 {ver} is still missing {', '.join(sorted(set(still.values())))} "
              f"after an automatic repair ({last}). Fix it in this session before running a script that needs it.")
    else:
        extra = f", after reinstalling broken Homebrew packages {', '.join(fixed)}" if fixed else ""
        print(f"Python deps: python3 {ver} was missing {', '.join(pkgs)}; installed them{extra}.")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as e:  # never block a session start
        print(f"Python deps: the check itself failed ({e}).")
        sys.exit(0)
