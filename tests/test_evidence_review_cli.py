from eventtrip import evidence_review_cli


SAMPLE_EVIDENCE = "examples/sample_web_evidence.json"


def test_evidence_review_preview_cli_succeeds(capsys):
    code = evidence_review_cli.main(["preview", "--evidence", SAMPLE_EVIDENCE])
    output = capsys.readouterr().out

    assert code == 0
    assert "candidate_lowest_price: 680.0" in output
    assert "candidate_listings: 340" in output


def test_evidence_review_convert_dry_run_does_not_write(tmp_path, capsys):
    destination = tmp_path / "snapshots.csv"
    code = evidence_review_cli.main(
        [
            "convert",
            "--evidence",
            SAMPLE_EVIDENCE,
            "--snapshot-date",
            "2026-05-22",
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
            "--destination",
            str(destination),
            "--dry-run",
        ]
    )
    output = capsys.readouterr().out

    assert code == 0
    assert "Dry run" in output
    assert not destination.exists()


def test_evidence_review_convert_save_writes_temp_destination(tmp_path):
    destination = tmp_path / "snapshots.csv"

    code = _run_convert(destination, save=True)

    assert code == 0
    assert destination.exists()


def test_evidence_review_duplicate_without_overwrite_fails(tmp_path, capsys):
    destination = tmp_path / "snapshots.csv"
    assert _run_convert(destination, save=True) == 0

    code = _run_convert(destination, save=True)
    output = capsys.readouterr().out

    assert code == 1
    assert "use --overwrite" in output


def test_evidence_review_duplicate_with_overwrite_succeeds(tmp_path):
    destination = tmp_path / "snapshots.csv"
    assert _run_convert(destination, save=True) == 0

    code = _run_convert(destination, save=True, overwrite=True)

    assert code == 0


def _run_convert(destination, save: bool, overwrite: bool = False) -> int:
    args = [
        "convert",
        "--evidence",
        SAMPLE_EVIDENCE,
        "--snapshot-date",
        "2026-05-22",
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
        "--destination",
        str(destination),
    ]
    args.append("--save" if save else "--dry-run")
    if overwrite:
        args.append("--overwrite")
    return evidence_review_cli.main(args)
