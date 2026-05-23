# Ticket Timing Skill

Use this skill to decide whether travelers should buy, wait, or monitor ticket inventory for a single event match.

## Inputs

- Lowest verified ticket price
- Active listings count
- Category or seat range target
- Seven-day price trend
- Days before event
- Official resale availability
- Hotel availability proxy
- Flight price pressure
- Social media or fan buzz
- Scalper Stress Index

## Process

1. Confirm the event scope and match ID.
2. Compare the lowest price against the target category range.
3. Check whether listings are rising, stable, or falling.
4. Treat falling prices plus high listings as possible reseller inventory unloading.
5. Treat high hotel availability and moderate flight prices as weak real travel-demand pressure.
6. Treat high social buzz as genuine retail demand, but do not let buzz alone force a purchase.
7. Use the Scalper Stress Index as a decision-support signal, not a standalone answer.

## Output Format

- Recommendation: buy, wait, or monitor
- Trigger price
- Signals supporting the recommendation
- Risks if travelers buy now
- Risks if travelers wait
- Next check-in window

## Example Recommendation

Monitor. Current listings are high and the price is near the upper end of the target range. Buy only if official resale inventory appears or the lowest verified price falls near the budget trigger.

