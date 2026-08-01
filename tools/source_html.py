"""Load the preserved DC/NGC HTML source used by the generators."""

import os
import subprocess
from pathlib import Path


DEFAULT_REPOSITORY = Path(
    os.environ.get(
        "EPHINEA4HAVEN_REPO",
        Path(__file__).resolve().parents[2] / "ephinea4haven.github.io",
    )
)
DEFAULT_REVISION = os.environ.get(
    "DROPTABLE_SOURCE_REVISION",
    "7280fec3e435bf06b2d0a25659478ef5375eb86c",
)


def read_legacy_html(version, filename, *, source_dir=None):
    """Read a DC/NGC source page from a directory or preserved Git revision."""
    if source_dir is not None:
        path = Path(source_dir) / filename
        if path.is_file():
            return path.read_text(encoding="utf-8")

    repository = DEFAULT_REPOSITORY
    if not (repository / ".git").exists():
        raise FileNotFoundError(
            f"Legacy source unavailable: {version}/{filename}; "
            f"set EPHINEA4HAVEN_REPO or provide source_dir"
        )

    object_name = f"{DEFAULT_REVISION}:droptable/{version}/{filename}"
    try:
        result = subprocess.run(
            ["git", "-C", str(repository), "show", object_name],
            check=True,
            capture_output=True,
            text=True,
            timeout=15,
        )
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired) as exc:
        raise RuntimeError(f"Cannot read preserved source {object_name}") from exc
    return result.stdout
