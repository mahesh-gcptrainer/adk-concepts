import numpy as np

def run(**kwargs):
    latencies = kwargs.get('latencies')
    api_name = kwargs.get('api_name', "API Endpoint")
    sla_threshold_ms = kwargs.get('sla_threshold_ms', 200)

    if not latencies:
        return f"# SLA Report for {api_name}

No latency data provided."

    # Ensure latencies are numeric
    try:
        latencies_array = np.array(latencies, dtype=float)
    except ValueError:
        return f"Error: All latency values must be numeric. Received: {latencies}"

    total_requests = len(latencies_array)

    # Calculate percentiles
    p50 = np.percentile(latencies_array, 50)
    p95 = np.percentile(latencies_array, 95)
    p99 = np.percentile(latencies_array, 99)

    # Check SLA compliance
    sla_compliant = p95 <= sla_threshold_ms
    compliance_status = "✅ COMPLIANT" if sla_compliant else "❌ NON-COMPLIANT"

    report = f"""# SLA Report for {api_name}

## Overview
- Total Requests: {total_requests}
- Configured SLA Threshold (P95): {sla_threshold_ms}ms
- **SLA Compliance Status: {compliance_status}**

## Latency Statistics
- P50 (Median): {p50:.2f}ms
- P95: {p95:.2f}ms
- P99: {p99:.2f}ms

## Raw Data (Sample)
First 10 latencies: {latencies[:10]}
"""
    return report
