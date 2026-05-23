from eventtrip.markdown_io import read_markdown, write_markdown


def test_markdown_roundtrip(tmp_path):
    path = tmp_path / "agent.md"
    frontmatter = {
        "agent": "ticket_agent",
        "status": "completed",
        "confidence": "medium",
        "next_agent": "flight_agent",
    }
    body = "# Ticket Agent\n\nMock output."

    write_markdown(path, frontmatter, body)
    metadata, read_body = read_markdown(path)

    assert metadata["agent"] == "ticket_agent"
    assert metadata["status"] == "completed"
    assert "Mock output." in read_body

