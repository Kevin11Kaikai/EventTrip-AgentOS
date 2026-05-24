# Ticket Link Recommendations

## Purpose

EventTrip-AgentOS recommends safe manual ticket navigation links. It does not buy tickets, log in, bypass access controls, solve CAPTCHA, automate checkout, or handle payment.

The goal is to point travelers toward official or verified official paths while preserving the existing budget-first and anti-scalper trigger policy.

## Link Policy

- Prefer FIFA official ticketing first.
- Prefer FIFA official resale/exchange before any non-FIFA source.
- Treat official support articles as policy references, not checkout pages.
- Treat hospitality as optional and premium, not budget-first by default.
- Treat StubHub as a secondary-market monitoring candidate, not as the preferred or official purchase channel.
- Do not recommend third-party marketplaces as preferred purchase channels.
- Always require manual verification before payment.

## Current Registry

The local registry is stored at:

```text
data/ticket_links.yaml
```

For `portugal_dr_congo`, it includes:

- FIFA World Cup 2026 Tickets
- FIFA Resale/Exchange Marketplace
- FIFA Resale/Exchange support guidance
- FIFA unofficial resale risk guidance
- FIFA hospitality as an optional premium path
- StubHub World Cup Tickets as a secondary-market candidate to monitor manually

## Manual Purchase Checklist

Before buying, manually confirm:

- The seller/page is official FIFA ticketing or official FIFA resale/exchange.
- The match is Portugal vs DR Congo.
- The date is June 17, 2026.
- The venue is NRG Stadium / Houston Stadium in Houston.
- Seat category, quantity, all-in price, fees, transfer policy, and refund policy.
- The all-in price against the $550 buy trigger and $600 strong-consider trigger.
- For StubHub or another third-party marketplace, confirm the exact match listing, delivery timing, FIFA transfer method, refund policy, and buyer protection terms.

## What This Does Not Do

- No automated purchasing.
- No login or account automation.
- No payment handling.
- No browser automation.
- No scraping of ticket marketplaces.
- No guarantee that inventory is available.
- No claim that StubHub is an official FIFA ticketing channel.

## MCP Tools

Phase 7.2 exposes preview-safe ticket link tools:

- `get_ticket_links`
- `recommend_ticket_links`

They return deterministic registry data and do not open URLs or write files.
