import json
import shutil

import pytest

from eventtrip import snapshots_cli
from eventtrip.data_providers.config import SUPPORTED_PROVIDER_TYPES, get_provider
from eventtrip.data_providers.import_provider import SnapshotImportProvider
from eventtrip.market_snapshots import default_snapshot_path, load_market_snapshots


CSV_EXAMPLE = "examples/external_snapshot_import.csv"
JSON_EXAMPLE = "examples/external_snapshot_import.json"


def test_import_provider_loads_external_csv_example():
    snapshots = SnapshotImportProvider(CSV_EXAMPLE).load_snapshots("portugal_dr_congo")

    assert len(snapshots) == 2
    assert snapshots[0].snapshot_date == "2026-05-22"
    assert snapshots[0].lowest_price == 650


def test_import_provider_loads_external_json_example():
    snapshots = SnapshotImportProvider(JSON_EXAMPLE).load_snapshots("portugal_dr_congo")

    assert len(snapshots) == 2
    assert snapshots[1].snapshot_date == "2026-05-29"
    assert snapshots[1].listings == 375


def test_import_provider_filters_by_match_id():
    snapshots = SnapshotImportProvider(CSV_EXAMPLE).load_snapshots("missing_match")

    assert snapshots == []


def test_import_provider_invalid_extension_fails(tmp_path):
    path = tmp_path / "snapshots.txt"
    path.write_text("not supported", encoding="utf-8")

    with pytest.raises(ValueError, match="Unsupported snapshot import format"):
        SnapshotImportProvider(path).load_snapshots()


def test_import_provider_invalid_score_fails(tmp_path):
    path = tmp_path / "invalid.csv"
    path.write_text(
        "snapshot_date,match_id,lowest_price,listings,category_3_low,category_3_high,"
        "hotel_availability_score,flight_price_pressure,social_buzz_score,days_before_event,"
        "source_type,notes\n"
        "2026-05-22,portugal_dr_congo,650,360,400,750,1.5,0.55,0.86,26,test,bad score\n",
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="hotel_availability_score must be between 0 and 1"):
        SnapshotImportProvider(path).load_snapshots("portugal_dr_congo")


def test_provider_registry_returns_supported_providers():
    assert "import_file" in SUPPORTED_PROVIDER_TYPES
    provider = get_provider("import_file", input_path=CSV_EXAMPLE)

    assert isinstance(provider, SnapshotImportProvider)


def test_provider_registry_rejects_deferred_scraper():
    with pytest.raises(NotImplementedError, match="does not scrape websites"):
        get_provider("web_scraper")


def test_cli_import_dry_run_does_not_modify_destination(tmp_path, capsys):
    destination = tmp_path / "snapshots.csv"

    exit_code = snapshots_cli.main(
        [
            "import",
            "--input",
            CSV_EXAMPLE,
            "--match",
            "portugal_dr_congo",
            "--destination",
            str(destination),
            "--dry-run",
        ]
    )
    output = capsys.readouterr().out

    assert exit_code == 0
    assert "Dry run: validated 2 snapshots" in output
    assert not destination.exists()


def test_cli_import_writes_to_temp_destination(tmp_path):
    destination = tmp_path / "snapshots.csv"

    exit_code = snapshots_cli.main(
        [
            "import",
            "--input",
            CSV_EXAMPLE,
            "--match",
            "portugal_dr_congo",
            "--destination",
            str(destination),
        ]
    )
    snapshots = load_market_snapshots(destination, "portugal_dr_congo")

    assert exit_code == 0
    assert len(snapshots) == 2
    assert snapshots[0].snapshot_date == "2026-05-22"


def test_cli_import_duplicate_without_overwrite_fails_safely(tmp_path, capsys):
    destination = tmp_path / "snapshots.csv"

    first_exit = snapshots_cli.main(
        ["import", "--input", CSV_EXAMPLE, "--match", "portugal_dr_congo", "--destination", str(destination)]
    )
    second_exit = snapshots_cli.main(
        ["import", "--input", CSV_EXAMPLE, "--match", "portugal_dr_congo", "--destination", str(destination)]
    )
    output = capsys.readouterr().out

    assert first_exit == 0
    assert second_exit == 1
    assert "use --overwrite" in output
    assert len(load_market_snapshots(destination, "portugal_dr_congo")) == 2


def test_cli_import_duplicate_with_overwrite_updates_existing_row(tmp_path):
    destination = tmp_path / "snapshots.csv"
    updated_import = tmp_path / "updated.json"
    updated_import.write_text(
        json.dumps(
            [
                {
                    "snapshot_date": "2026-05-22",
                    "match_id": "portugal_dr_congo",
                    "lowest_price": 620,
                    "listings": 390,
                    "category_3_low": 400,
                    "category_3_high": 750,
                    "hotel_availability_score": 0.48,
                    "flight_price_pressure": 0.57,
                    "social_buzz_score": 0.87,
                    "days_before_event": 26,
                    "source_type": "test_update",
                    "notes": "Overwrite test.",
                }
            ]
        ),
        encoding="utf-8",
    )

    assert snapshots_cli.main(
        ["import", "--input", CSV_EXAMPLE, "--match", "portugal_dr_congo", "--destination", str(destination)]
    ) == 0
    assert snapshots_cli.main(
        [
            "import",
            "--input",
            str(updated_import),
            "--match",
            "portugal_dr_congo",
            "--destination",
            str(destination),
            "--overwrite",
        ]
    ) == 0
    snapshots = load_market_snapshots(destination, "portugal_dr_congo")
    updated = [snapshot for snapshot in snapshots if snapshot.snapshot_date == "2026-05-22"][0]

    assert len(snapshots) == 2
    assert updated.lowest_price == 620
    assert updated.listings == 390


def test_cli_import_can_target_temp_copy_of_seed(tmp_path):
    destination = tmp_path / "seed_copy.csv"
    shutil.copyfile(default_snapshot_path("portugal_dr_congo"), destination)

    exit_code = snapshots_cli.main(
        ["import", "--input", JSON_EXAMPLE, "--match", "portugal_dr_congo", "--destination", str(destination)]
    )

    assert exit_code == 0
    assert len(load_market_snapshots(destination, "portugal_dr_congo")) == 7
