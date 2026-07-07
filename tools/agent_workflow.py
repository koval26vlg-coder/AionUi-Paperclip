from __future__ import annotations

import argparse
import json
import shutil
import sys
from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


LEVEL_ORDER = ["L1", "L2", "L3", "L4", "L5"]

DEFAULT_LEVELS: dict[str, dict[str, Any]] = {
    "L1": {
        "name": "Исследовательский отдел",
        "agent": "Antigravity CLI",
        "subagents": [
            {
                "id": "antigravity-source-verifier",
                "name": "Проверяющий фактов",
                "role": "Сверить brief, handoff, события и доступные источники перед передачей на инженерную проверку.",
                "model": {
                    "provider": "Google Antigravity",
                    "name": "Antigravity CLI AUTO",
                    "effort": "High",
                },
            },
            {
                "id": "antigravity-context-expander",
                "name": "Расширитель контекста",
                "role": "Добавить недостающие альтернативы, ограничения, зависимости и edge cases.",
                "model": {
                    "provider": "Google Antigravity",
                    "name": "Antigravity CLI AUTO",
                    "effort": "Low",
                },
            },
            {
                "id": "antigravity-noise-filter",
                "name": "Фильтр шума",
                "role": "Убрать неподтвержденные или лишние идеи, чтобы L1 не передал искажение выше.",
                "model": {
                    "provider": "Google Antigravity",
                    "name": "Antigravity CLI AUTO",
                    "effort": "Low",
                },
            },
            {
                "id": "antigravity-handoff-editor",
                "name": "Редактор L1-handoff",
                "role": "Собрать проверенный handoff с явным решением approve/revise/escalate/block.",
                "model": {
                    "provider": "Google Antigravity",
                    "name": "Antigravity CLI AUTO",
                    "effort": "Medium",
                },
            },
        ],
    },
    "L2": {
        "name": "Инженерная проверка",
        "agent": "Antigravity CLI",
        "subagents": [
            {
                "id": "antigravity-engineering-reviewer",
                "name": "Инженерный ревьюер",
                "role": "Проверить применимость L1-выводов к реальной реализации.",
                "model": {
                    "provider": "Google Antigravity",
                    "name": "Antigravity CLI AUTO",
                    "effort": "High",
                },
            },
            {
                "id": "antigravity-constraint-checker",
                "name": "Проверяющий ограничений",
                "role": "Сверить решение с brief, контрактом, risk flags, allowed_next_agents и контекстными лимитами.",
                "model": {
                    "provider": "Google Antigravity",
                    "name": "Antigravity CLI AUTO",
                    "effort": "High",
                },
            },
            {
                "id": "antigravity-edge-case-scout",
                "name": "Разведчик крайних случаев",
                "role": "Найти скрытые сценарии, неполные данные, конфликтующие требования и слабые места.",
                "model": {
                    "provider": "Google Antigravity",
                    "name": "Antigravity CLI AUTO",
                    "effort": "High",
                },
            },
            {
                "id": "antigravity-revision-gate",
                "name": "Gate ревизии",
                "role": "Решить, можно ли передавать работу на Codex L3 или нужно вернуть на доработку.",
                "model": {
                    "provider": "Google Antigravity",
                    "name": "Antigravity CLI AUTO",
                    "effort": "High",
                },
            },
        ],
    },
    "L3": {
        "name": "Декомпозиция реализации, тесты и automation",
        "agent": "Codex",
        "subagents": [
            {
                "id": "codex-implementation-decomposer",
                "name": "Декомпозитор реализации",
                "role": "Разбить задачу на исполнимые шаги, файлы, интерфейсы и критерии готовности.",
                "model": {
                    "provider": "OpenAI Codex",
                    "name": "codex-5.3",
                    "effort": "xhigh",
                },
            },
            {
                "id": "codex-test-planner",
                "name": "Планировщик тестов",
                "role": "Определить unit/smoke/integration проверки и негативные сценарии.",
                "model": {
                    "provider": "OpenAI",
                    "name": "gpt-5.5",
                    "effort": "xhigh",
                },
            },
            {
                "id": "codex-automation-builder",
                "name": "Инженер automation",
                "role": "Предложить или реализовать CLI/скрипты/мониторы для повторяемого выполнения.",
                "model": {
                    "provider": "OpenAI",
                    "name": "gpt-5.4 mini",
                    "effort": "xhigh",
                },
            },
            {
                "id": "codex-integration-checker",
                "name": "Проверяющий интеграции",
                "role": "Проверить совместимость с существующей структурой, SML, файлами памяти и политиками запуска.",
                "model": {
                    "provider": "OpenAI",
                    "name": "gpt-5.4",
                    "effort": "xhigh",
                },
            },
        ],
    },
    "L4": {
        "name": "Архитектурный синтез",
        "agent": "Codex",
        "subagents": [
            {
                "id": "codex-architecture-synthesizer",
                "name": "Архитектурный синтезатор",
                "role": "Собрать L1-L3 в целостное техническое решение без противоречий.",
                "model": {
                    "provider": "OpenAI",
                    "name": "gpt-5.5",
                    "effort": "xhigh",
                },
            },
            {
                "id": "codex-contract-auditor",
                "name": "Аудитор контракта",
                "role": "Проверить, что contract, handoff, events и итоговые выводы согласованы.",
                "model": {
                    "provider": "OpenAI",
                    "name": "gpt-5.5",
                    "effort": "xhigh",
                },
            },
            {
                "id": "codex-risk-gate",
                "name": "Risk gate",
                "role": "Отдельно оценить риски trading/long-running/secrets/external writes/destructive действий.",
                "model": {
                    "provider": "OpenAI",
                    "name": "gpt-5.5",
                    "effort": "xhigh",
                },
            },
            {
                "id": "codex-maintainability-reviewer",
                "name": "Ревьюер сопровождения",
                "role": "Оценить простоту поддержки, расширения и передачи следующему агенту.",
                "model": {
                    "provider": "OpenAI",
                    "name": "gpt-5.5",
                    "effort": "xhigh",
                },
            },
        ],
    },
    "L5": {
        "name": "Финальная инстанция для пользователя",
        "agent": "Claude Code",
        "subagents": [
            {
                "id": "claude-executive-summarizer",
                "name": "Executive summarizer",
                "role": "Сжато объяснить пользователю итог, решение и оставшиеся риски.",
                "model": {
                    "provider": "Anthropic",
                    "name": "Claude Opus 4.7 alias",
                    "effort": "xhigh",
                },
            },
            {
                "id": "claude-technical-verifier",
                "name": "Финальный техпроверяющий",
                "role": "Независимо проверить техническую связность L1-L4 перед финальным отчетом.",
                "model": {
                    "provider": "Anthropic",
                    "name": "Claude Haiku 4.5 alias",
                    "effort": "xhigh",
                },
            },
            {
                "id": "claude-anti-distortion-auditor",
                "name": "Аудитор против искажения",
                "role": "Сверить final-report с brief, handoff и events, чтобы не было испорченного телефона.",
                "model": {
                    "provider": "Anthropic",
                    "name": "Claude Sonnet 4.6 alias",
                    "effort": "xhigh",
                },
            },
            {
                "id": "claude-final-decision-writer",
                "name": "Автор заключения",
                "role": "Сформировать final-report.md для пользователя с понятным решением approve/revise/escalate/block.",
                "model": {
                    "provider": "Anthropic",
                    "name": "Claude Opus 4.8 alias",
                    "effort": "xhigh",
                },
            },
        ],
    },
}


def make_gemini_vertex_levels() -> dict[str, dict[str, Any]]:
    levels = deepcopy(DEFAULT_LEVELS)
    levels["L1"]["agent"] = "Gemini Vertex"
    levels["L1"]["subagents"] = [
        {
            "id": "gemini-source-verifier",
            "name": "Проверяющий источников",
            "role": "Сверить brief, handoff, события и доступные источники перед передачей на инженерную проверку.",
            "model": {
                "provider": "Google Vertex AI",
                "name": "gemini-2.5-flash via Vertex AI",
                "effort": "High",
            },
        },
        {
            "id": "gemini-context-expander",
            "name": "Расширитель контекста",
            "role": "Добавить недостающие альтернативы, ограничения, зависимости и edge cases.",
            "model": {
                "provider": "Google Vertex AI",
                "name": "gemini-2.5-flash via Vertex AI",
                "effort": "Low",
            },
        },
        {
            "id": "gemini-noise-filter",
            "name": "Фильтр шума",
            "role": "Убрать неподтвержденные или лишние идеи, чтобы L1 не передал искажение выше.",
            "model": {
                "provider": "Google Vertex AI",
                "name": "gemini-2.5-flash via Vertex AI",
                "effort": "Low",
            },
        },
        {
            "id": "gemini-handoff-editor",
            "name": "Редактор L1-handoff",
            "role": "Собрать проверенный handoff с явным решением approve/revise/escalate/block.",
            "model": {
                "provider": "Google Vertex AI",
                "name": "gemini-2.5-flash via Vertex AI",
                "effort": "Medium",
            },
        },
    ]
    levels["L2"]["agent"] = "Gemini Vertex"
    levels["L2"]["subagents"] = [
        {
            "id": "gemini-engineering-reviewer",
            "name": "Инженерный ревьюер",
            "role": "Проверить применимость L1-выводов к реальной реализации.",
            "model": {
                "provider": "Google Vertex AI",
                "name": "gemini-2.5-flash via Vertex AI",
                "effort": "High",
            },
        },
        {
            "id": "gemini-constraint-checker",
            "name": "Проверяющий ограничений",
            "role": "Сверить решение с brief, контрактом, risk flags, allowed_next_agents и контекстными лимитами.",
            "model": {
                "provider": "Google Vertex AI",
                "name": "gemini-2.5-flash via Vertex AI",
                "effort": "High",
            },
        },
        {
            "id": "gemini-edge-case-scout",
            "name": "Разведчик крайних случаев",
            "role": "Найти скрытые сценарии, неполные данные, конфликтующие требования и слабые места.",
            "model": {
                "provider": "Google Vertex AI",
                "name": "gemini-2.5-flash via Vertex AI",
                "effort": "High",
            },
        },
        {
            "id": "gemini-revision-gate",
            "name": "Gate ревизии",
            "role": "Решить, можно ли передавать работу на Codex L3 или нужно вернуть на доработку.",
            "model": {
                "provider": "Google Vertex AI",
                "name": "gemini-2.5-flash via Vertex AI",
                "effort": "High",
            },
        },
    ]
    return levels


def make_grok_gemini_levels() -> dict[str, dict[str, Any]]:
    levels = make_gemini_vertex_levels()
    levels["L1"]["agent"] = "Grok Build"
    levels["L1"]["subagents"] = [
        {
            "id": "grok-memory-bootstrapper",
            "name": "Загрузчик общей памяти",
            "role": "Подтянуть SML-контекст, AGENTS.md, context-pack, decisions, tasks и последние agent-log до анализа задачи.",
            "model": {
                "provider": "xAI Grok Build",
                "name": "Grok Build 0.2.87",
                "effort": "High",
            },
        },
        {
            "id": "grok-problem-framer",
            "name": "Формулировщик задачи",
            "role": "Разложить исходный brief на цель, ограничения, скрытые предположения, критерии готовности и вопросы без преждевременной реализации.",
            "model": {
                "provider": "xAI Grok Build",
                "name": "Grok Build 0.2.87",
                "effort": "Medium",
            },
        },
        {
            "id": "grok-source-scout",
            "name": "Разведчик контекста и источников",
            "role": "Найти связанные документы, прошлые решения, похожие workflow и возможные внешние факты, которые нужно проверить на L2.",
            "model": {
                "provider": "xAI Grok Build",
                "name": "Grok Build 0.2.87",
                "effort": "High",
            },
        },
            {
                "id": "grok-handoff-editor",
                "name": "Редактор первичного handoff",
                "role": "Собрать аккуратный L1-handoff для L2 с явным решением approve/revise/escalate/block и списком непроверенных мест.",
                "model": {
                    "provider": "xAI Grok Build",
                    "name": "Grok Build 0.2.87",
                "effort": "Medium",
            },
        },
    ]
    return levels


def make_grok_antigravity_levels() -> dict[str, dict[str, Any]]:
    levels = deepcopy(DEFAULT_LEVELS)
    levels["L1"] = deepcopy(make_grok_gemini_levels()["L1"])
    return levels


WORKFLOW_PROFILES: dict[str, dict[str, dict[str, Any]]] = {
    "antigravity": DEFAULT_LEVELS,
    "gemini-vertex": make_gemini_vertex_levels(),
    "grok-antigravity": make_grok_antigravity_levels(),
    "grok-gemini": make_grok_gemini_levels(),
}
DEFAULT_WORKFLOW_PROFILE = "grok-antigravity"

REQUIRED_HANDOFF_HEADINGS = [
    "## Что было сделано",
    "## На чем основан вывод",
    "## Что получилось хорошо",
    "## Что требует доработки",
    "## Какие есть риски",
    "## Что нельзя потерять/исказить дальше",
    "## Решение",
]

RISK_FLAGS = [
    "trading",
    "writes_external_system",
    "long_running",
    "uses_secrets",
    "destructive",
]

REVIEW_ONLY_MUTATION_AGENTS = {"Antigravity CLI", "Gemini Vertex", "Grok Build"}
TRUSTED_MUTATION_EXECUTORS = {"Codex", "Claude Code"}


class WorkflowError(Exception):
    def __init__(self, message: str, code: int = 2) -> None:
        super().__init__(message)
        self.code = code


def now_iso() -> str:
    return datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")


def safe_slug(text: str) -> str:
    slug = "".join(ch.lower() if ch.isalnum() else "-" for ch in text).strip("-")
    while "--" in slug:
        slug = slug.replace("--", "-")
    return slug[:70] or "workflow"


def workflow_dir(args: argparse.Namespace) -> Path:
    return Path(args.root) / args.workflow_id


def contract_path(wf_dir: Path) -> Path:
    return wf_dir / "contract.json"


def load_contract(wf_dir: Path) -> dict[str, Any]:
    path = contract_path(wf_dir)
    if not path.exists():
        raise WorkflowError(f"contract not found: {path}", 1)
    return json.loads(path.read_text(encoding="utf-8"))


def save_contract(wf_dir: Path, contract: dict[str, Any]) -> None:
    contract["updated_at"] = now_iso()
    contract_path(wf_dir).write_text(
        json.dumps(contract, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def append_event(wf_dir: Path, event: dict[str, Any]) -> None:
    with (wf_dir / "events.jsonl").open("a", encoding="utf-8") as fh:
        fh.write(json.dumps({"time": now_iso(), **event}, ensure_ascii=False) + "\n")


def require_allowed(contract: dict[str, Any], agent: str) -> None:
    allowed = contract.get("allowed_next_agents", [])
    if agent not in allowed:
        raise WorkflowError(
            f"agent {agent!r} is not allowed; allowed_next_agents={allowed}"
        )


def mutation_executor(args: argparse.Namespace) -> str:
    return str(getattr(args, "executor", None) or args.agent)


def require_mutation_executor(args: argparse.Namespace) -> str:
    executor = mutation_executor(args)
    if args.agent in REVIEW_ONLY_MUTATION_AGENTS and executor == args.agent:
        raise WorkflowError(
            f"{args.agent} is review-only for workflow state mutations; "
            "capture its handoff via isolated review runner and mutate with "
            "--executor Codex"
        )
    if args.agent in REVIEW_ONLY_MUTATION_AGENTS and executor not in TRUSTED_MUTATION_EXECUTORS:
        raise WorkflowError(
            f"{args.agent} workflow mutation requires trusted executor; "
            f"got {executor!r}"
        )
    return executor


def current_level(contract: dict[str, Any]) -> str:
    return str(contract["current_level"])


def current_subrole_id(contract: dict[str, Any]) -> str | None:
    value = contract.get("current_subrole")
    return str(value) if value else None


def next_level(level: str) -> str | None:
    index = LEVEL_ORDER.index(level)
    if index + 1 >= len(LEVEL_ORDER):
        return None
    return LEVEL_ORDER[index + 1]


def level_agent(contract: dict[str, Any], level: str) -> str:
    return str(contract["levels"][level]["agent"])


def level_subroles(contract: dict[str, Any], level: str) -> list[dict[str, Any]]:
    return list(contract["levels"][level].get("subroles") or [])


def find_subrole(contract: dict[str, Any], level: str, subrole_id: str) -> dict[str, Any]:
    for subrole in level_subroles(contract, level):
        if subrole.get("id") == subrole_id:
            return subrole
    raise WorkflowError(f"subrole {subrole_id!r} not found in {level}")


def assignment_for(
    contract: dict[str, Any], level: str, subrole_id: str | None = None
) -> dict[str, Any]:
    if subrole_id:
        subrole = find_subrole(contract, level, subrole_id)
        return {
            "level": level,
            "subrole_id": subrole_id,
            "data": subrole,
            "label": subrole_id,
            "agent": str(subrole["agent"]),
        }
    data = contract["levels"][level]
    return {
        "level": level,
        "subrole_id": None,
        "data": data,
        "label": level,
        "agent": str(data["agent"]),
    }


def current_assignment(contract: dict[str, Any]) -> dict[str, Any]:
    return assignment_for(contract, current_level(contract), current_subrole_id(contract))


def first_assignment(contract: dict[str, Any], level: str) -> dict[str, Any]:
    subroles = level_subroles(contract, level)
    if subroles:
        return assignment_for(contract, level, str(subroles[0]["id"]))
    return assignment_for(contract, level)


def next_assignment(contract: dict[str, Any]) -> dict[str, Any] | None:
    level = current_level(contract)
    subrole_id = current_subrole_id(contract)
    subroles = level_subroles(contract, level)
    if subrole_id and subroles:
        ids = [str(subrole["id"]) for subrole in subroles]
        index = ids.index(subrole_id)
        if index + 1 < len(ids):
            return assignment_for(contract, level, ids[index + 1])
    target = next_level(level)
    if target is None:
        return None
    return first_assignment(contract, target)


def assignment_dir(wf_dir: Path, assignment: dict[str, Any]) -> Path:
    path = wf_dir / "levels" / assignment["level"]
    if assignment.get("subrole_id"):
        path = path / str(assignment["subrole_id"])
    path.mkdir(parents=True, exist_ok=True)
    return path


def set_current_assignment(contract: dict[str, Any], assignment: dict[str, Any]) -> None:
    contract["current_level"] = assignment["level"]
    if assignment.get("subrole_id"):
        contract["current_subrole"] = assignment["subrole_id"]
    else:
        contract.pop("current_subrole", None)


def mark_related_blockers_resolved(contract: dict[str, Any], assignment: dict[str, Any]) -> None:
    for blocker in contract.get("blockers", []):
        if blocker.get("level") != assignment["level"]:
            continue
        blocker_assignment = blocker.get("assignment")
        if blocker_assignment and blocker_assignment != assignment["label"]:
            continue
        blocker["resolved"] = True
        blocker["resolved_at"] = now_iso()


def validate_handoff(text: str) -> None:
    missing = [heading for heading in REQUIRED_HANDOFF_HEADINGS if heading not in text]
    if missing:
        raise WorkflowError(
            "handoff is missing required headings: " + ", ".join(missing)
        )


def read_required_file(path: str | None, label: str) -> str:
    if not path:
        raise WorkflowError(f"{label} is required")
    file_path = Path(path)
    if not file_path.exists():
        raise WorkflowError(f"{label} not found: {file_path}")
    return file_path.read_text(encoding="utf-8")


def copy_text_artifact(
    wf_dir: Path, assignment: dict[str, Any], source: str, name: str
) -> str:
    src = Path(source)
    if not src.exists():
        raise WorkflowError(f"artifact not found: {src}")
    dst = assignment_dir(wf_dir, assignment) / name
    copy_file_if_different(src, dst)
    return str(dst.relative_to(wf_dir)).replace("\\", "/")


def same_path(left: Path, right: Path) -> bool:
    return left.resolve() == right.resolve()


def copy_file_if_different(src: Path, dst: Path) -> None:
    dst.parent.mkdir(parents=True, exist_ok=True)
    if dst.exists() and same_path(src, dst):
        return
    shutil.copyfile(src, dst)


def build_levels(profile: str = DEFAULT_WORKFLOW_PROFILE) -> dict[str, dict[str, Any]]:
    if profile not in WORKFLOW_PROFILES:
        raise WorkflowError(
            f"unknown workflow profile {profile!r}; available={sorted(WORKFLOW_PROFILES)}"
        )
    template = WORKFLOW_PROFILES[profile]
    levels: dict[str, dict[str, Any]] = {}
    for key, data in template.items():
        level = {
            "name": data["name"],
            "agent": data["agent"],
            "subagents": deepcopy(data.get("subagents", [])),
            "status": "pending",
            "handoff": None,
            "approved_by": None,
            "submitted_at": None,
            "approved_at": None,
        }
        if data.get("subroles"):
            level["subroles"] = [
                {
                    "id": subrole["id"],
                    "name": subrole["name"],
                    "agent": subrole["agent"],
                    "mode": subrole.get("mode"),
                    "purpose": subrole.get("purpose"),
                    "subagents": deepcopy(subrole.get("subagents", [])),
                    "status": "pending",
                    "handoff": None,
                    "approved_by": None,
                    "submitted_at": None,
                    "approved_at": None,
                }
                for subrole in data["subroles"]
            ]
        levels[key] = level
    return levels


def risk_flags_from_args(args: argparse.Namespace) -> dict[str, bool]:
    return {flag: bool(getattr(args, "risk_" + flag)) for flag in RISK_FLAGS}


def risk_gate_for(flags: dict[str, bool]) -> dict[str, Any]:
    required = any(flags.values())
    return {
        "required": required,
        "status": "pending" if required else "skipped",
        "agent": "Claude Code" if required else None,
        "summary": None,
        "approved_at": None,
        "approved_by": None,
    }


def model_label(subagent: dict[str, Any]) -> str:
    model = subagent.get("model")
    if not model:
        return "model=unspecified"
    parts = [str(model.get("name") or "unspecified")]
    if model.get("effort"):
        parts.append(str(model["effort"]))
    if model.get("mode"):
        parts.append(str(model["mode"]))
    return " / ".join(parts)


def unresolved_revision_or_block(contract: dict[str, Any]) -> bool:
    if any(not blocker.get("resolved") for blocker in contract.get("blockers", [])):
        return True
    for level in contract["levels"].values():
        if level.get("status") in {"revision_requested", "blocked"}:
            return True
        for subrole in level.get("subroles") or []:
            if subrole.get("status") in {"revision_requested", "blocked"}:
                return True
    return False


def cmd_new(args: argparse.Namespace) -> int:
    root = Path(args.root)
    root.mkdir(parents=True, exist_ok=True)
    workflow_id = (
        f"{datetime.now().strftime('%Y-%m-%d-%H%M%S-%f')}-{safe_slug(args.title)}"
    )
    wf_dir = root / workflow_id
    wf_dir.mkdir(parents=True)
    flags = risk_flags_from_args(args)
    levels = build_levels(args.profile)
    initial = first_assignment({"levels": levels, "current_level": "L1"}, "L1")
    contract = {
        "workflow_id": workflow_id,
        "title": args.title,
        "workflow_profile": args.profile,
        "state": "planned",
        "created_at": now_iso(),
        "updated_at": now_iso(),
        "created_by": args.created_by,
        "principal": args.principal,
        "current_level": "L1",
        "current_subrole": initial.get("subrole_id"),
        "allowed_next_agents": [initial["agent"]],
        "levels": levels,
        "risk_flags": flags,
        "risk_gate": risk_gate_for(flags),
        "blockers": [],
        "last_event": "workflow_created",
        "last_handoff": None,
        "final_report": None,
    }
    save_contract(wf_dir, contract)
    brief = args.brief or f"# {args.title}\n\nИсходная постановка не указана.\n"
    (wf_dir / "brief.md").write_text(brief.rstrip() + "\n", encoding="utf-8")
    (wf_dir / "handoff.md").write_text("# Handoff\n\nПока нет handoff.\n", encoding="utf-8")
    (wf_dir / "events.jsonl").write_text("", encoding="utf-8")
    append_event(
        wf_dir,
        {
            "event": "workflow_created",
            "agent": args.created_by,
            "workflow_profile": args.profile,
        },
    )
    print(workflow_id)
    return 0


def cmd_claim(args: argparse.Namespace) -> int:
    wf_dir = workflow_dir(args)
    contract = load_contract(wf_dir)
    require_allowed(contract, args.agent)
    executor = require_mutation_executor(args)
    assignment = current_assignment(contract)
    if assignment["data"]["status"] not in {"pending", "revision_requested"}:
        raise WorkflowError(f"{assignment['label']} is not claimable")
    assignment["data"]["status"] = "in_progress"
    contract["levels"][assignment["level"]]["status"] = "in_progress"
    contract["state"] = "in_progress"
    contract["last_event"] = "level_claimed"
    save_contract(wf_dir, contract)
    append_event(
        wf_dir,
        {
            "event": "level_claimed",
            "agent": args.agent,
            "executor": executor,
            "level": assignment["level"],
            "assignment": assignment["label"],
        },
    )
    print(f"{assignment['label']} in_progress")
    return 0


def cmd_submit_work(args: argparse.Namespace) -> int:
    wf_dir = workflow_dir(args)
    contract = load_contract(wf_dir)
    require_allowed(contract, args.agent)
    executor = require_mutation_executor(args)
    assignment = current_assignment(contract)
    level_data = contract["levels"][assignment["level"]]
    if assignment["data"]["status"] != "in_progress":
        raise WorkflowError(
            f"{assignment['label']} must be in_progress before submit-work"
        )
    text = read_required_file(args.handoff_file, "handoff file")
    validate_handoff(text)
    rel_handoff = copy_text_artifact(wf_dir, assignment, args.handoff_file, "handoff.md")
    copy_file_if_different(Path(args.handoff_file), wf_dir / "handoff.md")
    assignment["data"]["status"] = "submitted"
    assignment["data"]["handoff"] = rel_handoff
    assignment["data"]["submitted_at"] = now_iso()
    mark_related_blockers_resolved(contract, assignment)
    if not next_assignment(contract) or next_assignment(contract)["level"] != assignment["level"]:
        level_data["status"] = "submitted"
        level_data["handoff"] = rel_handoff
        level_data["submitted_at"] = assignment["data"]["submitted_at"]
    contract["last_handoff"] = rel_handoff
    target = next_assignment(contract)
    if target is None:
        contract["state"] = "ready_for_final"
        contract["allowed_next_agents"] = [assignment["agent"]]
    elif target["level"] == "L5":
        contract["state"] = "ready_for_final"
        contract["allowed_next_agents"] = [target["agent"]]
    else:
        contract["state"] = "waiting_for_approval"
        contract["allowed_next_agents"] = [target["agent"]]
    contract["last_event"] = "level_submitted"
    save_contract(wf_dir, contract)
    append_event(
        wf_dir,
        {
            "event": "level_submitted",
            "agent": args.agent,
            "executor": executor,
            "level": assignment["level"],
            "assignment": assignment["label"],
        },
    )
    print(f"{assignment['label']} submitted")
    return 0


def cmd_approve_level(args: argparse.Namespace) -> int:
    wf_dir = workflow_dir(args)
    contract = load_contract(wf_dir)
    require_allowed(contract, args.agent)
    executor = require_mutation_executor(args)
    assignment = current_assignment(contract)
    target = next_assignment(contract)
    if target is None:
        raise WorkflowError("L5 cannot be approved higher; use finalize")
    if target["level"] == "L5":
        raise WorkflowError("use finalize for L5 instead of approve-level")
    if assignment["data"]["status"] != "submitted" or not assignment["data"].get("handoff"):
        raise WorkflowError(
            f"{assignment['label']} requires submitted handoff before approve-level"
        )
    assignment["data"]["status"] = "approved"
    assignment["data"]["approved_by"] = args.agent
    assignment["data"]["approved_at"] = now_iso()
    mark_related_blockers_resolved(contract, assignment)
    if target["level"] == assignment["level"]:
        contract["levels"][assignment["level"]]["status"] = "in_progress"
    else:
        level_data = contract["levels"][assignment["level"]]
        level_data["status"] = "approved"
        level_data["approved_by"] = args.agent
        level_data["approved_at"] = assignment["data"]["approved_at"]
    set_current_assignment(contract, target)
    target["data"]["status"] = "pending"
    contract["state"] = "planned"
    contract["allowed_next_agents"] = [target["agent"]]
    contract["last_event"] = "level_approved"
    save_contract(wf_dir, contract)
    append_event(
        wf_dir,
        {
            "event": "level_approved",
            "agent": args.agent,
            "executor": executor,
            "level": assignment["level"],
            "assignment": assignment["label"],
            "next_level": target["level"],
            "next_assignment": target["label"],
        },
    )
    print(f"{assignment['label']} approved; next={target['label']}")
    return 0


def cmd_request_revision(args: argparse.Namespace) -> int:
    wf_dir = workflow_dir(args)
    contract = load_contract(wf_dir)
    require_allowed(contract, args.agent)
    executor = require_mutation_executor(args)
    assignment = current_assignment(contract)
    if assignment["data"]["status"] != "submitted":
        raise WorkflowError(
            f"{assignment['label']} must be submitted before request-revision"
        )
    if args.disagreement_file:
        rel_disagreement = copy_text_artifact(
            wf_dir, assignment, args.disagreement_file, "disagreement.md"
        )
        assignment["data"]["disagreement"] = rel_disagreement
    assignment["data"]["status"] = "revision_requested"
    contract["levels"][assignment["level"]]["status"] = "revision_requested"
    contract["state"] = "revision_requested"
    contract["allowed_next_agents"] = [assignment["agent"]]
    contract["blockers"].append(
        {
            "level": assignment["level"],
            "assignment": assignment["label"],
            "reason": args.reason,
            "requested_by": args.agent,
            "time": now_iso(),
            "resolved": False,
        }
    )
    contract["last_event"] = "revision_requested"
    save_contract(wf_dir, contract)
    append_event(
        wf_dir,
        {
            "event": "revision_requested",
            "agent": args.agent,
            "executor": executor,
            "level": assignment["level"],
            "assignment": assignment["label"],
            "reason": args.reason,
        },
    )
    print(f"{assignment['label']} revision_requested")
    return 0


def cmd_escalate(args: argparse.Namespace) -> int:
    wf_dir = workflow_dir(args)
    contract = load_contract(wf_dir)
    require_allowed(contract, args.agent)
    executor = require_mutation_executor(args)
    assignment = current_assignment(contract)
    target_assignment = next_assignment(contract)
    if target_assignment is None:
        raise WorkflowError("L5 cannot be escalated higher; use finalize")
    if target_assignment["level"] == assignment["level"]:
        raise WorkflowError(
            "finish remaining subroles inside the current level before escalation"
        )
    target = args.target_level or target_assignment["level"]
    if target not in LEVEL_ORDER:
        raise WorkflowError(f"unknown target level: {target}")
    if LEVEL_ORDER.index(target) != LEVEL_ORDER.index(assignment["level"]) + 1:
        raise WorkflowError("escalation can move only one level higher; direct jumps are blocked")
    if target == "L5":
        raise WorkflowError("direct escalation to L5 is blocked; use finalize after L4")
    if assignment["data"]["status"] != "submitted":
        raise WorkflowError(f"{assignment['label']} must submit handoff before escalation")
    assignment["data"]["status"] = "approved"
    assignment["data"]["approved_by"] = args.agent
    assignment["data"]["approved_at"] = now_iso()
    level_data = contract["levels"][assignment["level"]]
    level_data["status"] = "approved"
    level_data["approved_by"] = args.agent
    level_data["approved_at"] = assignment["data"]["approved_at"]
    mark_related_blockers_resolved(contract, assignment)
    set_current_assignment(contract, target_assignment)
    target_assignment["data"]["status"] = "pending"
    contract["state"] = "planned"
    contract["allowed_next_agents"] = [target_assignment["agent"]]
    contract["last_event"] = "escalated"
    save_contract(wf_dir, contract)
    append_event(
        wf_dir,
        {
            "event": "escalated",
            "agent": args.agent,
            "executor": executor,
            "level": assignment["level"],
            "assignment": assignment["label"],
            "target_level": target,
            "reason": args.reason,
        },
    )
    print(f"{assignment['label']} escalated to {target_assignment['label']}")
    return 0


def cmd_approve_risk(args: argparse.Namespace) -> int:
    wf_dir = workflow_dir(args)
    contract = load_contract(wf_dir)
    executor = require_mutation_executor(args)
    gate = contract["risk_gate"]
    if not gate.get("required"):
        raise WorkflowError("risk gate is not required")
    expected = gate.get("agent")
    if expected and args.agent != expected:
        raise WorkflowError(f"risk review requires agent {expected!r}")
    gate["status"] = "passed"
    gate["summary"] = args.summary
    gate["approved_at"] = now_iso()
    gate["approved_by"] = args.agent
    contract["last_event"] = "risk_approved"
    save_contract(wf_dir, contract)
    append_event(
        wf_dir,
        {
            "event": "risk_approved",
            "agent": args.agent,
            "executor": executor,
            "summary": args.summary,
        },
    )
    print("risk_gate passed")
    return 0


def collect_handoffs(contract: dict[str, Any]) -> list[str]:
    lines: list[str] = []
    for level in LEVEL_ORDER:
        data = contract["levels"][level]
        lines.append(
            f"- {level} {data['name']}: status={data['status']}, "
            f"agent={data['agent']}, handoff={data.get('handoff')}"
        )
        for subagent in data.get("subagents") or []:
            lines.append(
                f"  - subagent {subagent['id']}: {subagent['name']} - "
                f"{subagent['role']} [{model_label(subagent)}]"
            )
        for subrole in data.get("subroles") or []:
            lines.append(
                f"  - {subrole['id']} {subrole['name']}: "
                f"status={subrole['status']}, agent={subrole['agent']}, "
                f"mode={subrole.get('mode')}, handoff={subrole.get('handoff')}"
            )
            for subagent in subrole.get("subagents") or []:
                lines.append(
                    f"    - subagent {subagent['id']}: {subagent['name']} - "
                    f"{subagent['role']} [{model_label(subagent)}]"
                )
    return lines


def cmd_finalize(args: argparse.Namespace) -> int:
    wf_dir = workflow_dir(args)
    contract = load_contract(wf_dir)
    require_allowed(contract, args.agent)
    executor = require_mutation_executor(args)
    if current_level(contract) == "L4" and contract["levels"]["L4"].get("status") == "submitted":
        mark_related_blockers_resolved(
            contract,
            {"level": "L4", "label": "L4", "data": contract["levels"]["L4"]},
        )
    if unresolved_revision_or_block(contract):
        raise WorkflowError("finalize is blocked by unresolved revision or blocker")
    risk_gate = contract["risk_gate"]
    if risk_gate.get("required") and risk_gate.get("status") != "passed":
        raise WorkflowError("finalize is blocked until risk_gate is passed")
    level = current_level(contract)
    if level != "L4" or contract["levels"]["L4"]["status"] != "submitted":
        raise WorkflowError("finalize requires submitted L4 handoff")
    summary = read_required_file(args.report_file, "final report file")
    l4 = contract["levels"]["L4"]
    l4["status"] = "approved"
    l4["approved_by"] = args.agent
    l4["approved_at"] = now_iso()
    contract["levels"]["L5"]["status"] = "approved"
    contract["levels"]["L5"]["handoff"] = "final-report.md"
    contract["levels"]["L5"]["approved_by"] = args.agent
    contract["levels"]["L5"]["approved_at"] = now_iso()
    contract["current_level"] = "L5"
    contract["state"] = "done"
    contract["allowed_next_agents"] = []
    contract["final_report"] = "final-report.md"
    contract["last_event"] = "finalized"
    report_path = wf_dir / "final-report.md"
    report_path.write_text(
        summary.rstrip()
        + "\n\n## История прохождения уровней\n\n"
        + "\n".join(collect_handoffs(contract))
        + "\n",
        encoding="utf-8",
    )
    save_contract(wf_dir, contract)
    append_event(wf_dir, {"event": "finalized", "agent": args.agent, "executor": executor})
    print("done")
    return 0


def cmd_status(args: argparse.Namespace) -> int:
    wf_dir = workflow_dir(args)
    contract = load_contract(wf_dir)
    if args.json:
        print(json.dumps(contract, ensure_ascii=False, indent=2))
        return 0
    print(f"workflow: {contract['workflow_id']}")
    print(f"title: {contract['title']}")
    if contract.get("workflow_profile"):
        print(f"workflow_profile: {contract['workflow_profile']}")
    print(f"state: {contract['state']}")
    print(f"current_level: {contract['current_level']}")
    if contract.get("current_subrole"):
        print(f"current_subrole: {contract['current_subrole']}")
    print(f"allowed_next_agents: {', '.join(contract.get('allowed_next_agents', []))}")
    assignment = current_assignment(contract)
    subagents = assignment["data"].get("subagents") or []
    if subagents:
        print("subagents:")
        for subagent in subagents:
            print(f"- {subagent['id']}: {subagent['name']} [{model_label(subagent)}]")
    print(f"last_event: {contract.get('last_event')}")
    if contract.get("blockers"):
        print("blockers:")
        for blocker in contract["blockers"]:
            print(f"- {blocker['level']}: {blocker['reason']}")
    return 0


def add_new_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--title", required=True)
    parser.add_argument("--brief")
    parser.add_argument("--created-by", default="Codex")
    parser.add_argument("--principal", default="User")
    parser.add_argument(
        "--profile",
        choices=sorted(WORKFLOW_PROFILES),
        default=DEFAULT_WORKFLOW_PROFILE,
        help=(
            "Workflow runtime profile for L1/L2. Default uses Grok Build L1 "
            "and Antigravity CLI L2; use antigravity, gemini-vertex, or "
            "grok-gemini as explicit fallback/legacy profiles."
        ),
    )
    for flag in RISK_FLAGS:
        parser.add_argument(f"--risk-{flag}", action="store_true")


def add_executor_arg(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--executor",
        help=(
            "Trusted local executor that mutates workflow state on behalf of a "
            "review-only agent, for example --executor Codex."
        ),
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Hierarchical agent workflow CLI")
    parser.add_argument("--root", default="docs/agent-workflows")
    sub = parser.add_subparsers(dest="command", required=True)

    new = sub.add_parser("new")
    add_new_args(new)
    new.set_defaults(func=cmd_new)

    claim = sub.add_parser("claim")
    claim.add_argument("workflow_id")
    claim.add_argument("--agent", required=True)
    add_executor_arg(claim)
    claim.set_defaults(func=cmd_claim)

    submit = sub.add_parser("submit-work")
    submit.add_argument("workflow_id")
    submit.add_argument("--agent", required=True)
    submit.add_argument("--handoff-file", required=True)
    add_executor_arg(submit)
    submit.set_defaults(func=cmd_submit_work)

    approve = sub.add_parser("approve-level")
    approve.add_argument("workflow_id")
    approve.add_argument("--agent", required=True)
    add_executor_arg(approve)
    approve.set_defaults(func=cmd_approve_level)

    revise = sub.add_parser("request-revision")
    revise.add_argument("workflow_id")
    revise.add_argument("--agent", required=True)
    revise.add_argument("--reason", required=True)
    revise.add_argument("--disagreement-file")
    add_executor_arg(revise)
    revise.set_defaults(func=cmd_request_revision)

    escalate = sub.add_parser("escalate")
    escalate.add_argument("workflow_id")
    escalate.add_argument("--agent", required=True)
    escalate.add_argument("--target-level")
    escalate.add_argument("--reason", required=True)
    add_executor_arg(escalate)
    escalate.set_defaults(func=cmd_escalate)

    risk = sub.add_parser("approve-risk")
    risk.add_argument("workflow_id")
    risk.add_argument("--agent", required=True)
    risk.add_argument("--summary", required=True)
    add_executor_arg(risk)
    risk.set_defaults(func=cmd_approve_risk)

    finalize = sub.add_parser("finalize")
    finalize.add_argument("workflow_id")
    finalize.add_argument("--agent", required=True)
    finalize.add_argument("--report-file", required=True)
    add_executor_arg(finalize)
    finalize.set_defaults(func=cmd_finalize)

    status = sub.add_parser("status")
    status.add_argument("workflow_id")
    status.add_argument("--json", action="store_true")
    status.set_defaults(func=cmd_status)

    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        return int(args.func(args))
    except WorkflowError as exc:
        print(str(exc), file=sys.stderr)
        return exc.code


if __name__ == "__main__":
    raise SystemExit(main())

