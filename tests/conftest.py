from __future__ import annotations

import sys
from pathlib import Path


def pytest_configure() -> None:
    """Ensure project root is importable so `import src...` works in tests.

    Tests are executed from various working directories/contexts; adding the
    repository root to sys.path keeps imports stable without requiring an
    editable install.
    """

    repo_root = Path(__file__).resolve().parents[1]
    sys.path.insert(0, str(repo_root))
