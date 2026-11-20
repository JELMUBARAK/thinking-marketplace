"""Check a researcher's draft facts with one search-backed API call.

Replaces the researcher's own page fetching (slow: about 2.5 minutes for 8
pages). The researcher drafts facts, rules and what-ifs from knowledge only;
this script sends every fact that a rule or what-if cites to a search API in
ONE request and writes back verified / url / correction into
<slug>.research.json.

Provider, picked by which key is set:
  PERPLEXITY_API_KEY -> Perplexity Agent API, POST /v1/agent with web_search and
                        fetch_url tools and a JSON-schema response_format
                        (effort: PERPLEXITY_EFFORT, default "low"; or set
                        PERPLEXITY_MODEL, e.g. "openai/gpt-5.6-sol", to pin a model)
  GEMINI_API_KEY     -> Gemini with Google Search grounding (model: GEMINI_MODEL,
                        default "gemini-2.5-flash")
No key -> exit code 2; the skill then falls back to the researcher's web mode.

Plain HTTP with the standard library, not the perplexityai SDK: the plugin runs
scripts with `python -I`, which ignores user-installed packages.

Only the concept name and the fact claims are sent; nothing about the user.
Sources on blocked domains (Wikipedia, forums, video, blogs) never verify.
The question file is read only to count what-ifs that rest on unverified
facts; questions are never printed.

Usage: python verify.py <analogy-runs dir> <slug> [--all]
(by default only facts not yet verified are sent; --all re-checks every cited fact)
"""
import json
import os
import re
import ssl
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

BLOCKED = ("wikipedia.org", "reddit.com", "quora.com", "medium.com", "youtube.com",
           "blogspot.", "wordpress.", "facebook.com", "tiktok.com", "x.com", "twitter.com",
           "stackexchange.com", "chegg.com", "brainly.", "coursehero.com")

PROMPT = """You are checking facts for a science and civics learning app.
Concept: {concept}

For EACH claim below, search for a reliable source: a textbook (including
OpenStax, LibreTexts), a review article, a peer-reviewed study, a university
course page, or an official body (.gov, standards bodies). Wikipedia, forums,
blogs, videos and AI answers do NOT count.

Return ONLY a JSON array, one object per claim, no other text:
[{{"id": "F1", "verdict": "supported" | "contradicted" | "unclear",
   "url": "the exact page that states it, or empty",
   "correction": "if contradicted or only partly right, the corrected claim in one sentence, else empty"}}]

Claims:
{claims}
"""


def tls_context():
    """Verified TLS. On Windows, trust only the ROOT store: Python also loads the
    intermediate (CA) store, and a stale expired cross-certificate there made
    api.perplexity.ai fail with "certificate has expired" (20 Nov 2026)."""
    if sys.platform != "win32":
        return ssl.create_default_context()
    ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)  # verifies certs and hostnames
    ctx.load_verify_locations(cadata="".join(
        ssl.DER_cert_to_PEM_cert(der) for der, enc, _ in ssl.enum_certificates("ROOT") if enc == "x509_asn"))
    return ctx


def post(url, payload, headers):
    """POST JSON; on HTTP 429 wait for Retry-After (max 60 s) and try once more."""
    data = json.dumps(payload).encode()
    for attempt in (1, 2):
        req = urllib.request.Request(url, data=data, method="POST",
                                     headers={"Content-Type": "application/json", **headers})
        try:
            with urllib.request.urlopen(req, timeout=180, context=tls_context()) as r:
                return json.load(r)
        except urllib.error.HTTPError as e:
            if e.code == 429 and attempt == 1:
                time.sleep(min(int(e.headers.get("Retry-After") or 10), 60))
                continue
            hint = {401: "authentication failed: check PERPLEXITY_API_KEY (rotate it in the console if exposed)",
                    429: "rate limited twice; try again later"}.get(e.code, "")
            raise RuntimeError(f"HTTP {e.code} {hint}".strip()) from None


SCHEMA = {
    "type": "object",
    "properties": {"checks": {"type": "array", "items": {
        "type": "object",
        "properties": {"id": {"type": "string"},
                       "verdict": {"type": "string", "enum": ["supported", "contradicted", "unclear"]},
                       "url": {"type": "string"},
                       "correction": {"type": "string"}},
        "required": ["id", "verdict", "url", "correction"]}}},
    "required": ["checks"],
}


def ask_perplexity(prompt):
    """Perplexity Agent API (docs: api-reference/agent-post, agent-api/output-control)."""
    body = {"input": prompt,
            "instructions": "You verify facts against reliable published sources. Answer only in the requested JSON.",
            "tools": [{"type": "web_search"}, {"type": "fetch_url"}],
            "temperature": 0,
            "response_format": {"type": "json_schema",
                                "json_schema": {"name": "fact_checks", "schema": SCHEMA, "strict": True}}}
    if os.environ.get("PERPLEXITY_MODEL"):
        body["model"] = os.environ["PERPLEXITY_MODEL"]
    else:
        body["effort"] = os.environ.get("PERPLEXITY_EFFORT", "low")
    out = post("https://api.perplexity.ai/v1/agent", body,
               {"Authorization": "Bearer " + os.environ["PERPLEXITY_API_KEY"]})
    if out.get("status") != "completed":
        raise RuntimeError(f"agent status {out.get('status')}: {(out.get('error') or {}).get('message', '')}")
    # Raw JSON has no output_text (that is an SDK helper): join the message parts.
    text, cites = "", []
    for item in out.get("output", []):
        if item.get("type") == "message":
            for part in item.get("content", []):
                if part.get("type") == "output_text":
                    text += part.get("text", "")
                    cites += [a.get("url") for a in part.get("annotations") or []]
        elif item.get("type") == "search_results":
            cites += [x.get("url") for x in item.get("results", [])]
    cost = ((out.get("usage") or {}).get("cost") or {}).get("total_cost")
    return text, f"perplexity-agent:{out.get('model') or body.get('effort')}", cites, cost


def ask_gemini(prompt):
    model = os.environ.get("GEMINI_MODEL", "gemini-2.5-flash")
    out = post(f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent",
               {"contents": [{"parts": [{"text": prompt}]}],
                "tools": [{"google_search": {}}],
                "generationConfig": {"temperature": 0}},
               {"x-goog-api-key": os.environ["GEMINI_API_KEY"]})
    cand = out["candidates"][0]
    text = "".join(p.get("text", "") for p in cand["content"]["parts"])
    chunks = (cand.get("groundingMetadata") or {}).get("groundingChunks", [])
    cites = [c.get("web", {}).get("uri") for c in chunks]
    return text, f"gemini:{model}", cites, None


def parse(text):
    """Accept {"checks": [...]} (Agent API schema) or a bare JSON array (Gemini)."""
    try:
        data = json.loads(text)
        return data["checks"] if isinstance(data, dict) else data
    except Exception:
        m = re.search(r"\[.*\]", text, flags=re.S)
        if not m:
            raise ValueError("no JSON array in the reply")
        return json.loads(m.group(0))


def blocked(url):
    host = urllib.parse.urlparse(url or "").netloc.lower()
    return not host or any(b in host for b in BLOCKED)


def main():
    d, slug = sys.argv[1], sys.argv[2]
    if os.environ.get("PERPLEXITY_API_KEY"):
        ask = ask_perplexity
    elif os.environ.get("GEMINI_API_KEY"):
        ask = ask_gemini
    else:
        print(json.dumps({"ok": False, "fallback": True,
                          "problem": "no PERPLEXITY_API_KEY or GEMINI_API_KEY set; use the researcher's web mode"}))
        sys.exit(2)

    rpath = os.path.join(d, f"{slug}.research.json")
    r = json.load(open(rpath, encoding="utf-8"))
    try:
        qs = json.load(open(os.path.join(d, f"{slug}.questions.json"), encoding="utf-8"))
        qs = qs.get("whatifs", qs) if isinstance(qs, dict) else qs
    except Exception:
        qs = []
    facts = {f["id"]: f for f in r.get("facts", [])}
    cited = {fid for x in r.get("rules", []) for fid in x.get("fact_ids", [])}
    cited |= {fid for q in qs for fid in q.get("fact_ids", [])}
    todo = [facts[k] for k in sorted(cited, key=lambda s: int(re.sub(r"\D", "", s) or 0)) if k in facts]
    if "--all" not in sys.argv:  # re-check only what is not yet verified (no flip-flopping, cheaper)
        todo = [f for f in todo if f.get("verified") is not True]
    if not todo:
        print(json.dumps({"ok": True, "checked": 0, "note": "all cited facts already verified"}))
        return

    concept = r.get("concept") or slug
    claims = "\n".join(f'{f["id"]}: {f["claim"]}' for f in todo)
    try:
        text, provider, cites, cost = ask(PROMPT.format(concept=concept, claims=claims))
        verdicts = {v.get("id"): v for v in parse(text)}
    except Exception as e:
        print(json.dumps({"ok": False, "fallback": True, "problem": f"API call failed: {e!r}"}))
        sys.exit(1)

    contradicted, unverified = [], []
    for f in todo:
        v = verdicts.get(f["id"], {})
        url = v.get("url") or ""
        ok = v.get("verdict") == "supported" and not blocked(url)
        f.update({"verified": ok, "url": url, "verified_by": provider})
        f.setdefault("tier", 2 if ok else None)
        if v.get("correction"):
            f["correction"] = v["correction"]
        if v.get("verdict") == "contradicted":
            contradicted.append({"id": f["id"], "correction": v.get("correction", "")})
        elif not ok:
            unverified.append(f["id"])

    bad = {f["id"] for f in facts.values() if f["id"] in cited and not f.get("verified")}
    weak_rules = [x["id"] for x in r.get("rules", []) if bad & set(x.get("fact_ids", []))]
    weak_qs = sum(1 for q in qs if bad & set(q.get("fact_ids", [])))
    r["fetches"] = f"1 call ({provider})"
    r.setdefault("gaps", []).extend(f"{fid} not verified by {provider}" for fid in unverified)
    json.dump(r, open(rpath, "w", encoding="utf-8"), ensure_ascii=False)
    print(json.dumps({"ok": not contradicted and not weak_rules, "provider": provider,
                      "checked": len(todo), "verified": len(todo) - len(bad),
                      "contradicted": contradicted, "unverified": unverified,
                      "rules_on_unverified_facts": weak_rules,
                      "whatifs_on_unverified_facts": weak_qs,
                      "sources_returned": len([c for c in cites if c]),
                      "cost_usd": cost}))


if __name__ == "__main__":
    main()
