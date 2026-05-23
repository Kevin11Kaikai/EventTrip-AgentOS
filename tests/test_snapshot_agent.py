from eventtrip.agents.snapshot_agent import SnapshotAgent
from eventtrip.markdown_io import read_markdown
from eventtrip.orchestrator import load_demo_request


def test_snapshot_agent_writes_markdown_with_frontmatter(tmp_path):
    trip_request = load_demo_request("portugal_dr_congo_houston")
    result = SnapshotAgent(use_llm=False).run(trip_request, tmp_path, {})
    path = tmp_path / "04_snapshot_agent.md"
    metadata, body = read_markdown(path)

    assert path.exists()
    assert metadata["agent"] == "snapshot_agent"
    assert metadata["status"] == "completed"
    assert "Market Snapshot Trend Analysis" not in body
    assert "Snapshot Summary" in body
    assert result["snapshot_trend"]["snapshot_count"] >= 5
