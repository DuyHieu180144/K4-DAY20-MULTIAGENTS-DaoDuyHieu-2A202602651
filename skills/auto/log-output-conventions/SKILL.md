---
name: log-output-conventions
description: Use when parsing logs and producing structured error summaries for downstream consumers.
---
# Log Output Conventions

1. Normalize service names to lowercase and replace hyphens with underscores.
2. Sort error records by normalized service name, then by UTC timestamp in ascending order.
3. Include the required top-level schema version and generator identifier.
4. Validate the output structure, field names, timestamp format, and ordering before finishing.
