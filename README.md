# Security Audit Tool

Audit real code for vulnerabilities with GMI Cloud models. Paste code or a scanner finding, pick a model, and get a verdict: real or false positive, with severity, confidence, a reason, and a suggested fix.

**Live demo:** https://gmi-benchmark.vercel.app/
**Also live at:** https://jayanng.github.io/gmi-benchmark/
**Built on:** [GMI Cloud Inference Engine](https://www.gmicloud.ai/) — [GMI docs](https://docs.gmicloud.ai/)

No sign-up. No server. No account. You bring your own GMI API key, and you pay for your own calls — typically a fraction of a cent per finding. The author spends $0 when you use the tool.

## What it does

Most code review tools give you a generic summary. This one answers one specific question: **is this finding real, or is it a false positive?**

- Paste real code, a semgrep or osv-scanner finding, or a CVE description.
- Pick any of the 81 unique GMI models. Nothing is pre-selected — you choose.
- Get a verdict of `real` or `false_positive`, plus severity, confidence (0–1), a one-sentence reason, and a one-sentence fix.
- Or paste a GitHub repo link and audit its files, one model call per file.
- Export the result as Markdown or JSON and paste it into a pull request or a bug report.

It is security triage, not generic code review. A finding is only called real if untrusted input actually reaches a dangerous sink with no effective mitigation in the code shown. If the code uses parameterisation, escaping, an allowlist, or another effective mitigation, it is a false positive — and the tool says so, rather than flagging it anyway.

## Who it is for

- Developers who get a scanner alert and want to know whether it matters before they spend an afternoon on it.
- Security reviewers triaging semgrep, osv-scanner, or CVE findings.
- Anyone choosing between GMI models for security work who wants to test them on their own code, not on a canned demo.

## Quick start

1. **Open the live demo** at https://gmi-benchmark.vercel.app/
2. **Enter your GMI API key** in the key field and press **Test Key**. A good key returns your model list; a bad key returns 401. Test Key calls `GET /v1/models` only — it costs nothing.
3. **Paste code or a finding**, or load one of the 12 real examples.
4. **Select a model.** No model is pre-selected. The run button stays disabled until you pick one.
5. **Press Audit.** Read the verdict, severity, confidence, reason, fix, latency, token usage, and cost.
6. **Export the report** as Markdown or JSON.

If Test Key reports a network error, open the page in a full browser such as Chrome or Safari, not an in-app viewer, and turn off any VPN or content blocker, then try again. The GMI API sits behind Cloudflare, which can reject webviews before the call arrives.

## Features

| Feature | What it does |
|---|---|
| Live triage | Audit one finding with one model you choose. Temperature 0, JSON-only prompt. |
| Compare 2–3 models | Run the same finding through two or three models side by side. A disagreement flag appears when the verdicts differ. No model is marked right — you decide. |
| Two-stage triage | A cheap first pass, with a second model only when the first is uncertain: confidence below 0.8, an unparsed answer, or a first-stage error. You pick both stages; neither is pre-selected. Max tokens 800, 1200, or 2500. If Stage 2 errors, the Stage 1 verdict is kept and the failure is flagged. |
| Repo audit | Paste files, fetch a public GitHub repo by URL, or upload a zip. Pick from 7 checks: SQL injection, XSS, authentication and session flaws, hardcoded secrets, weak cryptography, SSRF, and path traversal. One model call per file, per-file findings with file, line, verdict, and fix. |
| 12 real examples | 9 real findings and 3 false positives, each loading with one click and showing its expected verdict so you can check whether the model gets it right. See [Examples](#examples). |
| Cost estimate first | The tool shows a typical and a maximum cost before it runs, based on your actual input length (about 4 characters per token) plus the prompt. Nothing runs until you press Audit. |
| Report export | Markdown preview with model, prompt, verdict, fix, and date, plus Copy Markdown, Download `.md`, and Download JSON. Saved runs (up to 10) live in sessionStorage only. |
| No defaults | No model is pre-selected anywhere: not in Live Triage, not in compare, not in either two-stage stage, and not in repo audit. Picking a model in one place does not silently set it in another. |

## Examples

The 12 built-in examples are real, not generic filler. Every one names its CVE or CWE, or its dataset finding id.

| # | Example | Expected verdict |
|---|---|---|
| 1 | Log4Shell, CVE-2021-44228, Log4j 2.0-beta9 to 2.14.1, CVSS 10.0 | Real, critical |
| 2 | Flask-AppBuilder Azure JWT, CVE-2026-59243, `verify_signature` defaults to False, fixed in 3.7.3 | Real, critical |
| 3 | Spring4Shell, CVE-2022-22965, Spring 5.3.0–5.3.17, JDK 9+ with WAR on Tomcat | Real, critical, only under those conditions |
| 4 | MOVEit SQL injection, CVE-2023-34362, CVSS 9.8, exploited May 2023 | Real, critical |
| 5 | Apache path traversal, CVE-2021-41773, Apache HTTP Server 2.4.49 | Real, high; critical with CGI |
| 6 | Struts2 OGNL, CVE-2017-5638, CVSS 10.0, S2-045, March 2017 | Real, critical |
| 7 | PAN-OS command injection, CVE-2024-3400, GlobalProtect | Real, critical |
| 8 | XZ supply chain, CVE-2024-3094, XZ Utils 5.6.0 / 5.6.1 | Real, critical |
| 9 | Pickle deserialization, CWE-502, `pickle.loads(request.data)` | Real, critical |
| 10 | SSRF false positive, dataset finding F05, fixed URL, not user-controlled | False positive, low |
| 11 | XSS false positive, dataset finding F04, `textContent`, not `innerHTML` | False positive, low |
| 12 | SQL injection false positive, dataset finding F01, parameterised query | False positive, low |

The MOVEit and PAN-OS examples show representative patterns, labelled as such, not proprietary source code.

## Models

The tool lists all **81 unique GMI models** (82 entries in `models-82.json`, one duplicate: `inclusionAI/Ling-3.0-flash-fin`), with real per-token prices and context lengths, verified against a live `list-models` call on 2026-11-08. The docs example `meta-llama/Llama-3.3-70B-Instruct` is not in that list and is not offered.

No model is pre-selected, and the tool makes no "best model" claim. Which model works best depends on your code, your budget, and how much reasoning a finding needs — which is exactly why the compare mode exists.

### A warning about reasoning-heavy models

Reasoning models can spend their whole completion budget thinking and return no visible JSON at all. `max_tokens` does not cap reasoning tokens.

This happened in real testing, twice, and it is worth knowing before you spend money on it:

- `deepseek-ai/deepseek-v4.1-flash-1017` on `run_benchmark.py` (4,246 prompt tokens) spent all 2,500 completion tokens reasoning on both the first call and the retry, returned empty content both times, and cost $0.008521 in total for no verdict.
- The same behaviour was seen earlier with Qwen, which produced 2,381 and 2,794 completion tokens despite a `max_tokens` of 800.

The tool now guards against this: repo audit uses `max_tokens` 2500 by default, warns before running a large file (over 3,000 prompt tokens) with a reasoning-heavy model (DeepSeek, thinking, R1, reasoning), and **skips the automatic retry for reasoning-heavy models**, because the retry costs another call and failed the same way in testing. Other models still get one retry with a shorter prompt on an unparsed answer.

Models that parsed reliably in the 50-finding test — `google/gemini-3.5-flash-lite`, `Qwen/Qwen3.8-Flash`, and `XiaomiMiMo/MiMo-V2.6-Flash`, with 0 unparsed on Gemini and Qwen — are named in the warning as options to try. They are not pre-selected. You choose.

## How it works

Every audit is a single chat call to the GMI Inference API, from your browser, with your key:

```
POST https://api.gmi-serving.com/v1/chat/completions
```

Temperature 0, JSON-only prompt. The model is asked to return only:

```json
{"findings": [{"line": 0, "check": "sql-injection", "verdict": "real", "severity": "high", "confidence": 0.9, "reason": "…", "fix": "…"}]}
```

The tool extracts the first `{...}` block containing a `findings` array. If no JSON can be extracted, the result is **unparsed** — shown as "Unparsed, no verdict, this file is NOT clean", with the reasoning token count, latency, and cost. It is never counted as zero findings, and no verdict is invented. A 90-second timeout is reported the same way.

Errors are shown honestly: 401 means the key is invalid, 404 means the model was not found, 429 means rate limited. The tool never invents a verdict.

### The test set behind it

The audit prompt and the 12 examples were validated against a labelled dataset of **50 findings — 25 real, 25 false positives** — across 14 categories: SQL injection, XSS, SSRF, path traversal, command injection, hardcoded secrets, weak cryptography, insecure deserialization, JWT, auth bypass, IDOR, CSRF, open redirect, and sensitive data. See `dataset.json`. A balanced 56-finding version, `dataset-v2.json` (14 categories × 4, 28 real / 28 false positives), exists in the repo but has not been run against any model yet — do not treat the v1 results as v2 results.

The per-model results from that test set are kept in the repo as evidence only (`results-all.json`, `results.json`): 25 models were verified as scored, with scored runs totalling $1.156338 and a whole-project grand total of about $1.21, plus about $0.019–$0.023 of later live testing. **There is no leaderboard on the site, no ranking, and no best-model claim.** The dataset is deliberately clear-cut, so good scores on it mean a model handles textbook cases well — they do not prove it would score the same on subtle, real-world code.

Two-stage triage was smoke-tested on the 5 hardest findings on 2026-11-09 for $0.007758 (22 calls): Gemini 3.5 Flash Lite alone scored 4 of 5, two-stage (Gemini plus Sol) also scored 4 of 5 at the same cost, because Stage 2 never fired, and Sol alone scored 2 of 5 counting errors as wrong, with 3 HTTP errors. On that small test two-stage did not beat the cheap model alone, and this README does not claim it does. It saves money when Stage 1 is uncertain often enough for Stage 2 to earn its cost, and costs nothing extra when Stage 1 is sure.

## Cost

You pay GMI, not the author. Costs come from token usage returned by the API and the per-token prices in `models-82.json`. The tool shows an estimate before every run.

Real costs from live testing:

| Call | Model | Tokens | Cost |
|---|---|---|---|
| `run_benchmark.py`, repo audit, first call | google/gemini-3.5-flash-lite | 4,615 prompt, 5 completion | $0.001397 |
| `run_benchmark.py`, repo audit, first call + retry, both unparsed | deepseek-ai/deepseek-v4.1-flash-1017 | 4,246 prompt, 2,500 completion (all reasoning), twice | $0.008521 |
| `scripts/build.js` (925 chars), repo audit | google/gemini-3.5-flash-lite | 536 prompt, 5 completion | $0.000173 |
| A single finding, typical | Most models | — | About $0.0001–$0.001 |

A single finding usually costs a fraction of a cent. Large files cost more, because the whole file is sent as prompt tokens — `run_benchmark.py` is 13,635 characters, about 4,246 prompt tokens. The cost estimate shows this before you run.

## Privacy and security

- **Your GMI key** stays in your browser, in `sessionStorage` only. It is never stored in `localStorage`, never logged, and never sent anywhere except directly to `https://api.gmi-serving.com/v1`. Press Clear key, or close the tab, and it is gone. Test Key calls `GET /v1/models` only and costs nothing.
- **Your GitHub token** (optional, for repo audit) is also `sessionStorage` only, sent only to `api.github.com`, never logged, with a Clear button. It raises the GitHub API limit from about 60 requests per hour to 5,000 per hour, and enables private repos you can see. Even a classic token with no scopes works for public repos.
- **No server.** The site is a single static page. It makes no calls of its own and stores nothing on a server. Saved runs live in your browser only.
- **No analytics, no cookies, no key logging** on the page. The page loads Google Fonts, which sends your IP address to Google; that is the only third-party request besides the GMI and GitHub APIs you choose to call.
- A model verdict is one reading on the code shown. Verify it before acting on it.

## Limitations

Honest limits, so you are not surprised by them:

- **Reasoning models can return nothing.** A reasoning-heavy model can spend all its completion tokens thinking and return no JSON. That is reported as unparsed, not as clean. See [Models](#models).
- **Unparsed is not clean.** If a file comes back unparsed, the tool says so plainly. Do not treat it as zero findings.
- **Repo audit limits.** 10 files, 40 KB per file, 200 KB total per audit. Large repos must be audited in slices, by ticking the files that matter.
- **GitHub API rate limits.** Unauthenticated GitHub API calls are limited to about 60 requests per hour, shared across the network you are on — on a shared or mobile network you can hit that limit fast, and the page will say so plainly with the reset time. Add a GitHub token to raise it to 5,000 per hour.
- **Private repos need a token.** Public repos work without one (subject to the rate limit above). Private repos need a GitHub token for an account that can see them.
- **The test set is textbook.** The 50-finding dataset is deliberately clear-cut. Good scores on it do not prove a model will score the same on subtle, real-world code.
- **Mobile layout is not yet verified on a real phone.** The page uses single-column stacking with no page-wide sideways scroll, but it has not been checked on a physical device.
- **No server-side history.** Saved runs live in `sessionStorage` only and disappear when the tab closes.

## Repo structure

```
index.html            Single-page app: audit console, compare, two-stage, repo audit, report export
vercel.json           Static hosting config, security headers
README.md             This file
TUTORIAL.md           Step-by-step tutorial for the audit tool
dataset.json          50 labelled findings (25 real / 25 false positives), the test set
dataset-v2.json       Balanced 56-finding dataset, not yet run
models-82.json        All 82 GMI model entries (81 unique), with prices and context lengths
results.json          Full per-model, per-finding results from the original 4-model run
results-all.json      Per-model and per-finding results for the 25 verified scored models
cost-all-models.json  Safe and realistic cost estimates for all priced models
run_benchmark.py      Runner used to build the test-set evidence (not needed to use the site)
```

## Development

Run it locally — it is a static page, there is nothing to install:

```bash
git clone https://github.com/Jayanng/gmi-benchmark.git
cd gmi-benchmark
python3 -m http.server 8000
# open http://localhost:8000/
```

Or open `index.html` directly in a browser. All calls go from your browser to the GMI and GitHub APIs; no local server logic is involved.

To rebuild the test-set evidence (not needed to use the site):

```bash
python3 run_benchmark.py --limit 5   # smoke test, 5 findings
python3 run_benchmark.py             # full run, 50 findings
```

Cost is calculated from token usage returned by the API and the prices in `models-82.json`. Every row in `results.json` comes from a live API response, or is recorded as unparsed when no verdict could be extracted.

### Deploy

The site is deployed from this repo:

- **Vercel:** https://gmi-benchmark.vercel.app/ (production, static, `vercel.json` sets `X-Content-Type-Options: nosniff` and `Referrer-Policy: no-referrer`)
- **GitHub Pages:** https://jayanng.github.io/gmi-benchmark/

A push to `Master` updates both. Vercel does not always auto-deploy on push; if the live site lags behind the repo, create a deployment from the Git source manually.

## GMI Cloud

Built on the [GMI Cloud Inference Engine](https://www.gmicloud.ai/) — list models and chat completions at `https://api.gmi-serving.com/v1`. Inference only: no AgentBox, no GMI Studio, no Cluster Engine is used by this tool.

If you share it, tag [@gmi_cloud](https://x.com/gmi_cloud) and use `#GMICloud` and `#GMIStudio`.

## Screenshots

No screenshots are included in the repo yet. The fastest way to see the tool is the live demo: https://gmi-benchmark.vercel.app/ — paste code or load an example, select a model, and audit it.

## Contributing

Issues and pull requests are welcome. Please keep the guardrails that make the tool trustworthy:

- Never invent a verdict, a score, or a finding. Unparsed is unparsed, not clean.
- Never pre-select a model. The user chooses.
- Never log, store, or send a key anywhere except the API it belongs to, and only from the visitor's browser.
- Keep the site a static page with no server and no leaderboard.

## License

No license file is included in this repo yet. All rights are reserved by default until one is added.

## Changelog

- **2026-11-10 — No model is pre-selected.** Every model select starts at "Select a model". Run buttons stay disabled until a key is entered and a model is picked. Retry is skipped for reasoning-heavy models; timeouts are shown as no verdict, not a crash. Fixed a bug where the repo estimate warning could be lost.
- **2026-11-10 — Repo audit unparsed fix.** Repo audit `max_tokens` raised from 800 to 2500, one retry with a shorter prompt, a warning for large files and reasoning-heavy models, and unparsed files shown as "no verdict, NOT clean" instead of "no findings".
- **2026-11-09 — GitHub repo fetch fix.** File contents are now actually fetched via `raw.githubusercontent.com` with a Contents API fallback, robust URL parsing (owner/repo, `.git`, `/tree/` and `/blob/` links), an optional GitHub token field, and real GitHub error messages with a rate-limit reset time.
- **2026-11-09 — Rebuilt as a live audit tool, no leaderboard.** The leaderboard, ranking, recommender, and charts were removed. The site is now a live audit tool: paste code or a GitHub repo, compare 2–3 models, two-stage triage, repo audit, report export.
- **2026-11-09 — Product audit.** Content accuracy, SEO, favicon, footer, accessibility, leaderboard sort, and privacy fixes. Found the `run_left.py` TN/FN scoring bug in the left-models run; that run was stopped and its scores were not merged.
- **2026-11-08 — Real GMI theme, Live Triage, your own key.** Rebuilt the frontend in GMI's black `#000000` and lime `#DDEA4D` theme, with Live Triage, a model selector, and a cost estimator.
- **2026-11-08 — First benchmark.** 4 models on 50 findings: Qwen 3.8 Flash and Gemini 3.5 Flash Lite scored 1.000 accuracy, GLM 5.3 Flash 0.980, DeepSeek V4.1 Flash 0.980 with one unparsed finding. Total spend at that point $0.055350.
