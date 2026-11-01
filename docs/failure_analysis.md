# Failure analysis and product release decision

Final exact match: 23/30. The product uses valid schema as a necessary check, not a guarantee of a correct interpretation.

| Cases | Failure | User consequence |
|---|---|---|
| final-07, final-08, final-09 | Model emits shortened filter values outside the schema | Request safely falls back to clarification, so the intended group is not returned |
| final-04 | Group-comparison paraphrase routed to overview | A valid overall result answers the wrong scope |
| final-27, final-28 | Missing duration/skip or paid-subscription fields routed to overview | The response is labeled artist repeat but fails to refuse the unsupported request |
| final-29 | Vague follow-up routed to overview | Should clarify which number the user meant |

Release decision: retain a research prototype with interpreted plan, evidence and limitations visible. Curated successful examples demonstrate the available workflow; they do not represent full benchmark accuracy. Do not claim production readiness or measured analyst productivity gains. Before broader free-text use, prioritize unsupported-intent recognition and filter interpretation, then evaluate on a new independently authored task set. No model or prompt was tuned on the final 30 tasks.

The earlier smaller-model development failure is preserved, as is the first final run before backend bootstrap ordering was stabilized. The backend correction did not change the frozen query-planner prompt or expected answers; the final rerun retained identical intent decisions.
