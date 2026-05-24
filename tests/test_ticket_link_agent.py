from eventtrip.agents.ticket_link_agent import TicketLinkAgent


def test_ticket_link_agent_writes_markdown_output(tmp_path):
    trip_request = {
        "match": {"match_id": "portugal_dr_congo"},
    }
    context = {"ticket_timing": "monitor"}

    result = TicketLinkAgent().run(trip_request, tmp_path, context)

    output = tmp_path / "01b_ticket_link_agent.md"
    assert output.exists()
    text = output.read_text(encoding="utf-8")
    assert "Ticket Link Recommendations" in text
    assert "FIFA World Cup 2026 Tickets" in text
    assert "Secondary Marketplace Candidate" in text
    assert "StubHub World Cup Tickets" in text
    assert result["ticket_links"]["primary_links"]
    assert result["ticket_links"]["secondary_links"]
