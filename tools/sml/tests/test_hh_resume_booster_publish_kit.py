from __future__ import annotations

import json
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
TOOLS = ROOT / "tools"
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

import hh_resume_booster_publish_kit as publish_kit


def write_rehearsal(data_dir: Path, name: str, record: dict[str, object]) -> Path:
    path = data_dir / name
    path.write_text(json.dumps(record), encoding="utf-8")
    return path


def test_parse_datetime_accepts_seven_fractional_digits() -> None:
    fallback = datetime(2026, 1, 1, tzinfo=timezone.utc)

    parsed = publish_kit.parse_datetime("2026-06-21T22:52:01.1234567+00:00", fallback)

    assert parsed == datetime(2026, 6, 21, 22, 52, 1, 123456, tzinfo=timezone.utc)


def test_latest_rehearsal_requires_matching_public_url_and_fresh_metadata(
    tmp_path: Path, monkeypatch
) -> None:
    data_path = tmp_path / "data" / "hh-booster-leads.jsonl"
    data_path.parent.mkdir()
    monkeypatch.setattr(publish_kit, "DEFAULT_DATA_PATH", data_path)
    generated_at = datetime.now(timezone.utc) - timedelta(minutes=5)
    write_rehearsal(
        data_path.parent,
        "hh-booster-day0-rehearsal-20260621-225152.json",
        {
            "publicBaseUrl": "https://eighty-boats-work.loca.lt/",
            "generatedAt": generated_at.isoformat(),
            "status": "ready_for_launch",
            "blockingFailures": [],
            "experimentStartedAt": None,
            "totalLeads": 0,
        },
    )
    write_rehearsal(
        data_path.parent,
        "hh-booster-day0-rehearsal-20260621-225153.json",
        {
            "publicBaseUrl": "https://other-temp-url.loca.lt",
            "generatedAt": datetime.now(timezone.utc).isoformat(),
            "status": "ready_for_launch",
            "blockingFailures": [],
        },
    )

    rehearsal = publish_kit.latest_rehearsal(
        "https://eighty-boats-work.loca.lt", max_age_minutes=15
    )

    assert rehearsal is not None
    assert rehearsal["ready"] is True
    assert rehearsal["status"] == "ready_for_launch"
    assert rehearsal["expires_in_minutes"] > 0
    assert rehearsal["blocking_failures"] == []
    assert rehearsal["experiment_started_at"] is None
    assert rehearsal["total_leads"] == 0


def test_latest_rehearsal_marks_old_metadata_as_stale(tmp_path: Path, monkeypatch) -> None:
    data_path = tmp_path / "data" / "hh-booster-leads.jsonl"
    data_path.parent.mkdir()
    monkeypatch.setattr(publish_kit, "DEFAULT_DATA_PATH", data_path)
    generated_at = datetime.now(timezone.utc) - timedelta(minutes=20)
    write_rehearsal(
        data_path.parent,
        "hh-booster-day0-rehearsal-20260621-220000.json",
        {
            "publicBaseUrl": "https://eighty-boats-work.loca.lt",
            "generatedAt": generated_at.isoformat(),
            "status": "ready_for_launch",
            "blockingFailures": [],
        },
    )

    rehearsal = publish_kit.latest_rehearsal(
        "https://eighty-boats-work.loca.lt", max_age_minutes=15
    )

    assert rehearsal is not None
    assert rehearsal["ready"] is False
    assert rehearsal["expires_in_minutes"] < 0


def test_latest_rehearsal_normalizes_blocking_failures(tmp_path: Path, monkeypatch) -> None:
    data_path = tmp_path / "data" / "hh-booster-leads.jsonl"
    data_path.parent.mkdir()
    monkeypatch.setattr(publish_kit, "DEFAULT_DATA_PATH", data_path)
    write_rehearsal(
        data_path.parent,
        "hh-booster-day0-rehearsal-20260621-225152.json",
        {
            "publicBaseUrl": "https://eighty-boats-work.loca.lt",
            "generatedAt": datetime.now(timezone.utc).isoformat(),
            "status": "ready_for_launch",
            "blockingFailures": "public api failed",
        },
    )

    rehearsal = publish_kit.latest_rehearsal(
        "https://eighty-boats-work.loca.lt", max_age_minutes=15
    )

    assert rehearsal is not None
    assert rehearsal["ready"] is False
    assert rehearsal["blocking_failures"] == ["public api failed"]


def test_render_rehearsal_section_only_requires_metadata_for_ephemeral_urls(
    tmp_path: Path, monkeypatch
) -> None:
    data_path = tmp_path / "data" / "hh-booster-leads.jsonl"
    data_path.parent.mkdir()
    monkeypatch.setattr(publish_kit, "DEFAULT_DATA_PATH", data_path)

    stable = publish_kit.render_rehearsal_section(
        "https://hh-booster.example.com", max_age_minutes=15
    )
    temporary = publish_kit.render_rehearsal_section(
        "https://eighty-boats-work.loca.lt", max_age_minutes=15
    )

    assert any("Stable public URL" in line for line in stable)
    assert any("No matching successful day-0 rehearsal metadata" in line for line in temporary)
    assert any("start-hh-booster-day0-rehearsal.ps1" in line for line in temporary)
