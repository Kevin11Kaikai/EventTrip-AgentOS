import yaml

from eventtrip import source_intake_cli
from eventtrip.source_evidence import load_source_evidence
from eventtrip.source_intake import (
    add_source_candidate,
    preview_source_candidate,
    validate_field_attribution_coverage,
    validate_source_registry,
    write_source_registry,
)


def test_current_source_registry_passes_strict_intake_validation():
    assert validate_source_registry(match_id="portugal_dr_congo") == []


def test_preview_source_candidate_reports_groups(tmp_path):
    candidate = _write_candidate(tmp_path / "candidate.yaml", source_id="new_ticket_safety_source")

    result = preview_source_candidate(candidate)

    assert result["status"] == "valid"
    assert result["source_id"] == "new_ticket_safety_source"
    assert "ticket_safety" in result["citation_groups"]
    assert result["field_attribution_status"] == "checked"


def test_preview_duplicate_source_id_fails(tmp_path):
    candidate = _write_candidate(tmp_path / "candidate.yaml", source_id="fifa_tickets")

    result = preview_source_candidate(candidate)

    assert result["status"] == "invalid"
    assert any("duplicate source_id" in error for error in result["errors"])


def test_preview_unknown_tag_fails(tmp_path):
    candidate = _write_candidate(
        tmp_path / "candidate.yaml",
        source_id="bad_tag_source",
        evidence_tags=["not_a_known_tag"],
    )

    result = preview_source_candidate(candidate)

    assert result["status"] == "invalid"
    assert any("unknown evidence tag" in error for error in result["errors"])


def test_add_source_candidate_dry_run_does_not_modify_registry(tmp_path):
    registry = tmp_path / "source_evidence.yaml"
    write_source_registry(registry, load_source_evidence())
    before = registry.read_text(encoding="utf-8")
    candidate = _write_candidate(tmp_path / "candidate.yaml", source_id="dry_run_source")

    result = add_source_candidate(candidate, registry_path=registry)

    assert result["status"] == "dry_run"
    assert result["saved"] is False
    assert registry.read_text(encoding="utf-8") == before


def test_add_source_candidate_save_writes_temp_registry(tmp_path):
    registry = tmp_path / "source_evidence.yaml"
    write_source_registry(registry, load_source_evidence())
    candidate = _write_candidate(tmp_path / "candidate.yaml", source_id="saved_source")

    result = add_source_candidate(candidate, registry_path=registry, save=True)
    updated = load_source_evidence(registry)
    source_ids = {
        source["source_id"]
        for source in updated["portugal_dr_congo"]["sources"]
    }

    assert result["status"] == "saved"
    assert result["saved"] is True
    assert "saved_source" in source_ids


def test_field_attribution_coverage_flags_missing_source_backed_ids():
    errors = validate_field_attribution_coverage({"match_id": "portugal_dr_congo", "sources": []})

    assert any("match_name is source_backed but has no source_ids" in error for error in errors)
    assert any("official_ticket_path is source_backed but has no source_ids" in error for error in errors)


def test_source_intake_cli_validate_passes(capsys):
    code = source_intake_cli.main(["validate"])
    output = capsys.readouterr().out

    assert code == 0
    assert "Source registry validation passed" in output
    assert "field-level attribution" in output


def test_source_intake_cli_add_dry_run(tmp_path, capsys):
    registry = tmp_path / "source_evidence.yaml"
    write_source_registry(registry, load_source_evidence())
    candidate = _write_candidate(tmp_path / "candidate.yaml", source_id="cli_dry_run_source")

    code = source_intake_cli.main(
        [
            "add",
            "--candidate",
            str(candidate),
            "--registry",
            str(registry),
            "--dry-run",
        ]
    )
    output = capsys.readouterr().out

    assert code == 0
    assert '"status": "dry_run"' in output
    assert "no registry file was modified" in output


def test_source_intake_cli_preview_handles_yaml_date(capsys):
    code = source_intake_cli.main(
        [
            "preview",
            "--candidate",
            "examples/source_candidate.example.yaml",
            "--match",
            "portugal_dr_congo",
        ]
    )
    output = capsys.readouterr().out

    assert code == 0
    assert '"published_date": "2026-05-24"' in output
    assert '"ticket_safety"' in output


def _write_candidate(path, source_id="candidate_source", evidence_tags=None):
    data = {
        "match_id": "portugal_dr_congo",
        "source": {
            "source_id": source_id,
            "title": "Candidate Source",
            "publisher": "Candidate Publisher",
            "published_date": "2026-05-24",
            "url": "https://example.com/candidate-source",
            "source_type": "news",
            "evidence_tags": evidence_tags or ["tickets", "ticket_safety"],
            "summary": "Human-reviewed candidate source summary.",
        },
    }
    path.write_text(yaml.safe_dump(data, sort_keys=False), encoding="utf-8")
    return path
