#!/usr/bin/env python3
"""Security Model Benchmark runner. Calls GMI Inference via the registered
custom.gmi-cloud credential, never with a pasted key.
Usage:
  python3 run_benchmark.py [--limit N] [--models model1,model2]
  python3 run_benchmark.py --models openai/gpt-6.1-sol --limit 5
  python3 run_benchmark.py --all-cheap --estimate-only
  python3 run_benchmark.py --models openai/gpt-6-sol --merge
Not locked to the original 4 models: any model ID in the live
list-models response (82 models, verified 2026-11-08) can be selected.
meta-llama/Llama-3.3-70B-Instruct is NOT in that list and is rejected.
Hard cap: no run whose safe upper-bound cost estimate exceeds $5.00 is started.
Safe upper-bound estimate uses 250 prompt tokens and 2500 completion tokens
per finding (2500 is max_tokens, so completion cannot exceed it). Observed
means across the original 200 calls were 156 prompt and 246 completion, but
reasoning models can use the full 2500 completion budget, e.g. DeepSeek F07
used 2500 completion tokens, cost $0.00305 vs $0.000408 on the old 160+300
estimate. The old estimate was NOT an upper bound and must not be used.
Per-model prompt-token overrides use observed maxima: openai/gpt-6.1-sol
uses about 4550 prompt tokens per call, almost all provider-side cached
tokens, not tokens sent by this runner, see results.json notes.
"""
import argparse, json, re, socket, sys, time, urllib.request, urllib.error
from pathlib import Path
sys.path.insert(0, "/opt/muse/skills/custom-connector-setup/bin")
from dynamic_credentials import add_surrogate_to_request, read_response_body

BASE = Path(__file__).resolve().parent
MODELS = json.load(open(Path.home() / "workspace/gmi-clouder/models-2026-11-08.json"))
PRICE = {}
for m in MODELS["data"]:
    p = m.get("pricing") or {}
    # Some models use a different schema (e.g. gmicloud/Ripple-65B-Preview);
    # only flat prompt/completion pricing is usable for estimates.
    # inclusionAI/Ling-3.0-flash-fin appears twice in the list, once free
    # ($0) and once paid; keep the paid entry so estimates are not $0.
    if isinstance(p, dict) and "prompt" in p and "completion" in p:
        existing = PRICE.get(m["id"])
        if existing is None or (float(existing.get("prompt", 0) or 0) + float(existing.get("completion", 0) or 0) == 0):
            PRICE[m["id"]] = p
DEFAULT_MODELS = [
    "zai-org/GLM-5.3-Flash",
    "deepseek-ai/DeepSeek-V4.1-Flash",
    "Qwen/Qwen3.8-Flash",
    "google/gemini-3.5-flash-lite",
]
MAX_TOKENS = 2500
HARD_CAP_USD = 5.00
EST_PROMPT_TOKENS = 250
EST_COMPLETION_TOKENS = 2500
# Observed prompt-token maxima, from live usage. Sol is an outlier: the
# runner sends the same ~150-token prompt to every model, yet Sol rows
# report ~4510 prompt tokens, ~3801 of them cached_tokens, in every row.
# That extra is provider-side, not sent by this runner.
OBSERVED_PROMPT_TOKENS = {"openai/gpt-6.1-sol": 4550}

class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, *args):
        raise RuntimeError("redirect refused")

def _req(url, data=None, method="GET", timeout=120):
    req = urllib.request.Request(url, data=data, method=method)
    req.add_header("Accept", "application/json")
    req.add_header("User-Agent", "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/120.0 Safari/537.36")
    if data is not None:
        req.add_header("Content-Type", "application/json")
    add_surrogate_to_request(req, "custom.gmi-cloud", allowed_hosts=["api.gmi-serving.com", "api.gmicloud.ai", "mcp.gmicloud.ai", "console.gmicloud.ai"])
    with urllib.request.build_opener(NoRedirect()).open(req, timeout=timeout) as resp:
        return json.loads(read_response_body(resp).decode())

def list_models_live():
    """Return the live list-models response. Never guess model IDs."""
    return _req("https://api.gmi-serving.com/v1/models")

def estimate_cost_usd(model, n_findings):
    """Safe upper-bound estimate for n findings, or None if pricing is unknown.
    Uses 250 prompt tokens (4550 for gpt-6.1-sol, observed) and 2500
    completion tokens, which is max_tokens, so a real run cannot exceed
    this estimate on token counts. Prices can still change; re-check live.
    """
    pr = PRICE.get(model)
    if not pr:
        return None
    pp = float(pr.get("prompt", 0) or 0)
    cp = float(pr.get("completion", 0) or 0)
    pt = OBSERVED_PROMPT_TOKENS.get(model, EST_PROMPT_TOKENS)
    return n_findings * (pt * pp + EST_COMPLETION_TOKENS * cp)

def cheapest_models(n=5):
    priced = [(mid, p) for mid, p in PRICE.items()
              if float(p.get("prompt", 0) or 0) + float(p.get("completion", 0) or 0) > 0]
    ranked = sorted(priced, key=lambda kv: float(kv[1].get("prompt", 0) or 0) + float(kv[1].get("completion", 0) or 0))
    return [mid for mid, _ in ranked[:n]]

def _is_timeout(exc):
    """True for socket/URL timeouts. urllib wraps socket.timeout in URLError."""
    if isinstance(exc, (TimeoutError, socket.timeout)):
        return True
    if isinstance(exc, urllib.error.URLError):
        reason = getattr(exc, "reason", None)
        return isinstance(reason, (TimeoutError, socket.timeout)) or "timed out" in str(reason).lower()
    return False

def chat(model, prompt, max_tokens=MAX_TOKENS):
    """One chat call, with a single retry on timeout.

    Fix for the 2026-11-08 runner bug: the old code caught only HTTPError,
    so a socket TimeoutError (120s read timeout) on a single finding
    crashed the whole run. deepseek-v4.1-flash-1017 crashed it 4 times,
    losing 70 billed calls, about $0.026. Now a timeout retries once
    with a 300s timeout, and if that also times out the finding is
    recorded as unparsed (verdict None, usage carries timeout=True and
    retried=True) instead of crashing the run. Billed cost of the timed-out
    calls cannot be recovered from the response, so it is not counted here.
    """
    body = {"model": model, "messages": [{"role": "user", "content": prompt}],
            "max_tokens": max_tokens, "temperature": 0}
    data = json.dumps(body).encode()
    t0 = time.time()
    for attempt, timeout in ((1, 120), (2, 300)):
        try:
            out = _req("https://api.gmi-serving.com/v1/chat/completions", data=data, method="POST", timeout=timeout)
            break
        except urllib.error.HTTPError as e:
            return None, time.time() - t0, {"error": f"HTTP {e.code}: {e.read().decode(errors='replace')[:300]}"}
        except Exception as e:
            if not _is_timeout(e):
                raise
            if attempt == 1:
                print(f"timeout on {model} after {timeout}s, retrying once with 300s", flush=True)
                continue
            return None, time.time() - t0, {"error": f"timeout after retry (120s + 300s): {e}", "timeout": True, "retried": True}
    dt = time.time() - t0
    ch = out.get("choices", [{}])[0]
    msg = ch.get("message", {})
    content = msg.get("content") or ""
    usage = out.get("usage", {})
    if isinstance(usage, dict):
        usage = dict(usage)
        usage["retried"] = (attempt == 2)
    return content, dt, usage

def _extract_balanced_json(text):
    """Return the first balanced {...} object in text, or None."""
    start = text.find("{")
    if start == -1:
        return None
    depth = 0
    in_str = False
    esc = False
    for i in range(start, len(text)):
        ch = text[i]
        if in_str:
            if esc:
                esc = False
            elif ch == "\\":
                esc = True
            elif ch == '"':
                in_str = False
        else:
            if ch == '"':
                in_str = True
            elif ch == "{":
                depth += 1
            elif ch == "}":
                depth -= 1
                if depth == 0:
                    return text[start:i + 1]
    return None

def parse_verdict(text):
    if not text:
        return None
    raw = _extract_balanced_json(text)
    if not raw:
        return None
    try:
        d = json.loads(raw)
    except Exception:
        return None
    if not isinstance(d, dict):
        return None
    v = str(d.get("verdict", "")).strip()
    if v == "real":
        return "real"
    if v == "false_positive":
        return "false_positive"
    return None

PROMPT = """You are a security code reviewer. Classify this code finding.
Return ONLY JSON, no other text: {"verdict": "real" or "false_positive", "severity": "critical|high|medium|low", "reason": "one short sentence"}
A finding is real only if untrusted input actually reaches a dangerous sink with no effective mitigation in the code shown.
If the code uses parameterisation, escaping, allowlisting, ownership checks, safe loaders, or verified signatures, it is a false_positive.
Code:
{code}
Category: {cat}
"""

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--models", default=",".join(DEFAULT_MODELS))
    ap.add_argument("--all-cheap", action="store_true", help="Use the 5 cheapest models by per-token price")
    ap.add_argument("--estimate-only", action="store_true", help="Print the cost estimate and exit without calling the API for chat")
    ap.add_argument("--max-tokens", type=int, default=MAX_TOKENS)
    ap.add_argument("--out", default="results.json")
    ap.add_argument("--merge", action="store_true", help="Merge new per-model results into the existing output file instead of replacing it")
    ap.add_argument("--allow-unpriced", action="store_true", help="Allow models with no flat per-token pricing (e.g. gmicloud/Ripple-65B-Preview). Without this flag such models are refused, because their cost cannot be estimated against the $5 hard cap.")
    args = ap.parse_args()

    # 1. Validate every requested model ID live, do not guess IDs.
    live = list_models_live()
    live_ids = {m["id"] for m in live.get("data", [])}
    if args.all_cheap:
        models = cheapest_models(5)
    else:
        models = [m.strip() for m in args.models.split(",") if m.strip()]
    unknown = [m for m in models if m not in live_ids]
    if unknown:
        print(f"ERROR: model(s) not in live list-models ({len(live_ids)} models): {unknown}", file=sys.stderr)
        print("meta-llama/Llama-3.3-70B-Instruct is not in the list and is rejected the same way.", file=sys.stderr)
        raise SystemExit(2)

    ds = json.load(open(BASE / "dataset.json"))
    findings = ds["findings"][: args.limit] if args.limit else ds["findings"]

    # 2. Cost estimate before running, hard $5 cap.
    estimates = {}
    for model in models:
        est = estimate_cost_usd(model, len(findings))
        estimates[model] = est
        print(f"estimate {model}: {len(findings)} findings -> ${est:.6f}" if est is not None else f"estimate {model}: pricing unknown, cannot estimate", flush=True)
    total_est = sum(e for e in estimates.values() if e is not None)
    unknown_pricing = [m for m, e in estimates.items() if e is None]
    print(f"estimated total: ${total_est:.6f} (hard cap ${HARD_CAP_USD:.2f})", flush=True)
    if total_est > HARD_CAP_USD:
        print(f"ERROR: estimated total ${total_est:.6f} exceeds the hard ${HARD_CAP_USD:.2f} cap. Refusing to run. Use --limit to run fewer findings or pick cheaper models.", file=sys.stderr)
        raise SystemExit(3)
    if args.estimate_only:
        if unknown_pricing:
            print(f"WARNING: no flat pricing for {unknown_pricing}; cost cannot be estimated for those models.", file=sys.stderr)
        return
    if unknown_pricing and not args.allow_unpriced:
        print(f"ERROR: no flat pricing for {unknown_pricing}; cost cannot be estimated against the ${HARD_CAP_USD:.2f} hard cap. Refusing to run. Re-run with --allow-unpriced to run them anyway, or run a 5-finding probe first.", file=sys.stderr)
        raise SystemExit(3)

    if args.merge and (BASE / args.out).exists():
        results = json.load(open(BASE / args.out))
        results.setdefault("per_model", {})
        results.setdefault("per_finding", [])
        # Drop old rows for models being re-run, so a re-run replaces them.
        results["per_finding"] = [r for r in results["per_finding"] if r.get("model") not in models]
    else:
        results = {"date": "2026-11-08", "models": models, "findings_count": len(findings), "per_model": {}, "per_finding": []}
    results["models"] = sorted(set(results.get("models", []) + models))

    for model in models:
        tp = fp = tn = fn = 0
        lat = []
        cost = 0.0
        per = []
        pr = PRICE.get(model, {})
        pp = float(pr.get("prompt", 0) or 0)
        cp = float(pr.get("completion", 0) or 0)
        for f in findings:
            content, dt, usage = chat(model, PROMPT.replace("{code}", f["code"]).replace("{cat}", f["category"]), max_tokens=args.max_tokens)
            lat.append(dt)
            if isinstance(usage, dict) and usage.get("prompt_tokens") is not None:
                cost += usage.get("prompt_tokens", 0) * pp + usage.get("completion_tokens", 0) * cp
            verdict = parse_verdict(content) if content else None
            exp = f["expected_label"]
            if verdict == "real" and exp == "real": tp += 1
            elif verdict == "real" and exp == "false_positive": fp += 1
            elif verdict == "false_positive" and exp == "false_positive": tn += 1
            elif verdict == "false_positive" and exp == "real": fn += 1
            per.append({"id": f["id"], "expected": exp, "verdict": verdict, "latency_s": round(dt, 2),
                        "raw": (content or "")[:400], "usage": usage if isinstance(usage, dict) else {}})
            print(f"{model} {f['id']} expected={exp} verdict={verdict} {dt:.1f}s", flush=True)
        unparsed = sum(1 for p in per if p["verdict"] is None)
        parsed = len(findings) - unparsed
        prec = tp / (tp + fp) if tp + fp else 0
        rec = tp / (tp + fn) if tp + fn else 0
        f1 = 2 * prec * rec / (prec + rec) if prec + rec else 0
        acc = (tp + tn) / len(findings) if findings else 0
        results["per_model"][model] = {
            "tp": tp, "fp": fp, "tn": tn, "fn": fn,
            "precision": round(prec, 3), "recall": round(rec, 3), "f1": round(f1, 3), "accuracy": round(acc, 3),
            "avg_latency_s": round(sum(lat) / len(lat), 2) if lat else 0,
            "total_cost_usd": round(cost, 6), "cost_per_finding_usd": round(cost / len(findings), 6) if findings else 0,
            "prompt_price_per_token": pp, "completion_price_per_token": cp,
            "unparsed": unparsed, "parsed": parsed, "total_findings": len(findings),
        }
        results["per_finding"].extend([{**p, "model": model} for p in per])
        print(f"== {model}: P={prec:.3f} R={rec:.3f} F1={f1:.3f} Acc={acc:.3f} latency={sum(lat)/len(lat):.2f}s cost=${cost:.6f}", flush=True)
    (BASE / args.out).write_text(json.dumps(results, indent=2))
    print(json.dumps(results["per_model"], indent=2))

if __name__ == "__main__":
    main()
