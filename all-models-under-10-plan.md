# All models under $10 — can it be done?

Date: 2026-11-09. No model runs were done for this plan. All numbers are calculated from cost-all-models.json (2026-11-08 prices), models-82.json, and results-all.json after merging Batch 1-A (25 scored, 37 attempted).

## Short answer

Yes, all 43 remaining priced models can be tested for under $10, but only if you trust the realistic / observed-token basis, not the safe basis. On the safe basis it costs $67.69, so no. On the realistic basis it costs $7.73, so yes, with about $2.27 headroom. The honest expected cost, family-adjusted from what the 25 scored models actually cost, is about $12.41, so $10 is tight and one expensive model may have to be left out or done as a 5-finding smoke test instead.

The way that definitely fits under $10, with margin, is two-stage triage: Gemini Stage 1 for all 50 findings, top-tier model only for the uncertain 10 percent. Family-adjusted total for all 43 remaining models: about $1.53. That is the best-ever way, and it is already built in Live Triage.

## What "remaining" means

- Total unique models: 81
- Attempted after Batch 1-A merge: 37 (25 scored, 12 unavailable)
- Remaining unattempted: 44
  - Priced: 43
  - Unpriced: 1, gmicloud/Ripple-65B-Preview, no pricing, cannot be estimated, do not run blind, check live pricing first or run 5 findings and check billed usage
- The 12 unavailable models are already attempted, not in the 44. 3 are permanent (404 / 400 deprecated), 9 are transient 503, worth a cheap 1-finding probe later, not a full 50-finding run.

## Cost bases, same 43 priced models, 50 findings each

| Basis | What it assumes | Total for 43 | Fits under $10, cheapest-first |
|---|---|---|---|
| Safe, 250 prompt + 2500 completion, Sol 4550 prompt | Every finding uses max_tokens, the only hard upper bound | $67.69 | 21 models, cum $9.64, next is Qwen/Qwen3-Coder-480B $0.57 |
| max_tokens 800, 250 prompt + 800 completion, Sol 4550 prompt | Completion capped at 800 | $22.83 | 38 models, cum $9.75, next is gpt-6.1-sol $0.86 |
| Realistic, cost rows, 156 prompt + 246 completion | Observed means from the original 4-model run | $7.73 | All 43, cum $7.73 |
| Observed mean, 155 prompt + 250 completion | Same as realistic, rounded | $7.40 | All 43, cum $7.40 |
| Observed mean tokens, all 25 scored, 205 prompt + 453 completion, 1094 usage rows | Actual mean tokens from results-all.json | $13.45 | 42 models, cum under $10, missing only the most expensive one |
| Family-adjusted expected actual | Realistic x median actual/realistic ratio per vendor, from the 25 scored models | $12.41 | 42 models, cum $8.95, missing only gpt-5.4-pro family-adjusted $3.46 |
| Two-stage, Gemini Stage 1 + 10% escalation, family-adjusted | $0.00665 Stage 1 for 50 findings per model, plus 10% of the target model's family-adjusted cost | $1.53 | All 43, with $8.47 headroom |

## Why realistic underestimates

Actual cost / realistic cost for the 25 scored models ranges from 0.20x to 7.10x, overall $1.156338 actual vs $0.451 realistic, ratio 2.56x.

- Qwen models: median 5.22x. Qwen3.5-35B 7.10x ($0.188 actual vs $0.027 realistic), Qwen3.5-27B 6.33x ($0.202 vs $0.032), Qwen3.6-35B 4.12x.
- Tencent models: median 3.69x. Hy3 3.79x, hy3-preview 3.58x, hy4 4.23x, hy4-preview 2.70x.
- DeepSeek models: median 1.19x, but R1 3.73x.
- Google models: median 0.21x, actual is cheaper than realistic. Gemini 3.5 Flash Lite 0.20x ($0.0067 vs $0.033), Gemini 3.1 preview 0.23x.
- MiniMax: median 1.40x, MiMo: 0.57x to 1.70x, GLM: 1.41x.

Reason: completion tokens. Observed mean completion is 453 tokens, not 246, median 201, p90 1186, max 5202 (Qwen3.5-35B). Reasoning models think a lot, and reasoning tokens are billed. max_tokens does NOT cap reasoning tokens: in the two-stage smoke test Qwen3.8 produced 2381 and 2794 completion tokens despite max_tokens 800. So the max800 basis, $22.83, is not a hard cap either. The safe basis, $67.69, is the only hard upper bound, because it prices completion at 2500 tokens, the max_tokens used in the full runs.

## The tail

The tail dominates every basis. Safe costs for the 5 most expensive remaining models:
- moonshotai/kimi-k3 $1.91
- openai/gpt-5.5 $3.81
- openai/gpt-5.6-sol $3.81
- openai/gpt-6-astra $6.38
- openai/gpt-5.4-pro $22.88, realistic $2.45, family-adjusted $3.46, observed-mean $2.48

gpt-5.4-pro alone is a third of the remaining safe total. gpt-6-astra is $6.38 safe, $0.69 realistic. Those two should be individual approvals, not bundled into a blanket run, and ideally done as 5-finding smoke tests first: 5 findings at observed mean costs about $0.25 for gpt-5.4-pro, $0.07 for gpt-6-astra.

## Minimum prompt tokens warning

12 remaining models list pricing overrides with min_prompt_tokens in models-82.json, including all the openai/gpt-5.x, gpt-6.x, grok, and Qwen Coder models, e.g. gpt-5.4-pro min 272,000 prompt tokens. If that minimum were actually billed, gpt-5.4-pro alone would cost 50 x 272,000 x $0.00006 = $816 prompt alone, which is absurd and is not what happened in practice: the gpt-6.1-sol smoke test reported about 4510 prompt tokens, not 272,000, and cost $0.009372 per finding. So the overrides are treated as not enforced, with that Sol evidence noted, but it is a risk to check on the first 5 findings of any override model, before running all 50.

## Hard actual-spend stop, the only way $10 holds

Do not run on the safe gate, do not run on the realistic gate alone. Run cheapest-first by realistic cost, and stop immediately when actual billed spend for the run reaches $10.00, even if models remain unrun. Record unrun models as cap-reached, not as zero scores. Check actual spend after each model, from token usage returned by the API, not from the estimate. At the family-adjusted expected cost, $10 gets 42 of 43 models, missing only gpt-5.4-pro. At the observed-mean cost, $10 also gets 42 of 43.

## Cheapest-first order, remaining 43 priced, by realistic cost

nvidia/nemotron-3-ultra-550b-a55b $0.038, Qwen/Qwen3.6-Plus $0.041, Qwen/Qwen3.6-Plus-2026-04-02 $0.041, google/gemini-3-flash-preview $0.041, stepfun-ai/Step-5-Preview $0.041, moonshotai/Kimi-K2.5 $0.042, Qwen/Qwen3.5-122B-A10B $0.042, Qwen/Qwen3.8-27B $0.043, zai-org/GLM-5-FP8 $0.047, Qwen/Qwen3.5-397B-A17B $0.049, google/gemini-3.8-flash $0.052, google/gemini-3.7-flash $0.052, Qwen/Qwen3-235B-A22B-Thinking-2507-FP8 $0.054, deepseek-ai/DeepSeek-V4-Pro $0.056, moonshotai/Kimi-K2.6 $0.057, moonshotai/kimi-k2.7-code $0.057, deepseek-ai/DeepSeek-V4-Pro-0813 $0.059, openai/gpt-5.4-mini $0.061, Qwen/Qwen3-Coder-480B-A35B-Instruct-FP8 $0.062, zai-org/GLM-5.2-FP8 $0.065, zai-org/GLM-5.1-FP8 $0.065, zai-org/GLM-5.3 $0.065, Qwen/Qwen3.8-Max-0902 $0.074, openai/gpt-5.6-luna $0.082, x-ai/grok-4.5 $0.089, xai/grok4.6 $0.089, Qwen/Qwen3.8-Max $0.089, google/gemini-3.6-flash $0.104, Qwen/Qwen3.7-Max $0.112, moonshotai/kimi-k2.7-code-highspeed $0.113, google/gemini-3.5-flash $0.122, google/gemini-4-argon $0.139, openai/gpt-6-sol $0.139, moonshotai/kimi-k3.1-pro $0.139, google/gemini-3.1-pro-preview $0.163, openai/gpt-5.4 $0.204, openai/gpt-5.6-terra $0.204, moonshotai/kimi-k3 $0.208, openai/gpt-5.5 $0.408, openai/gpt-5.6-sol $0.408, openai/gpt-6.1-sol $0.574, openai/gpt-6-astra $0.693, openai/gpt-5.4-pro $2.448. Ripple unpriced, not in this list.

## Recommendation

1. Do not run all 43 as single-model full runs on a $10 budget and expect it to hold. It probably will not, expected $12.41 family-adjusted, $13.45 observed-mean.
2. Run them two-stage instead: Gemini Stage 1, 10% escalation, family-adjusted $1.53 total, all 43 fit with $8.47 headroom. That gives a measured two-stage score for every model, not a single-model score, and it is the cheapest way to test all of them.
3. If single-model scores are required, run cheapest-first with a hard $10 actual-spend stop, 5 findings first for gpt-5.4-pro, gpt-6-astra, gpt-5.5, gpt-5.6-sol, and any override model, and accept that the last 1 or 2 models may be left unrun.
4. Ripple: check live pricing first, or 5 findings only, do not run 50 blind.

No model runs were done for this plan.
