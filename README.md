# DMO Assistant — LLM Application Engineering Capstone

A bilingual Arabic/English Data Management Office assistant demonstrating grounded FAQ, validated structured extraction, authorized tools, bilingual prompt-injection guards, Saudi PII masking, evaluation gates, cost metering, caching, fallback, and commercial/open-weight model boundaries.

## Run

### Local reproducible harness
```bash
python make_data.py
PYTHONPATH=src pytest -q
PYTHONPATH=src python run_project.py
```

### Colab / provider-SDK run
Open `DMO_Assistant_Capstone.ipynb` and choose **Runtime → Run all**. The notebook installs `openai`, then runs the project. The `OpenAIProviderAdapter` is the only section allowed to import the provider SDK. Configure the OpenAI-compatible endpoint through environment variables; model ids are resolved through aliases, not business-logic literals.

## Evidence
- `DECISIONS.md` — architecture/model ADRs.
- `data/golden_set.v1.yaml` — 120-case versioned, stratified golden set.
- `prompts/*.md` — versioned prompts and judge rubric.
- `EVALUATION_REPORT.md` — actual harness results and known limitations.
- `BENCHMARKS.md` — actual before/after measurements with eval verdicts.
- `eval/out/run_summary.json` — machine-readable run evidence.

## Safety
Saudi national ID/Iqama-shaped identifiers, mobile numbers, and email addresses are detected and masked before model/log use. Input injection checks are bilingual. The outbound wall blocks canary/system-prompt leakage and outbound PII.

## Training programme
LLM Application Engineering — SDAIA Academy. Add the official cohort dates in the repository metadata when confirmed by the trainee.

SDAIA Academy GitHub: https://github.com/SDAIAAcademy
