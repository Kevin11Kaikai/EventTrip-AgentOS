from eventtrip.ticket_links import (
    get_ticket_links,
    manual_purchase_checklist,
    recommend_ticket_links,
    validate_ticket_link_registry,
)


def test_ticket_link_registry_validates():
    assert validate_ticket_link_registry() == []


def test_ticket_links_are_official_first():
    links = get_ticket_links("portugal_dr_congo")

    assert links
    assert links[0]["source_type"] == "official_primary"
    assert links[0]["url"].startswith("https://www.fifa.com/")
    assert any(link["source_type"] == "secondary_market" for link in links)


def test_recommend_ticket_links_includes_manual_checklist():
    recommendation = recommend_ticket_links("portugal_dr_congo", "monitor_with_wait_bias")

    assert recommendation["primary_links"]
    assert recommendation["secondary_links"]
    assert recommendation["primary_links"][0]["purchase_role"] == "recommended_official_entry"
    assert recommendation["secondary_links"][0]["link_id"] == "stubhub_world_cup_tickets"
    assert "Monitor with wait bias" not in recommendation["warnings"][0]
    assert any("all-in price" in item for item in recommendation["manual_purchase_checklist"])
    assert any("StubHub" in warning for warning in recommendation["warnings"])


def test_manual_purchase_checklist_keeps_user_in_control():
    checklist = manual_purchase_checklist()

    assert any("Confirm the seller/page" in item for item in checklist)
    assert any("StubHub" in item for item in checklist)
    assert any("Do not share payment details" in item for item in checklist)
