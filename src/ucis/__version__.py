
BASE = "0.1.5"
SUFFIX = ""

__version__ = (BASE, SUFFIX)

# Package version string used by pyproject.toml dynamic versioning
_pkg_version = BASE + SUFFIX


def get_version():
    """Return the full version string, querying git when running from source."""
    base, suffix = __version__
    if suffix:
        return "%s%s" % (base, suffix)
    # Try to append git commit info when running from a source tree
    try:
        import subprocess, os
        src_dir = os.path.dirname(os.path.dirname(os.path.dirname(
            os.path.abspath(__file__))))
        out = subprocess.check_output(
            ["git", "describe", "--tags", "--dirty", "--always"],
            cwd=src_dir,
            stderr=subprocess.DEVNULL,
        ).decode().strip()
        # If the tag matches BASE exactly, no suffix needed
        if out != base:
            return "%s+%s" % (base, out)
    except Exception:
        pass
    return base
