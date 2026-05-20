"""Детектор секретов для SML (Req 10.2; P6).

Два уровня проверки, применяются последовательно к ``content`` операций
``sml.write``, ``sml.add_decision`` и ``sml.add_log``.

1. **Паттерны известных секретов** (regex) — API-ключи OpenAI, Anthropic,
   GitHub, Slack, Google, AWS, JWT, PEM-ключи, пары ``api_key=``,
   ``password=``, GitLab PAT.
2. **Шенноновская энтропия** — скользящее окно по подстрокам из класса
   ``[A-Za-z0-9+/=_-]`` длины 20..200. Энтропия ≥ 4.5 бит/символ → секрет.
   Подстрока со ≥ 3 словарными словами длиной ≥ 4 считается НЕ секретом
   (снижает ложные срабатывания на текстах вперемешку с base64-подобными
   вставками).

Результат проверки — ``SecretCheck`` с категорией причины. Для MCP-ответа
достаточно вернуть ``reason_category``; сам секрет нигде не логируется
и не проксируется.
"""

from __future__ import annotations

import math
import re
from dataclasses import dataclass
from typing import List, Optional, Tuple

__all__ = [
    "SecretCheck",
    "KNOWN_SECRET_PATTERNS",
    "ENTROPY_THRESHOLD_BITS",
    "check_pattern",
    "check_entropy",
    "check_secret",
]


# ---------------------------------------------------------------------------
# Уровень 1: известные паттерны секретов
# ---------------------------------------------------------------------------


# Каждая запись — (имя_категории, regex). Имя попадает в
# ``reason_category`` Operation_Log и в сообщение ошибки.
KNOWN_SECRET_PATTERNS: List[Tuple[str, re.Pattern[str]]] = [
    # OpenAI
    ("openai_api_key", re.compile(r"\bsk-[A-Za-z0-9]{20,}\b")),
    # Anthropic
    ("anthropic_api_key", re.compile(r"\bsk-ant-[A-Za-z0-9\-_]{20,}\b")),
    # GitHub
    ("github_pat", re.compile(r"\bghp_[A-Za-z0-9]{30,}\b")),
    ("github_oauth", re.compile(r"\bgho_[A-Za-z0-9]{30,}\b")),
    ("github_app_server", re.compile(r"\bghs_[A-Za-z0-9]{30,}\b")),
    # Slack (bot/app/…)
    ("slack_token", re.compile(r"\bxox[baprs]-[A-Za-z0-9-]{10,}\b")),
    # AWS
    ("aws_access_key_id", re.compile(r"\bAKIA[0-9A-Z]{16}\b")),
    (
        "aws_secret_key",
        re.compile(r"aws_secret_access_key\s*=\s*[A-Za-z0-9/+=]{40}\b", re.IGNORECASE),
    ),
    # Google
    ("google_api_key", re.compile(r"\bAIza[0-9A-Za-z\-_]{35}\b")),
    ("google_oauth", re.compile(r"\bya29\.[0-9A-Za-z\-_]+")),
    # JWT — три base64-like секции через точки, длина > 20 чтобы не ловить
    # короткие "a.b.c" случаи.
    ("jwt", re.compile(r"\beyJ[A-Za-z0-9\-_=]{10,}\.[A-Za-z0-9\-_=]{10,}\.[A-Za-z0-9\-_.+/=]{10,}\b")),
    # PEM-ключи
    (
        "pem_private_key",
        re.compile(r"-----BEGIN (?:RSA |EC |DSA |OPENSSH )?PRIVATE KEY-----"),
    ),
    # Общие пары "api_key=...", "password=..."
    (
        "api_key_pair",
        re.compile(
            r"(?i)\bapi[_\-]?key\s*[:=]\s*['\"]?[A-Za-z0-9\-_]{16,}['\"]?"
        ),
    ),
    (
        "password_pair",
        re.compile(
            r"(?i)\b(?:password|passwd|pwd)\s*[:=]\s*['\"]?\S{8,}['\"]?"
        ),
    ),
    # GitLab
    ("gitlab_pat", re.compile(r"\bglpat-[A-Za-z0-9\-_]{20,}\b")),
]


def check_pattern(text: str) -> Optional[str]:
    """Возвращает имя категории при совпадении с известным паттерном.

    Имена категорий стабильны — по ним строятся unit-тесты.
    """
    for name, pattern in KNOWN_SECRET_PATTERNS:
        if pattern.search(text):
            return name
    return None


# ---------------------------------------------------------------------------
# Уровень 2: энтропия Шеннона
# ---------------------------------------------------------------------------


ENTROPY_THRESHOLD_BITS = 4.5
ENTROPY_MIN_LEN = 20
ENTROPY_MAX_LEN = 200

# Подстроки, которые считаются "кандидатами в секрет": длинные непрерывные
# куски base64-подобных символов без пробелов, знаков препинания и
# кириллицы.
_CANDIDATE_RE = re.compile(r"[A-Za-z0-9+/=_\-]{%d,%d}" % (ENTROPY_MIN_LEN, ENTROPY_MAX_LEN))

# Минимальный словарь английских и русских слов для фильтра ложных
# срабатываний. Не полный словарь — только слова длины ≥ 4, которые часто
# встречаются в технических текстах. Если подстрока содержит ≥ 3 таких
# слов, она считается осмысленным текстом, а не секретом.
_DICTIONARY_WORDS = [
    # EN
    "agent", "agents", "build", "check", "code", "configuration", "context",
    "data", "database", "debug", "error", "example", "file", "filter",
    "function", "input", "output", "memory", "message", "module", "object",
    "package", "path", "query", "result", "record", "request", "response",
    "schema", "server", "source", "state", "store", "string", "system",
    "target", "test", "tests", "token", "true", "false", "update", "value",
    "version", "window", "worker",
    # RU (буквы a-z не встретятся, но оставим для обратной совместимости)
    "проверка", "пример", "запись", "данные", "память", "агент", "агента",
    "сервер", "система", "контекст", "процесс", "результат", "версия",
]


def _shannon_entropy(s: str) -> float:
    """Энтропия Шеннона строки в битах на символ."""
    if not s:
        return 0.0
    freq: dict[str, int] = {}
    for ch in s:
        freq[ch] = freq.get(ch, 0) + 1
    length = len(s)
    entropy = 0.0
    for count in freq.values():
        p = count / length
        entropy -= p * math.log2(p)
    return entropy


def _dictionary_words_count(s: str) -> int:
    s_lower = s.lower()
    hits = 0
    for word in _DICTIONARY_WORDS:
        if len(word) < 4:
            continue
        if word in s_lower:
            hits += 1
            if hits >= 3:
                return hits
    return hits


def check_entropy(text: str) -> Optional[str]:
    """Возвращает ``"high_entropy"`` при обнаружении длинной высоко-энтропийной подстроки.

    Иначе ``None``.
    """
    for match in _CANDIDATE_RE.finditer(text):
        candidate = match.group(0)
        if len(candidate) < ENTROPY_MIN_LEN:
            continue
        # Словарный фильтр: если в подстроке ≥ 3 осмысленных слов — не секрет.
        if _dictionary_words_count(candidate) >= 3:
            continue
        entropy = _shannon_entropy(candidate)
        if entropy >= ENTROPY_THRESHOLD_BITS:
            return "high_entropy"
    return None


# ---------------------------------------------------------------------------
# Публичный API
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class SecretCheck:
    """Результат проверки: допущено ли содержимое.

    - ``is_secret=False`` → всё ок, запись можно сохранять.
    - ``is_secret=True``  → ``reason_category`` содержит имя категории
      (одно из ``KNOWN_SECRET_PATTERNS`` или ``"high_entropy"``).
    """

    is_secret: bool
    reason_category: Optional[str] = None


def check_secret(text: str) -> SecretCheck:
    """Двухуровневая проверка на секреты.

    Сначала известные паттерны (быстрее и точнее), затем энтропия. При
    срабатывании любого из уровней возвращает ``SecretCheck(is_secret=True)``.

    Пустая строка проходит без ошибки — это не задача детектора, а задача
    валидации.
    """
    if not text:
        return SecretCheck(is_secret=False)
    cat = check_pattern(text)
    if cat is not None:
        return SecretCheck(is_secret=True, reason_category=cat)
    cat = check_entropy(text)
    if cat is not None:
        return SecretCheck(is_secret=True, reason_category=cat)
    return SecretCheck(is_secret=False)
