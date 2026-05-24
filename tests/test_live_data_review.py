from eventtrip import live_data_cli
from eventtrip.live_data_review import import_reviewed_live_snapshots
from eventtrip.market_snapshots import load_market_snapshots


FIXTURE = "examples/live_api_snapshot_response.json"


def test_reviewed_live_import_dry_run_does_not_write(tmp_path):
    destination = tmp_path / "snapshots.csv"

    result = import_reviewed_live_snapshots(
        input_path=FIXTURE,
        match_id="portugal_dr_congo",
        destination_path=destination,
    )

    assert result["status"] == "dry_run"
    assert result["saved"] is False
    assert result["snapshot_count"] == 1
    assert result["snapshots"][0]["source_type"] == "reviewed_live_data"
    assert not destination.exists()


def test_reviewed_live_import_requires_reviewed_flag_for_save(tmp_path):
    destination = tmp_path / "snapshots.csv"

    result = import_reviewed_live_snapshots(
        input_path=FIXTURE,
        match_id="portugal_dr_congo",
        destination_path=destination,
        save=True,
        reviewed=False,
    )

    assert result["status"] == "review_required"
    assert result["saved"] is False
    assert "requires --reviewed" in result["errors"][0]
    assert not destination.exists()


def test_reviewed_live_import_saves_after_human_review(tmp_path):
    destination = tmp_path / "snapshots.csv"

    result = import_reviewed_live_snapshots(
        input_path=FIXTURE,
        match_id="portugal_dr_congo",
        destination_path=destination,
        save=True,
        reviewed=True,
        review_notes="Manual review complete.",
    )
    snapshots = load_market_snapshots(destination, "portugal_dr_congo")

    assert result["status"] == "saved"
    assert result["saved"] is True
    assert len(snapshots) == 1
    assert snapshots[0].lowest_price == 640
    assert snapshots[0].source_type == "reviewed_live_data"
    assert "Manual review complete." in snapshots[0].notes


def test_reviewed_live_import_duplicate_without_overwrite_fails(tmp_path):
    destination = tmp_path / "snapshots.csv"

    assert import_reviewed_live_snapshots(
        input_path=FIXTURE,
        match_id="portugal_dr_congo",
        destination_path=destination,
        save=True,
        reviewed=True,
    )["saved"]
    duplicate = import_reviewed_live_snapshots(
        input_path=FIXTURE,
        match_id="portugal_dr_congo",
        destination_path=destination,
        save=True,
        reviewed=True,
    )

    assert duplicate["status"] == "duplicate"
    assert duplicate["saved"] is False
    assert "use --overwrite" in duplicate["errors"][0]


def test_live_data_cli_import_dry_run(capsys, tmp_path):
    destination = tmp_path / "snapshots.csv"

    code = live_data_cli.main(
        [
            "import",
            "--input",
            FIXTURE,
            "--match",
            "portugal_dr_congo",
            "--destination",
            str(destination),
            "--dry-run",
        ]
    )
    output = capsys.readouterr().out

    assert code == 0
    assert '"status": "dry_run"' in output
    assert "no snapshot file was modified" in output
    assert not destination.exists()


def test_live_data_cli_import_save_requires_reviewed(capsys, tmp_path):
    destination = tmp_path / "snapshots.csv"

    code = live_data_cli.main(
        [
            "import",
            "--input",
            FIXTURE,
            "--match",
            "portugal_dr_congo",
            "--destination",
            str(destination),
            "--save",
        ]
    )
    output = capsys.readouterr().out

    assert code == 1
    assert '"status": "review_required"' in output
    assert "requires --reviewed" in output
    assert not destination.exists()
