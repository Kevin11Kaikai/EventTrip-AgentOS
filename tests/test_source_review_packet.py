import json

from eventtrip import source_review_cli
from eventtrip.source_evidence import load_source_evidence
from eventtrip.source_intake import write_source_registry
from eventtrip.source_review_packet import (
    build_source_registry_review_summary,
    render_source_registry_review_markdown,
    write_source_registry_review_packet,
)


def test_source_registry_review_summary_passes_for_current_registry():
    summary = build_source_registry_review_summary(
        match_id="portugal_dr_congo",
        generated_at="2026-05-24T00:00:00Z",
    )

    assert summary["status"] == "pass"
    assert summary["source_count"] >= 1
    assert not summary["validation_errors"]
    assert any(group["group_key"] == "ticket_safety" for group in summary["citation_groups"])
    assert any(field["field_id"] == "official_ticket_path" for field in summary["field_attributions"])


def test_source_registry_review_markdown_includes_pr_checklist():
    summary = build_source_registry_review_summary(
        match_id="portugal_dr_congo",
        generated_at="2026-05-24T00:00:00Z",
    )
    markdown = render_source_registry_review_markdown(summary)

    assert "# Source Registry Review Packet" in markdown
    assert "## Pull Request Review Checklist" in markdown
    assert "Citation Group Coverage" in markdown
    assert "Field-Level Attribution Coverage" in markdown


def test_write_source_registry_review_packet_json(tmp_path):
    output = tmp_path / "review_packet.json"

    path = write_source_registry_review_packet(
        output,
        match_id="portugal_dr_congo",
        output_format="json",
    )
    payload = json.loads(path.read_text(encoding="utf-8"))

    assert payload["status"] == "pass"
    assert payload["match_id"] == "portugal_dr_congo"


def test_review_summary_fails_when_registry_loses_ticket_safety_group(tmp_path):
    registry = load_source_evidence()
    sources = registry["portugal_dr_congo"]["sources"]
    registry["portugal_dr_congo"]["sources"] = [
        source
        for source in sources
        if not set(source.get("evidence_tags", [])).intersection(
            {"tickets", "official_purchase", "official_resale", "ticket_safety", "resale_risk", "secondary_market"}
        )
    ]
    registry_path = tmp_path / "source_evidence.yaml"
    write_source_registry(registry_path, registry)

    summary = build_source_registry_review_summary(registry_path, match_id="portugal_dr_congo")

    assert summary["status"] == "fail"
    assert any("ticket_safety" in error for error in summary["validation_errors"])


def test_source_review_cli_summary_passes(capsys):
    code = source_review_cli.main(["summary", "--match", "portugal_dr_congo"])
    output = capsys.readouterr().out

    assert code == 0
    assert "Source registry review status: PASS" in output
    assert "Citation groups:" in output


def test_source_review_cli_export_markdown_to_file(tmp_path, capsys):
    output_path = tmp_path / "packet.md"

    code = source_review_cli.main(
        [
            "export",
            "--match",
            "portugal_dr_congo",
            "--format",
            "md",
            "--output",
            str(output_path),
        ]
    )
    output = capsys.readouterr().out

    assert code == 0
    assert "written to" in output
    assert "# Source Registry Review Packet" in output_path.read_text(encoding="utf-8")
