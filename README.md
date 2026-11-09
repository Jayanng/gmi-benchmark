## v2, 2026-11-08: real GMI theme, Live Triage, your own key

v1 used a dark navy theme (#05070d) with blue/teal accents. That was wrong.

Theme verification, two checks, 2026-11-08:
- My own CSS check, from GMI's live stylesheet at https://www.gmicloud.ai/_next/static/chunks/14_o4m.30b0m6.css: design tokens are light by default, page #f6f6f6, text #000000, brand lime #ddea4d, secondary #99a22f, fonts Inter / Geist Mono.
- The separate live browser check, desktop 1919x998, https://www.gmicloud.ai/en, https://www.gmicloud.ai/en/developer-demos, https://docs.gmicloud.ai/, is authoritative for what the site actually looks like, and it overrides the CSS tokens for the visual design: the site alternates black and white sections. Page/header/hero black #000000, primary/accent lime #DDEA4D, white #FFFFFF sections, hero subhead light grey #DBD7D6, card borders on black #404040 1px, cards #000000 on black, white-section background #FFFFFF with a very light grey dot-grid, final CTA full-width lime #DDEA4D with black heading, footer #000000, lime is the ONLY accent, no blue link colour, lime dot "●" before eyebrow labels, docs sidebar active pale lime #E4E7D1. Headings are clean geometric sans, normal/medium weight, NOT heavy bold, tight letter spacing, hero ~400-500, section headings ~500-600, font family name NOT verified, so no font name is claimed as GMI's. Body, eyebrows, nav, buttons, prices are monospace, eyebrows uppercase mono wide letter-spacing, buttons ALL CAPS monospace letter-spaced. Sizes at 1919px: hero H1 ~72-80px, section H2 ~48-56px, H3 ~20-24px, body mono ~15-16px, header nav ~14-15px, header buttons 36px tall, hero CTA ~43px tall, spacing 80-120px between sections, max-width ~1500px, sharp corners, 0 border-radius. Header sticky black #000000 ~65px. Hero background is NOT flat colour: full-bleed dark desaturated looping video/photo behind a dark overlay. Mobile layout NOT VERIFIED, no viewport-resize was possible, so v2 uses standard responsive stacking, single column, and notes mobile as unverified.
- The v2 frontend follows the browser spec exactly, not the old dark navy theme and not a whole-page light theme.

v2 adds Live Triage: paste real code, a real semgrep/osv finding, a CVE description, or a code snippet, pick any of the 82 verified models, enter your own GMI API key, and get a live verdict from https://api.gmi-serving.com/v1/chat/completions, temperature 0, max_tokens 2500. The key is stored in sessionStorage only, never in localStorage, never logged, never sent anywhere except directly to api.gmi-serving.com from your browser, and you can clear it anytime. Errors are shown honestly (401 invalid key, 404 model not found, 429 rate limit, unparsed answer). No verdict is invented.

v2 also adds a model selector for all 82 models (list in `models-82.json`, verified live 2026-11-08) and a recommender by priority (highest accuracy, fastest, cheapest, best value, best for coding/security triage, strongest overall). Strong models are labelled UNTESTED with real prices and no invented scores, including openai/gpt-6.1-sol, openai/gpt-6-sol, openai/gpt-5.6-sol, openai/gpt-5.4-pro, deepseek-ai/DeepSeek-V4-Pro, nvidia/nemotron-3-ultra-550b-a55b, Qwen/Qwen3-235B-A22B-Instruct-2507-FP8, moonshotai/Kimi-K2.5, Qwen/Qwen3-Coder-480B-A35B-Instruct-FP8. The docs example meta-llama/Llama-3.3-70B-Instruct is NOT in the list and is not listed as available.

Strong-model smoke test, verified 2026-11-08, openai/gpt-6.1-sol on 5 findings only: precision 1.000, recall 1.000, accuracy 1.000, avg latency 4.19 s, cost per finding $0.009372, total $0.046858. That is a 5-finding smoke test, NOT a full 50-finding benchmark. No full run on an expensive model was done, to stay under the $5 cap. Additional GMI cost for v2 work: $0.00, no new model calls were made for the redesign itself; the only live call in this task was a fresh list-models call, which is free.

## What is in this folder

- `dataset.json` - 50 labelled findings, 25 real and 25 false positives, across 14 categories: sql-injection, xss, ssrf, path-traversal, command-injection, hardcoded-secret, weak-crypto, insecure-deserialization, jwt, auth-bypass, idor, csrf, open-redirect, sensitive-data. Each finding has an id, category, severity, expected label, title, code snippet, and explanation. All examples are generic, public-style snippets. No private finding is used. Categories in v1 are NOT balanced: 11 categories have 4 findings each, path-traversal, csrf, and open-redirect have 2 each.
- `dataset-v2.json` - NEW, 2026-11-08, balanced dataset: 56 findings, 14 categories x 4 each, 28 real, 28 false positives, adding S26-S28 and F26-F28, one real and one false positive each for path-traversal, csrf, and open-redirect. v2 has NOT been run against any model yet, no v2 results exist, do not treat v1 results as v2 results. Safe upper-bound cost to run v2 on the 4 original models: $0.67 total. v1 results in `results.json` are unchanged and exact.
- `run_benchmark.py` - runner. Calls GMI Inference at https://api.gmi-serving.com/v1/chat/completions through the registered GMI Cloud credential, never with a pasted key. Same prompt, same findings, every model. Temperature 0, max_tokens 2500. Cost estimator is now a SAFE upper bound: 250 prompt tokens (4550 for openai/gpt-6.1-sol, observed) + 2500 completion tokens per finding. The old 160 + 300 estimate was NOT an upper bound and was removed. Safe upper bounds for 50 findings, verified by `--estimate-only` on 2026-11-08: GLM $0.064, DeepSeek $0.154, Qwen $0.061, Gemini $0.316, Sol $1.705, all five together $2.30, under the $5 cap.
- `results.json` - full results, per model and per finding, with token usage, latency, and cost. Notes fixed 2026-11-08: the re-run note now says 4 of 5 null verdicts parsed, DeepSeek F07 remained unparsed, not all 5. Sol prompt-token note now records the investigation: runner sends the same ~150-token prompt to every model, Sol rows report ~3801 cached tokens per row, so the extra tokens are provider-side, not a runner bug. F17 note now includes the second reviewer note.
- `models-82.json` - all 82 models from the live list-models call on 2026-11-08, with per-token prices and context length. One model, gmicloud/Ripple-65B-Preview, has no pricing in the list.
- `TUTORIAL.md` - how to build it, run it, and read the results.

## Fixes, 2026-11-08, fix-everything pass

- Mobile scrolling: tab bar and leaderboard table no longer overflow sideways on phone. Tabs wrap, tables scroll inside their own container with a clear indicator, no page-wide horizontal scroll. Verified at phone width in the frontend rebuild.
- Cost estimator: now a safe upper bound, 250 prompt tokens (4550 for Sol, observed) + 2500 completion tokens per finding. Old 160 + 300 estimate removed everywhere.
- Dataset balance: v1 stays 50 findings, unbalanced, results unchanged. Balanced v2 is a separate file, `dataset-v2.json`, 56 findings, 14 categories x 4 each, 28 real, 28 false positives, not yet run.
- F17: original false_positive label kept, plus a second reviewer note in `dataset.json` and in `results.json` notes: if this were production auth, not a test, the label would be real, severity high.
- Sol smoke anomaly: investigated, no runner bug. Runner sends the same ~150-token prompt to every model, Sol rows report ~3801 cached tokens per row, so the extra tokens are provider-side. Estimator now uses 4550 prompt tokens for Sol.
- Re-run note fixed: 4 of 5 null verdicts parsed on re-run, DeepSeek F07 remained unparsed, not all 5.

## Models tested, 2026-11-08

All four model IDs were verified live against a fresh list-models call on 2026-11-08, 82 models total, pricing unchanged from models-2026-11-08.json. The docs example meta-llama/Llama-3.3-70B-Instruct is NOT in the list and was NOT used.

| Model | Precision | Recall | F1 | Accuracy | Avg latency | Cost per finding | Total cost |
|---|---|---|---|---|---|---|---|
| Qwen/Qwen3.8-Flash | 1.000 | 1.000 | 1.000 | 1.000 | 3.85 s | $0.000157 | $0.007836 |
| google/gemini-3.5-flash-lite | 1.000 | 1.000 | 1.000 | 1.000 | 2.87 s | $0.000133 | $0.006663 |
| zai-org/GLM-5.3-Flash | 0.962 | 1.000 | 0.980 | 0.980 | 3.53 s | $0.000207 | $0.010345 |
| deepseek-ai/DeepSeek-V4.1-Flash | 1.000 | 1.000 | 1.000 | 0.980 | 4.09 s | $0.000539 | $0.026937 |

Total for the full 50-finding run plus the targeted re-run: $0.051781. Including the earlier 5-finding smoke test ($0.003569), total project spend was $0.055350. Budget cap was $5. Well under cap.

## What the numbers mean, honestly

- Qwen and Gemini were perfect on this dataset: 25/25 real caught, 25/25 false positives dismissed, no missed verdicts.
- GLM missed one: F17, a JWT test with a mock key, expected false positive, GLM called it real. That is its single false positive, precision 0.962.
- DeepSeek missed one verdict, not one classification: F07, a path-traversal check that stays inside the base directory, expected false positive. Its answer was empty even after a 2500-token re-run, because reasoning tokens filled the whole budget. That is recorded as unparsed, accuracy 0.98, precision and recall 1.000 on the 49 parsed answers.
- The dataset is deliberately clear-cut, so perfect scores here mean the models handle textbook cases well. They do not prove the models would score the same on subtle, real-world code. A harder dataset with borderline cases would separate the models more.

## How to re-run

```bash
cd ~/workspace/gmi-clouder/security-benchmark
python3 run_benchmark.py --limit 5   # smoke test, 5 findings
python3 run_benchmark.py             # full run, 50 findings x 4 models
```

Cost is calculated from token usage returned by the API and the per-token prices in the models list. No cost, latency, or verdict is invented: every row in results.json comes from a live API response, or is recorded as unparsed when no verdict could be extracted.

## Audit notes, 2026-11-08

- Fresh list-models call: 82 models, IDs and prices for the four tested models match the saved list exactly.
- Dataset labels checked: 50 unique IDs, 25 real, 25 false positive, every code snippet matches its explanation.
- Initial run had 5 unparsed verdicts, all reasoning-token overflow at max_tokens 1000. Re-run at 2500 tokens resolved 4 of 5. The remaining one, DeepSeek F07, is still unparsed and is shown as such in the dashboard, not hidden.
- Unverified: balance and credits in the GMI Console, AgentBox, and GMI Studio were not checked through this API key, which is inference-only. The console sign-in via the cloud browser failed, so those parts are out of scope for this project.

## All-models run, 2026-11-08 (34 models attempted, v1 dataset, 50 findings)

Cost to run all 80 priced unique models on 50 findings: safe upper bound $73.53, realistic estimate $8.38 (156 prompt + 246 completion tokens per finding, observed means). One model, gmicloud/Ripple-65B-Preview, has no pricing and cannot be estimated. All 81 unique models do NOT fit in the $5 cap.

Gate used: cumulative safe cost, not realistic, because realistic underestimates reasoning models (DeepSeek F07 used 2500 completion tokens). 4 original + 30 cheapest untested models: cumulative safe $4.886, under the $5 cap. The 31st cheapest untested model, Qwen/Qwen3.5-27B (safe $0.304), would push safe cumulative to $5.19, so it was NOT run.

Total actually spent in this pass (results-all.json): $0.696507. Grand total billed for the whole benchmark project, estimated about $0.75 (results-all $0.696507 + prior smoke $0.003569 + lost batch-1 duplicate first runs $0.015767 + Hy3 partial first run about $0.007, exact cost lost with its log, + about $0.026 unrecorded from 4 crashed deepseek-v4.1-flash-1017 attempts, 70 billed calls lost to an uncaught socket TimeoutError in the runner), still well under the $5 cap. Runner bug FIXED 2026-11-09: run_benchmark.py now catches socket TimeoutError / URLError timeouts in chat(), retries the single finding once with a 300s timeout, records the retry, and if it still times out records the finding as unparsed instead of crashing the run. Verified with 5 mocked timeout tests and a live --estimate-only run, no new model calls. The stale grand-total figure in cost-all-models.json was also corrected to $0.749 (exact sum $0.748843, shown as about $0.75) on 2026-11-09.

Scored models, 22, cheapest first by actual cost:

| Model | P | R | F1 | Acc | Latency | Cost | Unparsed |
|---|---|---|---|---|---|---|---|
| XiaomiMiMo/MiMo-V2.6-Flash | 0.926 | 1.000 | 0.962 | 0.960 | 5.21s | $0.002579 | 0 |
| deepseek-ai/DeepSeek-V3-0324 | 0.852 | 1.000 | 0.920 | 0.820 | 1.83s | $0.003640 | 5 |
| google/gemini-3.1-flash-lite-preview | 0.774 | 1.000 | 0.873 | 0.840 | 2.48s | $0.004638 | 1 |
| deepseek-ai/DeepSeek-V4-Flash | 0.893 | 1.000 | 0.943 | 0.920 | 3.77s | $0.005190 | 1 |
| google/gemini-3.5-flash-lite | 1.000 | 1.000 | 1.000 | 1.000 | 2.87s | $0.006663 | 0 |
| MiniMaxAI/MiniMax-M3 | 0.889 | 0.960 | 0.923 | 0.920 | 1.64s | $0.006724 | 0 |
| Qwen/Qwen3.8-Flash | 1.000 | 1.000 | 1.000 | 1.000 | 3.85s | $0.007836 | 0 |
| deepseek-ai/DeepSeek-V3.2 | 0.958 | 0.920 | 0.939 | 0.940 | 5.60s | $0.009028 | 0 |
| zai-org/GLM-5.3-Flash | 0.962 | 1.000 | 0.980 | 0.980 | 3.53s | $0.010345 | 0 |
| MiniMaxAI/MiniMax-M3.1-Flash | 1.000 | 1.000 | 1.000 | 0.980 | 2.86s | $0.011013 | 1 |
| deepseek-ai/deepseek-v4.1-flash-1017 | 1.000 | 0.920 | 0.958 | 0.960 | 1.72s | $0.018812 | 0 |
| deepseek-ai/DeepSeek-V4-Flash-0731 | 0.923 | 1.000 | 0.960 | 0.940 | 3.89s | $0.023197 | 1 |
| deepseek-ai/deepseek-v4-flash-vision-exp | 1.000 | 1.000 | 1.000 | 1.000 | 3.86s | $0.023517 | 0 |
| XiaomiMiMo/MiMo-V2.6-Pro | 0.962 | 1.000 | 0.980 | 0.980 | 5.01s | $0.023911 | 0 |
| MiniMaxAI/MiniMax-M2.7 | 0.862 | 1.000 | 0.926 | 0.920 | 7.77s | $0.025958 | 0 |
| deepseek-ai/DeepSeek-V4.1-Flash | 1.000 | 1.000 | 1.000 | 0.980 | 4.09s | $0.026937 | 1 |
| MiniMaxAI/MiniMax-M2.5 | 1.000 | 1.000 | 1.000 | 0.960 | 9.16s | $0.030323 | 2 |
| tencent/Hy3 | 1.000 | 0.913 | 0.955 | 0.900 | 17.39s | $0.031205 | 3 |
| tencent/hy3-preview | 1.000 | 0.875 | 0.933 | 0.900 | 19.08s | $0.031454 | 2 |
| Qwen/Qwen3.6-35B-A3B | 0.962 | 1.000 | 0.980 | 0.980 | 10.38s | $0.083255 | 0 |
| deepseek-ai/DeepSeek-R1-0528 | 0.920 | 1.000 | 0.958 | 0.840 | 25.60s | $0.121789 | 6 |
| Qwen/Qwen3.5-35B-A3B | 0.926 | 1.000 | 0.962 | 0.960 | 23.24s | $0.188493 | 0 |

Best accuracy 1.000: google/gemini-3.5-flash-lite, Qwen/Qwen3.8-Flash, deepseek-ai/deepseek-v4-flash-vision-exp. Best value remains Gemini 3.5 Flash Lite, $0.006663, perfect. Slowest: DeepSeek R1 25.6s, Qwen 3.5-35B 23.2s, hy3-preview 19.1s, Hy3 17.4s.

Unavailable models, 12, P=0/R=0, unparsed=50, $0 cost. These are NOT zero scores. Each verified by a direct single chat call on 2026-11-08:

- Qwen/Qwen3-235B-A22B-Instruct-2507-FP8: HTTP 503 routing: framework forward exhausted, no eligible worker, code no_capacity
- Qwen/Qwen3-Next-80B-A3B-Instruct: HTTP 503 Max retries exhausted, last_status_code 523
- Qwen/Qwen3-Next-80B-A3B-Thinking: HTTP 503 Max retries exhausted, last_status_code 523
- google/gemma-4-26b-a4b-it: HTTP 503 Max retries exhausted, last_status_code 523
- google/gemma-4-31b-it: HTTP 503 Max retries exhausted, last_status_code 523
- inclusionAI/Ling-3.0-flash-fin: HTTP 404 No matching target server found
- moonshotai/Kimi-K2-Instruct-0905: HTTP 503 Max retries exhausted, last_status_code 523
- moonshotai/Kimi-K2-Thinking: HTTP 404 No matching target server found
- openai/gpt-5.4-nano: HTTP 503 Max retries exhausted, last_status_code 523
- openai/gpt-6-luna: HTTP 503 routing: framework forward exhausted, no eligible worker, code no_capacity
- stepfun-ai/Step-3.7-Flash: HTTP 503 Max retries exhausted, last_status_code 523
- zai-org/GLM-4.7-FP8: HTTP 400 UnavailableModel: model deprecated and no longer available

404 and 400-deprecated are permanent. 503 no_capacity / 523 may be transient and worth retrying later. The 4 batch-1 lost models (Ling, gemma-4-26b, gemma-4-31b, gpt-6-luna) have no per-finding rows in results-all.json, marked as flagged entries. Batch 1 was lost when its process died before writing output; its scored models were re-run to separate files and the re-runs are canonical. Re-run scores differ slightly from the lost first run despite temperature 0 (reasoning nondeterminism). Lost first-run summaries: DeepSeek-V4-Flash P0.893 R1.000 Acc0.940 $0.004332; MiMo-V2.6-Flash P0.962 R1.000 Acc0.980 $0.002489; DeepSeek-V3.2 P0.962 R1.000 Acc0.980 $0.008946.

Left to run: 47 models (46 priced + Ripple unpriced). Cheapest remaining, safe cost for 50 findings: Qwen/Qwen3.5-27B $0.304, tencent/hy4 $0.323, tencent/hy4-preview $0.323, nvidia/nemotron-3-ultra-550b-a55b $0.335, stepfun-ai/Step-5-Preview $0.350. Remaining total: safe $68.64, realistic $7.84. Most expensive remaining: openai/gpt-5.5 safe $3.81, openai/gpt-6-astra safe $6.38, openai/gpt-5.4-pro safe $22.88 ($2.45 realistic). A realistic-cost budget of about $10 would cover all 80 priced models, but the safe upper-bound budget for all 80 is $73.53. Running the next batch needs user approval of a higher cap and a decision on safe vs realistic gate. Full cost table: cost-all-models.json.

Frontend leaderboard: rebuilt from results-all.json to show all 34 models, 12 unavailable flagged, and the new cost table.
