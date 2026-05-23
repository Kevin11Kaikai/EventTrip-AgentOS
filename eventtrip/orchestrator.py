"""CLI orchestrator for EventTrip-AgentOS."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

import yaml

try:  # pragma: no cover - depends on optional dependency availability
    from dotenv import load_dotenv

    load_dotenv()
except Exception:
    pass

from eventtrip.agents import (
    BudgetAgent,
    FlightAgent,
    HotelAgent,
    MarketAgent,
    ReportAgent,
    RiskAgent,
    SnapshotAgent,
    TicketAgent,
)
from eventtrip.markdown_io import create_run_dir, write_markdown
from eventtrip.report_polisher import polish_report


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = PROJECT_ROOT / "data" / "worldcup_houston_demo.yaml"


def load_demo_request(demo: str) -> dict[str, Any]:
    if demo != "portugal_dr_congo_houston":
        raise ValueError("Only --demo portugal_dr_congo_houston is supported.")
    return yaml.safe_load(DATA_PATH.read_text(encoding="utf-8"))


def write_user_request(run_dir: Path, trip_request: dict[str, Any]) -> None:
    match = trip_request["match"]
    travelers = "\n".join(
        f"- {traveler['name']}: {traveler['origin']}" for traveler in trip_request["travelers"]
    )
    constraints = "\n".join(f"- {constraint}" for constraint in trip_request["constraints"])
    body = f"""# User Request

Plan a budget-first collaborative event trip for one match only.

## Match

- {match["name"]}
- Date: {match["date"]}
- Venue: {match["venue"]}, {match["city"]}

## Travelers

{travelers}

## Constraints

{constraints}

Default mode must use mock data only and must not call paid APIs.
"""
    write_markdown(
        run_dir / "00_user_request.md",
        {
            "agent": "user_request",
            "status": "completed",
            "confidence": "high",
            "next_agent": "ticket_agent",
        },
        body,
    )


def run_demo(
    demo: str = "portugal_dr_congo_houston",
    use_llm: bool = False,
    runs_root: Path | None = None,
) -> dict[str, Any]:
    trip_request = load_demo_request(demo)
    run_dir = create_run_dir("portugal_dr_congo_houston_demo", runs_root=runs_root)
    write_user_request(run_dir, trip_request)

    context: dict[str, Any] = {}
    agents = [
        TicketAgent(use_llm=False),
        FlightAgent(use_llm=False),
        HotelAgent(use_llm=False),
        SnapshotAgent(use_llm=False),
        MarketAgent(use_llm=False),
        BudgetAgent(use_llm=False),
        RiskAgent(use_llm=False),
        ReportAgent(use_llm=False),
    ]
    for agent in agents:
        context.update(agent.run(trip_request, run_dir, context))

    recommended = context["budget"]["recommended"]
    polish_result = None
    if use_llm:
        polish_result = polish_report(
            context["final_report_path"],
            run_dir / "09_final_report_polished.md",
        )
    return {
        "run_dir": run_dir,
        "final_report_path": context["final_report_path"],
        "polished_report": polish_result,
        "recommended_option": recommended["option_name"],
        "estimated_cost_per_traveler": recommended["total_cost_per_traveler"],
        "ticket_timing_recommendation": context.get(
            "combined_ticket_timing_recommendation",
            context["ticket_timing"],
        ),
        "ticket_timing_label": context.get("combined_ticket_timing_label", context["ticket_timing"]),
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run the EventTrip-AgentOS demo.")
    parser.add_argument("--demo", required=True, help="Demo id. Use portugal_dr_congo_houston.")
    parser.add_argument("--use-llm", action="store_true", help="Enable optional OhMyGPT prose polishing.")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        result = run_demo(demo=args.demo, use_llm=args.use_llm)
    except Exception as exc:
        print(f"ERROR: {exc}")
        return 2

    print(f"Final report: {result['final_report_path']}")
    print(f"Recommended option: {result['recommended_option']}")
    print("Estimated cost per traveler:")
    for traveler, total in result["estimated_cost_per_traveler"].items():
        print(f"  {traveler}: ${total:.0f}")
    print(f"Ticket timing recommendation: {result['ticket_timing_label']}")
    if result["polished_report"]:
        polish_result = result["polished_report"]
        print(f"LLM polishing status: {polish_result['status']}")
        if polish_result.get("output_path"):
            print(f"Polished report: {polish_result['output_path']}")
        for issue in polish_result.get("issues", []):
            print(f"  - {issue}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
