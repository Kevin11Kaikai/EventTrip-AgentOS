from eventtrip.llm_client import generate_text


def test_missing_ohmygpt_key_is_clear(monkeypatch):
    monkeypatch.delenv("OHMYGPT_API_KEY", raising=False)

    result = generate_text("system", "user")

    assert result.startswith("ERROR:")
    assert "OHMYGPT_API_KEY is missing" in result

