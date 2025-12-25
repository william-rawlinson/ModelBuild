transform_datapoints = """You are given a list of datapoints from a health economic model.

Your task is to convert each datapoint into a model parameter with a clear, concise, and consistent name.

IMPORTANT RULES:
- Each input datapoint MUST result in exactly one output parameter.
- Do NOT drop, merge, or duplicate datapoints.
- Do NOT invent values or distributions. 
- Parameter names must be:
  - snake_case
  - lowercase
  - reasonably short but descriptive
  - valid Python identifiers
- Parameter names should reflect the *meaning* of the datapoint, not just restate the description verbatim.
- Use standard health-economic conventions where possible (e.g. pfs_utility, death_prob_pps).
- If a datapoint is ambiguous, still produce a parameter name, but add a short note explaining the ambiguity.
- If you have any of the following datapoints IGNORE THESE, they will be handled separately:
    Time horizon
    Model cycle length
    Discount rate for QALYs
    Discount rate for costs

INPUT DATAPOINTS:
<datapoints>
{datapoints_json}
</datapoints>

OUTPUT FORMAT:
Return a JSON array. Each element must have the following fields:

- parameter_name: string
- value: number or null
- description: string (can reuse or lightly rephrase the input description)
- distribution: string or null
- standard_error: number or null
- notes: string (optional; include only if something is ambiguous)

EXAMPLE OUTPUT ITEM:
{{
  "parameter_name": "pfs_to_pps_prob",
  "value": 0.12,
  "description": "Per-cycle probability of progression from PFS to PPS",
  "distribution": "beta",
  "standard_error": 0.03
}}

Return ONLY valid JSON. Do not include any explanatory text.
"""