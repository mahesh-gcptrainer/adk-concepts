---
name: sla-auditor
description: Audits API endpoint latencies, calculates statistical percentiles (P50,
  P95, P99), checks compliance against a configurable SLA threshold (defaulting to
  200ms), and generates a formatted Markdown report. This skill helps in evaluating
  API performance and adherence to service level agreements.
---

# SLA Auditor Skill

## Objective
- To audit a given set of API latencies, calculate key statistical percentiles (P50, P95, P99), and determine SLA compliance against a specified threshold.
- To generate a human-readable Markdown report summarizing the findings.

## Step-by-step procedure
1.  **Prepare Latency Data:** Gather the latency measurements for the API endpoint you wish to audit. This should be a list of numerical values, typically in milliseconds.
2.  **Invoke the Skill:** Call the `run_code` function, providing the latency data, an optional API name, and an optional SLA threshold.
    -   `latencies`: A list of numbers (integers or floats) representing the latency measurements in milliseconds.
    -   `api_name`: (Optional) A string identifier for the API endpoint being audited (e.g., "User Service API"). Defaults to "API Endpoint".
    -   `sla_threshold_ms`: (Optional) An integer representing the SLA threshold for the P95 latency in milliseconds. Defaults to 200ms.
3.  **Receive Report:** The skill will return a Markdown formatted string containing the SLA audit report.

## Expected Input Format
The `run_code` function expects a Python dictionary with the following keys:
-   `latencies` (required): `list[float | int]` - A list of latency values in milliseconds.
-   `api_name` (optional): `str` - The name of the API endpoint. Default is "API Endpoint".
-   `sla_threshold_ms` (optional): `int` - The SLA threshold for P95 latency in milliseconds. Default is 200.

### Example Input for `run_code`
```python
{
    'latencies': [120, 150, 210, 80, 300, 195, 180, 220, 160, 175],
    'api_name': 'Payment Gateway API',
    'sla_threshold_ms': 250
}
```

## Expected Output Format
A Markdown formatted string representing the SLA report. The report will include:
-   API Name
-   Total number of requests
-   Configured SLA Threshold (P95)
-   SLA Compliance Status (COMPLIANT or NON-COMPLIANT)
-   P50 (Median) Latency
-   P95 Latency
-   P99 Latency
-   A sample of the raw latency data

## Edge Cases and Guidelines
-   **No Latency Data:** If an empty list or `None` is provided for `latencies`, the skill will report "No latency data provided."
-   **Non-numeric Latencies:** Ensure all values in the `latencies` list are numeric (integers or floats). Non-numeric values will cause a runtime error.
-   **Single Data Point:** While statistically less meaningful, the skill can process a single latency value. Percentiles will reflect this single point.
-   **Threshold Interpretation:** The SLA threshold is applied to the P95 latency. The service is considered compliant if P95 is *less than or equal to* the threshold.
-   **Units:** All latencies and the SLA threshold are assumed to be in milliseconds (ms).
