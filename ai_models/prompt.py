def build_prompt(contracts_text: str, config_rows: list) -> str:

    if config_rows:
        checklist_lines = []
        sorted_rows = sorted(config_rows, key=lambda x: int(x.get("OutputOrder") or 99))

        for row in sorted_rows:
            if str(row.get("Enabled", "Yes")).strip().lower() != "yes":
                continue
            checklist_lines.append(
                f'- Section: "{row["Section"]}" | Subject: "{row["Subject"]}" | '
                f'Extract: {row["KeyInfoToExtract"]} | '
                f'Flag risks: {row["KeyRisksToExtract"] or "general risks"} | '
                f'Keywords: {row["Keywords"]}'
            )

        checklist = "\n".join(checklist_lines)
        assessment_instruction = f"""
For each item in the checklist below, analyze the contracts and produce one entry.
Checklist:
{checklist}
"""
    else:
        assessment_instruction = """
No config file was provided. Perform a general assessment.
Use section: "General" and subject: "Overall Assessment".
"""

    return f"""
You are a legal and risk assessment analyst. Analyze the following contract documents.

{assessment_instruction}

Contract Documents:
{contracts_text}

Respond in this exact JSON format with no extra text, no markdown, no backticks:
{{
    "overall_risk": "LOW | MEDIUM | HIGH | CRITICAL",
    "risk_score": <number 0-100>,
    "sections": [
        {{
            "section": "<Section name from checklist, or General if no config>",
            "subject": "<Subject name from checklist, or Overall Assessment if no config>",
            "summary": "<detailed analysis based on KeyInfoToExtract, KeyRisksToExtract and Keywords for this subject>"
        }}
    ],
    "remarks": "<2-3 sentence overall remarks on the project risk>"
}}
"""
