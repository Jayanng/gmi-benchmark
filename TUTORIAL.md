# Tutorial: Benchmark GMI Models on Security Triage

Build a fixed benchmark that tests how well GMI Cloud Inference Engine models tell a real vulnerability from a false positive, and publish the results on a dashboard.

GMI products used: Inference Engine only. No AgentBox, no GMI Studio, no Cluster Engine. That is deliberate, because the API key used here is inference-only.

## What you will build

1. A fixed dataset of 50 labelled findings, 25 real and 25 false positives.
2. A runner that sends the same prompt and the same 50 findings to 4 GMI models.
3. A dashboard that shows the leaderboard, charts, and every finding with each model's verdict.

## Step 1: Pick models that actually exist

Do not trust the docs example. Call list-models first and pick from the live list:

```bash
python3 ~/workspace/custom-connectors/custom.gmi-cloud/bin/gmi-cloud.py list-models
```

On 2026-11-08 that returned 82 models. The docs example `meta-llama/Llama-3.3-70B-Instruct` was NOT in the list, so it was not used. The four cheapest fast models picked were:

- `zai-org/GLM-5.3-Flash` - $0.000000150 prompt, $0.000000500 completion per token
- `deepseek-ai/DeepSeek-V4.1-Flash` - $0.000000300 prompt, $0.000001200 completion
- `Qwen/Qwen3.8-Flash` - $0.000000160 prompt, $0.000000470 completion
- `google/gemini-3.5-flash-lite` - $0.000000300 prompt, $0.000002500 completion

## Step 2: Build a fixed dataset

Write 50 short, generic code snippets. Half must be real vulnerabilities, half must be false positives where a mitigation is present in the code shown: parameterised SQL, escaped templates, allowlisted URLs, ownership checks, safe loaders, verified JWT signatures, and so on.

Each finding needs: id, category, severity, expected label, title, code, explanation. Keep the labels honest. A finding is real only if untrusted input actually reaches a dangerous sink with no effective mitigation in the code shown. Save it as `dataset.json` so anyone can re-run the same test and get comparable numbers.

Do not use private findings from real repos. Use generic, public-style examples only.

## Step 3: Write the runner

One prompt, same for every model and every finding:

> Classify this code finding. Return ONLY JSON: {"verdict": "real" or "false_positive", "severity": "critical|high|medium|low", "reason": "one short sentence"}

Set temperature 0 so results are repeatable. Set max_tokens to at least 1000. Some models spend most of that budget on reasoning tokens and return an empty answer, so plan a re-run at 2500 tokens for any unparsed answer, and record unparsed answers as unparsed, do not guess them.

Measure, for each model: true positives, false positives, true negatives, false negatives, precision, recall, F1, accuracy, average latency per finding, and cost per finding from the token usage the API returns and the per-token prices in the models list.

Run a 5-finding smoke test first. On 2026-11-08 that cost $0.003569 for 5 findings x 4 models. Only then run the full 50. For a cost estimate, use the safe upper bound in run_benchmark.py: 250 prompt tokens (4550 for openai/gpt-6.1-sol, observed) + 2500 completion tokens per finding. The old 160 + 300 estimate was NOT an upper bound, do not use it. Safe upper bounds for 50 findings, verified 2026-11-08: GLM $0.064, DeepSeek $0.154, Qwen $0.061, Gemini $0.316, Sol $1.705, all five together $2.30, under the $5 cap.

## Step 4: Read the results

On 2026-11-08, full run, 50 findings x 4 models, 200 calls:

| Model | Precision | Recall | F1 | Accuracy | Avg latency | Cost per finding | Total |
|---|---|---|---|---|---|---|---|
| Qwen/Qwen3.8-Flash | 1.000 | 1.000 | 1.000 | 1.000 | 3.85 s | $0.000157 | $0.007836 |
| google/gemini-3.5-flash-lite | 1.000 | 1.000 | 1.000 | 1.000 | 2.87 s | $0.000133 | $0.006663 |
| zai-org/GLM-5.3-Flash | 0.962 | 1.000 | 0.980 | 0.980 | 3.53 s | $0.000207 | $0.010345 |
| deepseek-ai/DeepSeek-V4.1-Flash | 1.000 | 1.000 | 1.000 | 0.980 | 4.09 s | $0.000539 | $0.026937 |

Total full run plus re-run: $0.051781. Total project spend including the smoke test: $0.055350. Budget cap was $5.

The two misses, stated plainly: GLM called F17, a JWT test with a mock key, real when it is a false positive. DeepSeek returned no verdict at all for F07, a path-traversal check that stays inside the base directory, even after a 2500-token re-run, because reasoning tokens filled the budget. That is a real failure mode for reasoning models on this task, and it is the reason DeepSeek costs the most and is the slowest here despite perfect precision and recall on parsed answers.

Fastest was Gemini at 2.87 seconds per finding. Cheapest per finding was also Gemini at $0.000133, followed by Qwen at $0.000157. Qwen and Gemini were the best value here: perfect scores, fast, and cheap.

## Step 5: Make it reusable

Keep the dataset, runner, and results in one folder, with a README that records the date, the model IDs, the prices, the total cost, and any unparsed answers. Anyone should be able to re-run `python3 run_benchmark.py` and compare their numbers to yours. That is what makes this a benchmark, not a one-off test.

Next steps, if you want to go further: run the balanced v2 dataset, dataset-v2.json, 56 findings, 14 categories x 4 each, 28 real, 28 false positives. It has NOT been run yet, no v2 results exist. Safe upper-bound cost to run v2 on the 4 original models is $0.67 total. Add borderline cases that are harder than textbook examples, add more models, or test the same models with a longer reasoning budget and record whether the extra tokens are worth the cost.

## Step 6, v2: Use Live Triage with your own key

The v2 dashboard has a Live Triage section. It is the part that handles real stuff, not just the 50 textbook findings.

1. Paste real code, a real semgrep or osv finding, a CVE description, or a code snippet into the input box. Three pre-filled examples are there to load with one click: real SQL injection, real JWT verification disabled, and a false positive with a parameterised query.
2. Pick a model from the selector. All 82 verified models are listed, with real prices. The 4 tested models have full benchmark scores. Strong models like openai/gpt-6.1-sol are labelled UNTESTED, with real prices and no invented scores.
3. Enter your own GMI API key in the key field. Your key stays in your browser, in sessionStorage only. It is never sent to our server, never stored in localStorage, never logged. It is only used to call https://api.gmi-serving.com/v1 directly from your browser. Clear it anytime with the Clear key button. If no key is entered, Live Triage stays disabled and tells you why.
4. Press Triage. The page calls POST https://api.gmi-serving.com/v1/chat/completions with temperature 0 and max_tokens 2500, and shows the live verdict (real or false positive), severity, confidence, reason, suggested fix, latency, and token usage. If the call fails, it shows the error honestly: 401 means the key is invalid, 404 means the model was not found, 429 means rate limited. It never invents a verdict.
5. To run the full 50-finding benchmark on a model you choose, use the Run benchmark control, check the cost estimate shown before running. The estimate is now a safe upper bound: 250 prompt tokens (4550 for Sol) + 2500 completion tokens per finding, so a real run cannot exceed it on token counts. Safe upper bound for Sol on 50 findings is $1.705, not the old $0.47 projection, which used the unsafe 160 + 300 estimate. Do not run an expensive model on all 50 findings without checking that estimate first, and note the $5 cap warning.

## Links

- Frontend dashboard: see the live link in the project report.
- Dataset, runner, and full results: `~/workspace/gmi-clouder/security-benchmark/` - `dataset.json`, `run_benchmark.py`, `results.json`.
- GMI Cloud: https://www.gmicloud.ai/ - Inference Engine, https://api.gmi-serving.com/v1


## Fixes, 2026-11-08, fix-everything pass

- Mobile: tab bar and leaderboard table no longer overflow sideways on phone.
- Cost estimator: safe upper bound, 250 + 2500 tokens, Sol 4550 prompt tokens, old 160 + 300 estimate removed.
- Dataset v2: balanced 56-finding dataset in dataset-v2.json, not yet run, v1 results unchanged.
- F17: contestable label kept, with a second reviewer note: if this were production auth, the label would be real, severity high.
- Sol smoke anomaly: investigated, no runner bug, extra prompt tokens are provider-side cached tokens, about 3801 per row.
- Re-run note: 4 of 5 null verdicts parsed on re-run, DeepSeek F07 remained unparsed.
