# Music Insights Copilot

## Target workflow

A product manager reviewing music discovery evidence repeatedly needs an analyst to switch cohorts, confirm denominators and check whether a conclusion survives a definition change. Help them complete a trustworthy first-pass evidence review with fewer handoffs. This need is a hypothesis, not a reported interview finding.

The product starts from curated questions, accepts supported follow-ups, exposes the interpreted plan, and returns numbers with the underlying parameterized SQL, source checksum and limitations. A decision readout recommends the next evidence to collect. It does not manufacture a root cause.

## Why an LLM

Qwen maps varied English/Chinese requests and prior plan context to a constrained semantic request. DuckDB executes only fixed parameterized templates over real aggregate records. Deterministic rendering supplies the numerical answer. This separates language understanding from arithmetic and avoids executing generated SQL. No fine-tuning, agent swarm or unrestricted warehouse access is needed for the first product scope.

Validation rejects invalid schema and filters. It cannot detect every valid-looking but semantically wrong plan. The benchmark preserves those failures. Clarifications and unsupported requests are first-class outcomes, not fabricated answers.

## Evidence and benchmark

Source aggregates are byte-copied from the sibling real-data project and pinned by SHA-256. The frozen task set is author-written evaluation material, NOT real users, interviews, listening records, or production traffic. One deterministic model generation per question; model load measured separately; all-request timings include failures and execution. Compare with a keyword baseline. A small author benchmark cannot establish user-task improvement or production reliability.

Local model inference uses downloaded open weights; report actual tokenizer counts. Hardware, electricity and cost per successful answer are not measured, so dollar ROI and cost savings are not claimed.

## Live versus showcase

The runnable local application performs actual inference for new questions. The hosted static showcase transparently replays saved actual model runs and disables unsupported free-text inference. No recorded answer is presented as a new live model call.

## Product validation still needed

Ask consenting target users to complete the same evidence-review tasks with the dashboard and with the dashboard plus Copilot. Measure correct task completion, time, corrections and handoffs. Do not claim measured productivity gains until such a study exists. If fixed dashboard views already solve the tasks, retain the simpler product.
