"""Pytest-конфигурация для тестов SML.

Добавляет корень проекта в sys.path, чтобы `import tools.sml...`
работал при запуске из любой директории.
"""

from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[3]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
