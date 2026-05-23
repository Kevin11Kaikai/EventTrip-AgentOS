# Hotel Value Skill

Use this skill to rank hotel options for event travel where budget, access, and cancellation flexibility matter.

## Inputs

- Two-bed availability
- Walking distance to venue
- METRORail or transit access
- Cancellation policy
- Price per night
- Price per person after AA split
- Review quality or rating
- Late-night safety considerations
- Optional breakfast or kitchen value

## Process

1. Filter out hotels that cannot confirm two beds when two travelers are sharing.
2. Prefer walking distance when the post-event exit will be crowded.
3. Use METRORail access as a strong substitute for walking distance.
4. Penalize non-refundable inventory when ticket purchase timing is uncertain.
5. Score price per person, not just room price.
6. Treat breakfast or kitchen access as optional value, not a primary reason to overpay.
7. Flag lower-rated hotels even when they are cheaper.

## Output Format

- Ranked hotel list
- Best budget-first hotel
- AA split per person
- Cancellation notes
- Access notes
- Risks and mitigations

