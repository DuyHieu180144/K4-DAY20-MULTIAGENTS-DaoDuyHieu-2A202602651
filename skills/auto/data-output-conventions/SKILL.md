---
name: data-output-conventions
description: Use when cleaning tabular data or producing machine-readable analysis outputs that include money, dates, or metadata.
---
# Data Output Conventions

1. Count input rows before deduplication; deduplicate by the specified key before calculating distinct-record metrics.
2. Exclude records with unknown amounts from amount-based calculations and report row counts according to the requested definitions.
3. Represent money as integer minor units; use decimal-safe arithmetic for monetary calculations.
4. Write CSVs with the exact requested header order, one row per qualifying record, and required timestamp and category formats.
5. Include all required metadata fields, using the specified source name and row-count definitions.
6. Validate output files against the requested schema and formatting rules before finishing.
