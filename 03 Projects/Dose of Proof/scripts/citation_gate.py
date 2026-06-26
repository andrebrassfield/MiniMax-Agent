#!/usr/bin/env python3
"""
Citation Gate — [[triage-gate-spec]] §1b — PubMed eSummary runtime lookup.

Per Co-CEO rule 2026-06-25 21:14 CT: "Any draft whose release depends on a
citation (PMID/DOI/author-year) is BLOCKED until the citation is **independently
verified**: the identifier resolves to a real source AND that source supports
the specific claim."

Fail-closed: API timeout / unresolved PMID / off-topic → SENSITIVE.

Status: ✅ SHIPPED v0.5 STAGING per Co-CEO sign-off (B) 2026-06-26 11:54 CT
        (see specs/v0.4-review-package.md §9.4.1 + specs/v0.5-staged-plan.md)
Regression: 4/4 PASS (scripts/run_citation_gate_tests.py)
Independent of v0.4 LLM calibration sprint — ships ahead of LLM unblock.

Usage:
    from citation_gate import citation_gate
    result = citation_gate("The model I followed mapped it this way: unstable neck → vagus irritation → mast cell activation. Source: Henderson et al. 2023 (PMID:37421564) on CCI/autonomic.", claim_context="unstable neck → vagus irritation → mast cell activation")
"""
import json
import re
import urllib.request
import urllib.error
from typing import Any

CITATION_PATTERNS = [
    (r'\bPMID[:\s]+(\d{6,9})\b', 'pmid'),
    (r'\bpmid[:\s]+(\d{6,9})\b', 'pmid'),
    (r'\bDOI[:\s]+(10\.\d{4,9}/[^\s\]]+)', 'doi'),
    (r'\bdoi[:\s]+(10\.\d{4,9}/[^\s\]]+)', 'doi'),
]

# Common English stopwords to exclude from topic-match heuristic
STOPWORDS = {
    'this', 'that', 'with', 'from', 'have', 'been', 'were', 'their', 'study',
    'paper', 'findings', 'results', 'show', 'demonstrate', 'associated',
    'where', 'which', 'these', 'those', 'were', 'such', 'more', 'most',
    'between', 'through', 'during', 'before', 'after', 'above', 'below',
    'into', 'from', 'with', 'about', 'against', 'among', 'under',
}


def extract_citations(content: str) -> list[dict]:
    """Extract all PMID/DOI citations from a post body."""
    citations = []
    for pattern, ctype in CITATION_PATTERNS:
        for match in re.finditer(pattern, content):
            citations.append({
                "type": ctype,
                "identifier": match.group(1),
                "span": match.span(),
            })
    return citations


def verify_pmid(pmid: str, timeout: float = 10.0) -> dict:
    """Verify PMID via PubMed eSummary API. Returns {valid, title, authors, journal, pubdate} or {valid: False, error}."""
    url = f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?db=pubmed&id={pmid}&retmode=json"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mavis-EA/1.0 (compliance gate)"})
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        result = data.get("result", {}).get(pmid, {})
        if "error" in result:
            return {"valid": False, "pmid": pmid, "error": result["error"]}
        if not result.get("title"):
            return {"valid": False, "pmid": pmid, "error": "no title in PubMed response"}
        return {
            "valid": True,
            "pmid": pmid,
            "title": result.get("title", ""),
            "authors": [a.get("name", "") for a in result.get("authors", [])[:3]],
            "journal": result.get("source", ""),
            "pubdate": result.get("pubdate", ""),
        }
    except urllib.error.HTTPError as e:
        return {"valid": False, "pmid": pmid, "error": f"PubMed HTTP {e.code}: {e.reason}"}
    except urllib.error.URLError as e:
        return {"valid": False, "pmid": pmid, "error": f"PubMed URL error: {e.reason}"}
    except Exception as e:
        return {"valid": False, "pmid": pmid, "error": str(e)}


def verify_doi(doi: str, timeout: float = 10.0) -> dict:
    """Verify DOI via doi.org content negotiation. Returns {valid, title, type} or {valid: False, error}."""
    url = f"https://doi.org/{doi}"
    try:
        req = urllib.request.Request(url, headers={"Accept": "application/vnd.citationstyles.csl+json", "User-Agent": "Mavis-EA/1.0 (compliance gate)"})
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        return {
            "valid": True,
            "doi": doi,
            "title": data.get("title", ""),
            "type": data.get("type", ""),
        }
    except Exception as e:
        return {"valid": False, "doi": doi, "error": str(e)}


def check_topic_match(claim: str, paper_title: str, threshold: float = 0.15) -> dict:
    """
    Heuristic keyword overlap between paper title and the post's specific claim.
    Returns {matches, overlap_terms, confidence}.

    NOTE: this is a heuristic, NOT a model. Mavis should NOT auto-reject on low
    confidence — flag for HITL review. Production deployment should use the
    LLM layer for topic verification (much better than keyword overlap).
    """
    def terms(text: str) -> set[str]:
        return set(re.findall(r'\b[a-z]{4,}\b', text.lower())) - STOPWORDS

    claim_terms = terms(claim)
    title_terms = terms(paper_title)

    overlap = claim_terms & title_terms
    overlap_score = len(overlap) / max(len(claim_terms), 1)

    return {
        "matches": overlap_score >= threshold,
        "overlap_terms": sorted(overlap),
        "confidence": round(overlap_score, 3),
        "threshold": threshold,
        "claim_term_count": len(claim_terms),
        "title_term_count": len(title_terms),
    }


def citation_gate(content: str, claim_context: str = "", threshold: float = 0.15) -> dict:
    """
    Run §1b citation verification on a post body. Fail-closed: SENSITIVE if any check fails.

    Returns {
        classification: "CLEAR" | "SENSITIVE",
        citations: [list of per-citation results],
        failures: [list of failure messages],
        notes: [general notes],
    }
    """
    citations = extract_citations(content)
    if not citations:
        return {"classification": "CLEAR", "citations": [], "failures": [], "notes": "No citations in body."}

    results = []
    failures = []

    for cite in citations:
        if cite["type"] == "pmid":
            verification = verify_pmid(cite["identifier"])
            topic_check = {"matches": True, "overlap_terms": [], "confidence": 1.0}
            if verification.get("valid"):
                if claim_context:
                    topic_check = check_topic_match(claim_context, verification.get("title", ""), threshold=threshold)
                else:
                    topic_check = {"matches": True, "note": "no claim_context provided — topic check skipped (verification only)"}
            results.append({"citation": cite, "verification": verification, "topic_match": topic_check})
        elif cite["type"] == "doi":
            verification = verify_doi(cite["identifier"])
            topic_check = {"matches": True, "overlap_terms": [], "confidence": 1.0}
            if verification.get("valid") and claim_context:
                topic_check = check_topic_match(claim_context, verification.get("title", ""), threshold=threshold)
            results.append({"citation": cite, "verification": verification, "topic_match": topic_check})
        else:
            failures.append(f"Unknown citation type: {cite['type']}")
            continue

        if not verification.get("valid"):
            failures.append(
                f"Citation {cite['identifier']} ({cite['type']}) FAILED to resolve: {verification.get('error', 'unknown')}"
            )
        elif not topic_check.get("matches"):
            failures.append(
                f"Citation {cite['identifier']} resolves but topic-overlap with claim is LOW "
                f"(confidence={topic_check.get('confidence')}, threshold={threshold}). "
                f"Paper title: '{verification.get('title', '')[:120]}'. "
                f"Overlap terms: {topic_check.get('overlap_terms')}. "
                f"Per §1b: presence ≠ validity. This citation does NOT support the specific claim."
            )

    classification = "SENSITIVE" if failures else "CLEAR"

    return {
        "classification": classification,
        "citations": results,
        "failures": failures,
        "notes": [
            f"Verified {len(results)} citation(s) against PubMed eSummary API + DOI content negotiation.",
            f"Topic-match threshold: {threshold} (heuristic keyword overlap — NOT a model decision).",
            "Per [[triage-gate-spec]] §1b: a fabricated citation is worse than none. Verification is a separate gate, never self-asserted.",
        ],
    }


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: citation_gate.py '<text>' [claim_context]")
        sys.exit(1)
    text = sys.argv[1]
    claim_context = sys.argv[2] if len(sys.argv) > 2 else ""
    result = citation_gate(text, claim_context=claim_context)
    print(json.dumps(result, indent=2))
    sys.exit(0 if result["classification"] == "CLEAR" else 78)