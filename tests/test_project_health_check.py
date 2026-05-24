from scripts import project_health_check


def test_secret_detection_allows_placeholder_key():
    assert not project_health_check.has_suspicious_secret(
        "OHMYGPT" + "_API_KEY=your_ohmygpt_api_key_here"
    )


def test_secret_detection_flags_realistic_openai_style_key():
    assert project_health_check.has_suspicious_secret(
        "OHMYGPT" + "_API_KEY=" + "s" + "k-abcdefghijklmnopqrstuvwxyz123456"
    )


def test_important_files_check_passes_for_current_repo():
    assert project_health_check.check_important_files() == []
