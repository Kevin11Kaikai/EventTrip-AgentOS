import shutil

from eventtrip import snapshots_cli
from eventtrip.market_snapshots import default_snapshot_path, load_market_snapshots


def _copy_seed(tmp_path):
    path = tmp_path / "snapshots.csv"
    shutil.copyfile(default_snapshot_path("portugal_dr_congo"), path)
    return path


def _valid_append_args(path):
    return [
        "append",
        "--match",
        "portugal_dr_congo",
        "--snapshot-date",
        "2026-05-22",
        "--lowest-price",
        "650",
        "--listings",
        "360",
        "--category-3-low",
        "400",
        "--category-3-high",
        "750",
        "--hotel-availability-score",
        "0.50",
        "--flight-price-pressure",
        "0.55",
        "--social-buzz-score",
        "0.86",
        "--days-before-event",
        "26",
        "--source-type",
        "manual",
        "--notes",
        "Manual check",
        "--path",
        str(path),
    ]


def test_analyze_command_runs_against_temp_seed_copy(tmp_path, capsys):
    path = _copy_seed(tmp_path)

    exit_code = snapshots_cli.main(
        ["analyze", "--match", "portugal_dr_congo", "--path", str(path)]
    )
    output = capsys.readouterr().out

    assert exit_code == 0
    assert "Snapshot count: 5" in output
    assert "Recommendation:" in output


def test_append_dry_run_does_not_modify_file(tmp_path, capsys):
    path = _copy_seed(tmp_path)
    before = path.read_text(encoding="utf-8")

    exit_code = snapshots_cli.main(_valid_append_args(path) + ["--dry-run"])
    output = capsys.readouterr().out
    after = path.read_text(encoding="utf-8")

    assert exit_code == 0
    assert "Dry run" in output
    assert before == after


def test_append_writes_new_valid_row(tmp_path):
    path = _copy_seed(tmp_path)

    exit_code = snapshots_cli.main(_valid_append_args(path))
    snapshots = load_market_snapshots(path, "portugal_dr_congo")

    assert exit_code == 0
    assert len(snapshots) == 6
    assert snapshots[-1].snapshot_date == "2026-05-22"
    assert snapshots[-1].lowest_price == 650


def test_append_duplicate_without_overwrite_fails_safely(tmp_path, capsys):
    path = _copy_seed(tmp_path)

    first_exit = snapshots_cli.main(_valid_append_args(path))
    second_exit = snapshots_cli.main(_valid_append_args(path))
    output = capsys.readouterr().out

    assert first_exit == 0
    assert second_exit == 1
    assert "use --overwrite" in output
    assert len(load_market_snapshots(path, "portugal_dr_congo")) == 6


def test_append_duplicate_with_overwrite_replaces_row(tmp_path):
    path = _copy_seed(tmp_path)
    first_args = _valid_append_args(path)
    second_args = [
        "700" if value == "650" else value
        for value in _valid_append_args(path)
    ]

    assert snapshots_cli.main(first_args) == 0
    assert snapshots_cli.main(second_args + ["--overwrite"]) == 0
    snapshots = load_market_snapshots(path, "portugal_dr_congo")

    assert len(snapshots) == 6
    assert snapshots[-1].snapshot_date == "2026-05-22"
    assert snapshots[-1].lowest_price == 700


def test_invalid_score_above_one_fails(tmp_path, capsys):
    path = _copy_seed(tmp_path)
    args = [
        "1.50" if value == "0.50" else value
        for value in _valid_append_args(path)
    ]

    exit_code = snapshots_cli.main(args)
    output = capsys.readouterr().out

    assert exit_code == 2
    assert "hotel_availability_score must be between 0 and 1" in output


def test_invalid_category_range_fails(tmp_path, capsys):
    path = _copy_seed(tmp_path)
    args = [
        "800" if value == "400" else value
        for value in _valid_append_args(path)
    ]

    exit_code = snapshots_cli.main(args)
    output = capsys.readouterr().out

    assert exit_code == 2
    assert "category_3_low must be less than or equal to category_3_high" in output
