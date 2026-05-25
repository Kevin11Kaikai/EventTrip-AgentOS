# Source Registry Review Packet

## Summary

| Field | Value |
|---|---|
| Generated at | 2026-05-25T01:08:19Z |
| Match ID | `portugal_dr_congo` |
| Registry | `D:\others\Eventrip_agentos\data\source_evidence.yaml` |
| Validation status | **PASS** |
| Source count | 13 |

## Automated Review Checks

- [x] Registry passes strict source intake validation.
- [x] Every source has required metadata fields.
- [x] Every citation group has at least one source.
- [x] Every source maps to at least one citation group.
- [x] Field-level source IDs all point to registered sources.
- [x] Unknown or model-derived values remain separated from source-backed facts.

## Citation Group Coverage

| Group | Title | Sources | Source IDs |
|---|---|---:|---|
| `match_facts` | Match facts | 2 | fifa_match_preview, axios_drc_base_camp |
| `ticket_safety` | Ticket safety | 6 | fifa_tickets, fifa_resale_support, kiplinger_ticket_scams, stubhub_world_cup_tickets, moneyweek_ticket_scam_warning, ap_group_games_general_sale |
| `houston_logistics` | Houston logistics | 4 | axios_drc_base_camp, axios_houston_transport_waymo, axios_houston_pitch, axios_houston_worldcup_hotel_supply |
| `cost_trends` | Cost trend evidence | 4 | ap_group_games_general_sale, expedia_2026_air_hacks, kayak_2026_hotel_timing, axios_houston_worldcup_hotel_supply |

## Source Inventory

| Source ID | Publisher | Type | Tags | Citation groups |
|---|---|---|---|---|
| `fifa_match_preview` | FIFA | official | match, venue, date | match_facts |
| `fifa_tickets` | FIFA | official | tickets, official_purchase | ticket_safety |
| `fifa_resale_support` | FIFA World Cup 2026 Customer Support | official | tickets, official_resale | ticket_safety |
| `axios_drc_base_camp` | Axios Houston | news | team_base_camp, houston, match | match_facts, houston_logistics |
| `axios_houston_transport_waymo` | Axios Houston | news | local_transport, houston | houston_logistics |
| `axios_houston_pitch` | Axios Houston | news | venue_readiness, houston | houston_logistics |
| `kiplinger_ticket_scams` | Kiplinger | news | ticket_safety, resale_risk | ticket_safety |
| `stubhub_world_cup_tickets` | StubHub | marketplace | tickets, secondary_market, resale_risk | ticket_safety |
| `moneyweek_ticket_scam_warning` | MoneyWeek | news | ticket_safety, resale_risk | ticket_safety |
| `ap_group_games_general_sale` | Associated Press | news | tickets, ticket_market_pressure | ticket_safety, cost_trends |
| `expedia_2026_air_hacks` | Expedia | travel_data | airfare_trend | cost_trends |
| `kayak_2026_hotel_timing` | KAYAK | travel_data | hotel_trend | cost_trends |
| `axios_houston_worldcup_hotel_supply` | Axios Houston | news | houston, hotel_trend, local_transport | houston_logistics, cost_trends |

## Evidence Tag Counts

| Evidence tag | Count |
|---|---:|
| `airfare_trend` | 1 |
| `date` | 1 |
| `hotel_trend` | 2 |
| `houston` | 4 |
| `local_transport` | 2 |
| `match` | 2 |
| `official_purchase` | 1 |
| `official_resale` | 1 |
| `resale_risk` | 3 |
| `secondary_market` | 1 |
| `team_base_camp` | 1 |
| `ticket_market_pressure` | 1 |
| `ticket_safety` | 2 |
| `tickets` | 4 |
| `venue` | 1 |
| `venue_readiness` | 1 |

## Field-Level Attribution Coverage

| Field ID | Status | Source IDs | Unknown source refs |
|---|---|---|---|
| `forecast_chart` | model_inference | ap_group_games_general_sale, expedia_2026_air_hacks, kayak_2026_hotel_timing, axios_houston_worldcup_hotel_supply | None |
| `houston_logistics` | source_backed | axios_drc_base_camp, axios_houston_transport_waymo, axios_houston_pitch, axios_houston_worldcup_hotel_supply | None |
| `match_date` | source_backed | fifa_match_preview, axios_drc_base_camp | None |
| `match_name` | source_backed | fifa_match_preview, axios_drc_base_camp | None |
| `match_venue` | source_backed | fifa_match_preview, axios_drc_base_camp | None |
| `official_ticket_path` | source_backed | fifa_tickets, fifa_resale_support, kiplinger_ticket_scams, moneyweek_ticket_scam_warning, ap_group_games_general_sale | None |
| `pit_recommendation` | model_inference | ap_group_games_general_sale, expedia_2026_air_hacks, kayak_2026_hotel_timing, axios_houston_worldcup_hotel_supply | None |
| `reviewed_live_snapshots` | human_reviewed_data | None | None |
| `sea_recommendation` | model_inference | ap_group_games_general_sale, expedia_2026_air_hacks, kayak_2026_hotel_timing, axios_houston_worldcup_hotel_supply | None |
| `secondary_market_stubhub` | source_backed | stubhub_world_cup_tickets | None |
| `trigger_policy` | internal_policy | None | None |
| `unknown_exact_prices` | no_source_backed_data_found | None | None |

## Validation Errors

- None.

## Pull Request Review Checklist

- [ ] The source URL is a public HTTPS page and does not require login, payment, checkout, or CAPTCHA.
- [ ] The source summary is human-reviewed and does not overstate what the page supports.
- [ ] The source uses supported source_type and evidence_tags values.
- [ ] The source maps to at least one citation group used by the public report.
- [ ] No unsupported ticket, flight, hotel, local transport, or total-budget number is presented as source-backed.
- [ ] Field-level attribution still distinguishes source-backed facts, model inference, internal policy, and unknown values.
- [ ] No secrets, credentials, generated run outputs, or private local files are included.

## Reviewer Notes

- This packet is generated from local source metadata only.
- It does not fetch URLs, scrape websites, verify article contents automatically, or purchase tickets.
- If a public source does not support a value, keep that value unknown or internally labeled rather than source-backed.
