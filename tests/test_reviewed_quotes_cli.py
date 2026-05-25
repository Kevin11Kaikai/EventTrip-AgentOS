from eventtrip import reviewed_quotes_cli, source_backed_quotes_cli
from eventtrip.reviewed_quotes import load_reviewed_quotes


def test_reviewed_quotes_summary_handles_empty_file(tmp_path, capsys):
    path = tmp_path / "missing.csv"

    code = reviewed_quotes_cli.main(["summary", "--match", "portugal_dr_congo", "--path", str(path)])
    output = capsys.readouterr().out

    assert code == 0
    assert "Source-backed quote count: 0" in output
    assert "No source-backed quotes are available yet." in output


def test_reviewed_quotes_import_dry_run_does_not_write(tmp_path, capsys):
    destination = tmp_path / "quotes.csv"

    code = reviewed_quotes_cli.main(
        [
            "import",
            "--input",
            "examples/reviewed_quote_import.csv",
            "--match",
            "portugal_dr_congo",
            "--destination",
            str(destination),
            "--dry-run",
        ]
    )
    output = capsys.readouterr().out

    assert code == 0
    assert "Dry run: validated 5 source-backed quote rows" in output
    assert not destination.exists()


def test_reviewed_quotes_import_writes_and_summary_reports_total(tmp_path, capsys):
    destination = tmp_path / "quotes.csv"

    import_code = reviewed_quotes_cli.main(
        [
            "import",
            "--input",
            "examples/reviewed_quote_import.csv",
            "--match",
            "portugal_dr_congo",
            "--destination",
            str(destination),
        ]
    )
    summary_code = reviewed_quotes_cli.main(
        ["summary", "--match", "portugal_dr_congo", "--path", str(destination)]
    )
    output = capsys.readouterr().out

    assert import_code == 0
    assert summary_code == 0
    assert len(load_reviewed_quotes(destination)) == 5
    assert "PIT source-backed total: $1190" in output
    assert "SEA source-backed total: $1290" in output


def test_reviewed_quotes_import_duplicate_without_overwrite_fails(tmp_path, capsys):
    destination = tmp_path / "quotes.csv"
    args = [
        "import",
        "--input",
        "examples/reviewed_quote_import.csv",
        "--match",
        "portugal_dr_congo",
        "--destination",
        str(destination),
    ]

    assert reviewed_quotes_cli.main(args) == 0
    duplicate_code = reviewed_quotes_cli.main(args)
    output = capsys.readouterr().out

    assert duplicate_code == 1
    assert "Duplicate source-backed quote rows" in output


def test_source_backed_quotes_cli_alias_runs_summary(tmp_path, capsys):
    path = tmp_path / "missing.csv"

    code = source_backed_quotes_cli.main(
        ["summary", "--match", "portugal_dr_congo", "--path", str(path)]
    )
    output = capsys.readouterr().out

    assert code == 0
    assert "Source-backed quote count: 0" in output
