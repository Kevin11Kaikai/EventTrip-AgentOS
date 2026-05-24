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


def test_recommend_ticket_links_includes_manual_checklist():
    recommendation = recommend_ticket_links("portugal_dr_congo", "monitor_with_wait_bias")

    assert recommendation["primary_links"]
    assert recommendation["primary_links"][0]["purchase_role"] == "recommended_official_entry"
    assert "Monitor with wait bias" not in recommendation["warnings"][0]
    assert any("all-in price" in item for item in recommendation["manual_purchase_checklist"])


def test_manual_purchase_checklist_keeps_user_in_control():
    checklist = manual_purchase_checklist()

    assert any("Confirm the seller/page" in item for item in checklist)
    assert any("Do not share payment details" in item for item in checklist)
