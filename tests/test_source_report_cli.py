from eventtrip import source_report_cli


def _write_report(run_dir, text="report"):
    run_dir.mkdir(parents=True)
    report = run_dir / source_report_cli.SOURCE_BACKED_REPORT_NAME
    report.write_text(text, encoding="utf-8")
    return report


def _write_html_report(run_dir, text="<html></html>"):
    run_dir.mkdir(parents=True, exist_ok=True)
    report = run_dir / source_report_cli.SOURCE_BACKED_HTML_REPORT_NAME
    report.write_text(text, encoding="utf-8")
    return report


def test_find_latest_source_backed_report_uses_newest_run_name(tmp_path):
    older = _write_report(tmp_path / "portugal_dr_congo_houston_demo_20260524_090000")
    newer = _write_report(tmp_path / "portugal_dr_congo_houston_demo_20260524_100000")

    latest = source_report_cli.find_latest_source_backed_report(tmp_path)

    assert older.exists()
    assert latest == newer


def test_latest_cli_prints_report_path(tmp_path, capsys):
    report = _write_report(tmp_path / "portugal_dr_congo_houston_demo_20260524_100000")

    code = source_report_cli.main(["latest", "--runs-root", str(tmp_path)])
    output = capsys.readouterr().out

    assert code == 0
    assert str(report) in output


def test_latest_cli_prints_html_report_path(tmp_path, capsys):
    report = _write_html_report(tmp_path / "portugal_dr_congo_houston_demo_20260524_100000")

    code = source_report_cli.main(["latest", "--format", "html", "--runs-root", str(tmp_path)])
    output = capsys.readouterr().out

    assert code == 0
    assert str(report) in output


def test_latest_cli_reports_missing_source_report(tmp_path, capsys):
    code = source_report_cli.main(["latest", "--runs-root", str(tmp_path)])
    output = capsys.readouterr().out

    assert code == 1
    assert "No 10_source_backed_final_report.md found" in output
