from eventtrip import web_collect_cli


def test_cli_extract_local_fixture_succeeds(capsys):
    code = web_collect_cli.main(
        [
            "extract",
            "--local-path",
            "examples/sample_ticket_market_page.html",
            "--match",
            "portugal_dr_congo",
        ]
    )
    output = capsys.readouterr().out

    assert code == 0
    assert '"candidate_lowest_price": 680.0' in output
    assert '"candidate_listings": 340' in output


def test_cli_collect_dry_run_does_not_write(tmp_path, capsys):
    code = web_collect_cli.main(
        [
            "collect",
            "--target-id",
            "sample_fixture",
            "--local-path",
            "examples/sample_ticket_market_page.html",
            "--match",
            "portugal_dr_congo",
            "--dry-run",
            "--output-dir",
            str(tmp_path),
        ]
    )
    output = capsys.readouterr().out

    assert code == 0
    assert "Dry run" in output
    assert not list(tmp_path.glob("*.json"))
    assert not (tmp_path / "raw").exists()


def test_cli_collect_save_writes_to_temp_output_dir(tmp_path):
    code = web_collect_cli.main(
        [
            "collect",
            "--target-id",
            "sample_fixture",
            "--local-path",
            "examples/sample_ticket_market_page.html",
            "--match",
            "portugal_dr_congo",
            "--save",
            "--output-dir",
            str(tmp_path),
        ]
    )

    assert code == 0
    assert len(list(tmp_path.glob("*.json"))) == 1
    assert len(list((tmp_path / "raw").glob("*.txt"))) == 1


def test_cli_url_collection_requires_live_http(capsys):
    code = web_collect_cli.main(
        [
            "collect",
            "--target-id",
            "example_public",
            "--url",
            "https://example.com",
            "--match",
            "portugal_dr_congo",
            "--dry-run",
        ]
    )
    output = capsys.readouterr().out

    assert code == 2
    assert "Live HTTP collection is disabled" in output


def test_cli_policy_prints_conservative_policy(capsys):
    code = web_collect_cli.main(["policy"])
    output = capsys.readouterr().out

    assert code == 0
    assert '"max_pages_per_command": 1' in output
    assert '"default_live_http": false' in output
