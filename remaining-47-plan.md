# Remaining 47 models plan — Security Model Benchmark

Prepared 2026-11-09. No new model runs were made for this plan. No new GMI spend.
Sources, verified against each other: `cost-all-models.json` (80 priced rows),
`models-82.json` (82 entries, 81 unique IDs), `results-all.json` (34 attempted,
22 scored, 12 unavailable).

## Status so far

- 81 unique models in the live list. 80 have flat per-token pricing. 1 does not.
- Attempted: 34 (4 original + 30 cheapest untested). Scored: 22. Unavailable: 12.
- Spent in the all-models pass: $0.696507 (results-all.json).
- Grand total for the whole project, estimated about $0.75: $0.696507 + smoke
  $0.003569 + lost batch-1 duplicate first runs $0.015767 + Hy3 partial first
  run about $0.007 + about $0.026 unrecorded from 4 crashed
  deepseek-v4.1-flash-1017 attempts. Exact sum $0.748843. Well under the $5 cap.
- Runner bug fixed 2026-11-09: `run_benchmark.py` now catches socket
  TimeoutError / URLError timeouts, retries once with a 300s timeout, records
  the retry, and records the finding as unparsed if it still times out,
  instead of crashing the run. Verified with 5 mocked timeout tests and a
  live `--estimate-only` run, no new model calls.

## Remaining: 47 models

46 priced + 1 unpriced. Sorted cheapest to most expensive by safe cost for
50 findings on the v1 dataset.

Safe basis: 250 prompt tokens (4550 for openai/gpt-6.1-sol) + 2500 completion
tokens per finding x 50. Realistic basis: 156 prompt + 246 completion tokens
per finding x 50, observed means from results.json.

| # | Model | Safe $/50 | Realistic $/50 | Cum safe $ | Cum realistic $ |
|---|---|---|---|---|---|
| 1 | Qwen/Qwen3.5-27B | 0.3038 | 0.0319 | 0.3038 | 0.0319 |
| 2 | tencent/hy4 | 0.3231 | 0.0373 | 0.6268 | 0.0691 |
| 3 | tencent/hy4-preview | 0.3231 | 0.0373 | 0.9499 | 0.1064 |
| 4 | nvidia/nemotron-3-ultra-550b-a55b | 0.3350 | 0.0382 | 1.2849 | 0.1446 |
| 5 | stepfun-ai/Step-5-Preview | 0.3500 | 0.0410 | 1.6349 | 0.1856 |
| 6 | google/gemini-3-flash-preview | 0.3813 | 0.0408 | 2.0161 | 0.2264 |
| 7 | Qwen/Qwen3.6-Plus | 0.3813 | 0.0408 | 2.3974 | 0.2672 |
| 8 | Qwen/Qwen3.6-Plus-2026-04-02 | 0.3813 | 0.0408 | 2.7786 | 0.3080 |
| 9 | moonshotai/Kimi-K2.5 | 0.3825 | 0.0416 | 3.1611 | 0.3496 |
| 10 | Qwen/Qwen3.5-122B-A10B | 0.4050 | 0.0425 | 3.5661 | 0.3921 |
| 11 | Qwen/Qwen3.8-27B | 0.4056 | 0.0429 | 3.9718 | 0.4350 |
| 12 | zai-org/GLM-5-FP8 | 0.4125 | 0.0472 | 4.3843 | 0.4821 |
| 13 | deepseek-ai/DeepSeek-V4-Pro | 0.4568 | 0.0564 | 4.8410 | 0.5385 |
| 14 | Qwen/Qwen3.5-397B-A17B | 0.4575 | 0.0490 | 5.2985 | 0.5875 |
| 15 | google/gemini-3.8-flash | 0.4781 | 0.0520 | 5.7766 | 0.6394 |
| 16 | google/gemini-3.7-flash | 0.4781 | 0.0520 | 6.2548 | 0.6914 |
| 17 | deepseek-ai/DeepSeek-V4-Pro-0813 | 0.5115 | 0.0590 | 6.7663 | 0.7504 |
| 18 | moonshotai/Kimi-K2.6 | 0.5119 | 0.0566 | 7.2781 | 0.8070 |
| 19 | moonshotai/kimi-k2.7-code | 0.5119 | 0.0566 | 7.7900 | 0.8636 |
| 20 | Qwen/Qwen3-235B-A22B-Thinking-2507-FP8 | 0.5294 | 0.0544 | 8.3194 | 0.9180 |
| 21 | zai-org/GLM-5.2-FP8 | 0.5675 | 0.0650 | 8.8869 | 0.9830 |
| 22 | zai-org/GLM-5.1-FP8 | 0.5675 | 0.0650 | 9.4544 | 1.0481 |
| 23 | zai-org/GLM-5.3 | 0.5675 | 0.0650 | 10.0219 | 1.1131 |
| 24 | openai/gpt-5.4-mini | 0.5719 | 0.0612 | 10.5938 | 1.1743 |
| 25 | Qwen/Qwen3-Coder-480B-A35B-Instruct-FP8 | 0.5738 | 0.0624 | 11.1675 | 1.2367 |
| 26 | Qwen/Qwen3.8-Max-0902 | 0.6395 | 0.0738 | 11.8070 | 1.3104 |
| 27 | openai/gpt-5.6-luna | 0.7625 | 0.0816 | 12.5695 | 1.3920 |
| 28 | Qwen/Qwen3.8-Max | 0.7750 | 0.0894 | 13.3445 | 1.4814 |
| 29 | x-ai/grok-4.5 | 0.7750 | 0.0894 | 14.1195 | 1.5708 |
| 30 | xai/grok4.6 | 0.7750 | 0.0894 | 14.8945 | 1.6603 |
| 31 | google/gemini-3.6-flash | 0.9563 | 0.1040 | 15.8508 | 1.7642 |
| 32 | Qwen/Qwen3.7-Max | 0.9688 | 0.1118 | 16.8195 | 1.8760 |
| 33 | moonshotai/kimi-k2.7-code-highspeed | 1.0238 | 0.1132 | 17.8433 | 1.9892 |
| 34 | google/gemini-3.5-flash | 1.1438 | 0.1224 | 18.9870 | 2.1116 |
| 35 | google/gemini-4-argon | 1.2750 | 0.1386 | 20.2620 | 2.2502 |
| 36 | openai/gpt-6-sol | 1.2750 | 0.1386 | 21.5370 | 2.3888 |
| 37 | moonshotai/kimi-k3.1-pro | 1.2750 | 0.1386 | 22.8120 | 2.5274 |
| 38 | google/gemini-3.1-pro-preview | 1.5250 | 0.1632 | 24.3370 | 2.6906 |
| 39 | openai/gpt-6.1-sol | 1.7050 | 0.5740 | 26.0420 | 3.2646 |
| 40 | openai/gpt-5.6-terra | 1.9063 | 0.2040 | 27.9482 | 3.4686 |
| 41 | openai/gpt-5.4 | 1.9063 | 0.2040 | 29.8545 | 3.6726 |
| 42 | moonshotai/kimi-k3 | 1.9125 | 0.2079 | 31.7670 | 3.8805 |
| 43 | openai/gpt-5.6-sol | 3.8125 | 0.4080 | 35.5795 | 4.2885 |
| 44 | openai/gpt-5.5 | 3.8125 | 0.4080 | 39.3920 | 4.6965 |
| 45 | openai/gpt-6-astra | 6.3750 | 0.6930 | 45.7670 | 5.3895 |
| 46 | openai/gpt-5.4-pro | 22.8750 | 2.4480 | 68.6420 | 7.8375 |
| 47 | gmicloud/Ripple-65B-Preview | unknown, no pricing in list | unknown | — | — |

Remaining totals: safe $68.6420, realistic $7.8375, for the 46 priced models.
Ripple cannot be estimated. Do not run it blind: check live pricing first,
or run 5 findings and check billed usage before a full 50.

## Gate choice

- Safe gate: total for all 80 priced models $73.53. Remaining safe $68.64.
  A safe budget would need about $74 in total, $69 more. Safe never
  underestimates on token counts, because 2500 completion tokens is
  max_tokens. The risk is only price changes.
- Realistic gate: total for all 80 priced models $8.38. Remaining realistic
  $7.84. A realistic budget of about $10 would cover all 46 priced remaining
  models in expectation. The risk is real: realistic underestimates reasoning
  models. DeepSeek F07 burned all 2500 completion tokens on one finding,
  $0.00305 vs $0.000408 on the old estimate. Actual spend so far is about
  14% of safe cumulative ($0.6965 actual vs $4.886 safe for the 34 attempted),
  so realistic has been close in aggregate, but a single reasoning-heavy
  model can spike. gpt-5.4-pro alone is $22.88 safe vs $2.45 realistic.
- Batches by budget:
  - $10 safe: first 22 remaining, $9.4544 safe, about $1.05 realistic.
  - $10 realistic: all 46 priced remaining, $7.8375 realistic, $68.64 safe.
  - $25 safe: first 38 remaining, $24.3370 safe, about $2.69 realistic.
  - $25 realistic: all 46, with $17 headroom over the $7.84 realistic total.

## Unavailable models: retry or not

12 models were unavailable on 2026-11-08, verified by a direct single chat
call each. They are NOT zero scores.

Permanent, do not retry:
- inclusionAI/Ling-3.0-flash-fin: HTTP 404, no matching target server
- moonshotai/Kimi-K2-Thinking: HTTP 404, no matching target server
- zai-org/GLM-4.7-FP8: HTTP 400, model deprecated and no longer available

Transient, worth retrying later (one cheap single-finding probe each first):
- google/gemma-4-26b-a4b-it: HTTP 503, max retries exhausted, last status 523
- google/gemma-4-31b-it: HTTP 503, max retries exhausted, last status 523
- stepfun-ai/Step-3.7-Flash: HTTP 503, max retries exhausted, last status 523
- moonshotai/Kimi-K2-Instruct-0905: HTTP 503, max retries exhausted, last status 523
- Qwen/Qwen3-Next-80B-A3B-Instruct: HTTP 503, max retries exhausted, last status 523
- Qwen/Qwen3-Next-80B-A3B-Thinking: HTTP 503, max retries exhausted, last status 523
- openai/gpt-5.4-nano: HTTP 503, max retries exhausted, last status 523
- Qwen/Qwen3-235B-A22B-Instruct-2507-FP8: HTTP 503 routing, no eligible worker, code no_capacity
- openai/gpt-6-luna: HTTP 503 routing, no eligible worker, code no_capacity

## Recommendation

Run Batch 1 first: the next 22 cheapest remaining models (#1-22 above),
safe gate, $10 budget. Safe cost $9.4544, expected realistic cost about
$1.05. No single model in this batch costs more than $0.57 safe. That takes
the benchmark to 56 of 81 models attempted, with the expensive tail still
unrun and still a separate decision.

Then, only after Batch 1 actuals are in, decide Batch 2: the remaining 24
priced models (#23-46, safe $59.19, realistic $6.79), plus Ripple if its
pricing can be checked. gpt-5.4-pro ($22.88 safe, $2.45 realistic) and
gpt-6-astra ($6.38 safe, $0.69 realistic) should be individual approvals,
not bundled into a blanket run, because Pro alone is a third of the safe
total for all remaining models.

Do not run anything under a realistic-only gate without a hard actual-spend
stop: the runner's $5 hard cap must be raised explicitly for the batch, and
the run must stop if actual billed spend reaches the approved budget, even
if the realistic estimate said it would fit.
