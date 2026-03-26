# Data

## Source
Databento, CME Globex (GLBX.MDP3), Trades schema

## Files
- 2025-05-01 to 2025-12-31: GLBX-20250501-20251231.zip
- 2026-01-01 to 2026-03-09: GLBX-20260101-20260309.zip

## Schema
Each record contains: timestamp, price, size, aggressor side

## More Info
- Project analysis restricted to Regular Trading Hours 
  (RTH, 9:30 AM to 4:00 PM EST)
- Data stored locally in Desktop/Quant Research Project/raw-data
- All duplicate trades are confirmed legitimate multi-level fills 
  (large orders sweeping multiple price levels simultaneously). 
  All these trades are retained in the dataset.

## Excluded Trading Days

The following days were excluded from the sample due to anomalously
low activity (federal holidays or half-sessions):

| Date       | Reason                                            | Trade Count |
|------------|---------------------------------------------------|-------------|
| 2025-05-26 | Memorial Day (federal holiday)                    | 14,711      |
| 2025-07-04 | Independence Day (federal holiday)                | 13,367      |
| 2025-09-01 | Labor Day (federal holiday)                       | 11,431      |
| 2025-11-27 | Day before Thanksgiving (half-session, 1PM close) | 9,258       |

All excluded days have trade counts below 15,000 versus a sample
mean of 340,597. A natural gap exists between these four days
and the next lowest day (51,784 trades on 2025-06-19, Juneteenth).

Juneteenth (2025-06-19) and other reduced-activity days with
trade counts above 50,000 are retained as legitimate trading 
sessions.
