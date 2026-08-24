# Data Review

This file lists the decisions that change which source value reaches the final database. The detailed rows are in `review/`.

## Source choice

- Weather values use BMD, then BRRI, then BBS.
- Equal-authority conflicts use the newest stated coverage, then the later source occurrence.
- Every displaced value remains in `review/VALUE_CONFLICTS.csv`.

## Monthly derivation

- Daily maximum temperature becomes the monthly maximum.
- Daily minimum temperature becomes the monthly minimum.
- Daily rainfall is summed by month.
- Daily humidity is averaged by month.
- Daily sunshine remains daily.
- Aggregation counts are in `review/BRRI_MONTHLY_AGGREGATION.csv`.

## Review counts

- Active source blocks: 62 (B01-B62).
- Source-cell accounting for every block is in `review/BLOCK_ACCOUNTING.csv`.
- Displaced source values: 39591.
- Quarantined rows or values: 56.
- Stations without a published district mapping: 40.

## Team report follow-up

- Use 62 active source blocks.
- Use the table name `Industry_Type` consistently.
- `Industry_Usage.Quantity` is produced waste-water volume.
- `Industry_Usage.Percentage` is the reuse rate.
- Climatic event values are monthly frequencies, not a count of days.
- Database rows for minimum and maximum temperature remain separate because `Type` is part of the approved primary key.
