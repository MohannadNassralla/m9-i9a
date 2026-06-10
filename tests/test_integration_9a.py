"""Autograder for Integration 9A — SPARQL Query Suite.

Tests run each of q1..q8 against the live Fuseki publications dataset.
Repo root after Classroom acceptance contains queries.py at the top level
and data/publications.ttl. The lab's queries are also checked via rdflib
as a local fallback so the structural checks still run when Fuseki is
unavailable.
"""

import json
import os
import sys
import time

import pytest
import requests
from rdflib import Graph

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from queries import q1, q2, q3, q4, q5, q6, q7, q8  # noqa: E402

TTL_FILE = os.path.join(os.path.dirname(__file__), "..", "data", "publications.ttl")
FUSEKI_SPARQL = "http://localhost:3030/publications/sparql"
FUSEKI_PING = "http://localhost:3030/$/ping"


# Expected gold counts — computed against the canonical data/publications.ttl
# shipped with the starter. If the dataset is regenerated, these change.
GOLD = {
    "q1_neurips_authors": 17,
    "q2_topic_groups": 24,
    "q3_canonical_coauthor_pairs": 215,
    "q4_paper_rows": 80,
    "q4_unbound_doi_min": 1,
    "q5_ask": True,
    "q6_construct_triples_2023": 31,
    "q7_top_cc": 485,
    "q8_hinton_matches": 2,
}


@pytest.fixture(scope="module")
def g():
    graph = Graph()
    graph.parse(TTL_FILE, format="turtle")
    return graph


@pytest.fixture(scope="module")
def fuseki_ready():
    deadline = time.time() + 30
    while time.time() < deadline:
        try:
            if requests.get(FUSEKI_PING, timeout=2).status_code == 200:
                return True
        except requests.RequestException:
            pass
        time.sleep(1)
    return False


def _run_sparql(query, accept="application/sparql-results+json"):
    r = requests.get(
        FUSEKI_SPARQL,
        params={"query": query},
        headers={"Accept": accept},
        timeout=15,
    )
    r.raise_for_status()
    if "json" in accept:
        return r.json()
    return r.text


# ----------------------------- Sanity / shape ---------------------------------

def test_dataset_triples_present(g):
    assert len(g) >= 500, f"publications.ttl unexpectedly small: {len(g)} triples."


def test_fuseki_loaded(fuseki_ready):
    if not fuseki_ready:
        pytest.skip("Fuseki not reachable on localhost:3030.")
    res = _run_sparql("ASK { ?s ?p ?o }")
    assert res.get("boolean") is True


@pytest.mark.parametrize("name, fn", [
    ("q1", q1), ("q2", q2), ("q3", q3), ("q4", q4),
    ("q5", q5), ("q6", q6), ("q7", q7), ("q8", q8),
])
def test_query_is_nonempty(name, fn):
    s = fn()
    assert isinstance(s, str) and s.strip(), f"{name}() must return a non-empty SPARQL string."


# ----------------------------- Per-query checks -------------------------------

def test_q1_neurips_authors_count(g):
    rows = list(g.query(q1()))
    assert len(rows) == GOLD["q1_neurips_authors"], (
        f"q1 returned {len(rows)} rows; expected {GOLD['q1_neurips_authors']}. "
        f"Distinct authors of papers :publishedIn :NeurIPS."
    )


def test_q2_papers_per_topic_grouped(g):
    rows = list(g.query(q2()))
    assert len(rows) == GOLD["q2_topic_groups"], (
        f"q2 returned {len(rows)} rows; expected {GOLD['q2_topic_groups']} topics. "
        f"Did you GROUP BY ?topic with COUNT(?paper) AS ?n?"
    )
    # Every row must bind two variables (?topic, ?n) and ?n must be > 0.
    bad = [r for r in rows if len(r) != 2]
    assert not bad, "Each q2 row must bind (?topic, ?n)."


def test_q3_coauthor_pairs_canonical(g):
    rows = list(g.query(q3()))
    assert len(rows) == GOLD["q3_canonical_coauthor_pairs"], (
        f"q3 returned {len(rows)} rows; expected {GOLD['q3_canonical_coauthor_pairs']}. "
        f"Common bugs: (a) missing SELECT DISTINCT — coauthors who share "
        f"multiple papers produce one row per shared paper (~230 rows); "
        f"(b) missing FILTER (str(?a) < str(?b)) — symmetric duplicates (~2x rows); "
        f"(c) self-pairs slipping through."
    )
    seen = set()
    for a, b in rows:
        assert str(a) != str(b), "q3 must not return self-pairs."
        assert str(a) < str(b), (
            f"q3 must return canonical pairs only — FILTER (str(?a) < str(?b)) "
            f"is required. Saw ({a}, {b})."
        )
        key = (str(a), str(b))
        assert key not in seen, f"q3 returned duplicate pair {key}."
        seen.add(key)


def test_q4_papers_optional_doi(g):
    rows = list(g.query(q4()))
    assert len(rows) == GOLD["q4_paper_rows"], (
        f"q4 returned {len(rows)} rows; expected {GOLD['q4_paper_rows']} papers. "
        f"Papers without :doi must still appear (?doi unbound) — use OPTIONAL."
    )
    unbound = sum(1 for r in rows if r[1] is None)
    assert unbound >= GOLD["q4_unbound_doi_min"], (
        f"q4 returned {unbound} rows with unbound ?doi; expected at least "
        f"{GOLD['q4_unbound_doi_min']}. Did you use WHERE instead of OPTIONAL "
        f"for the :doi triple?"
    )


def test_q5_ask_prolific_author(g):
    sparql = q5()
    res = bool(g.query(sparql))
    assert res is GOLD["q5_ask"], (
        f"q5 returned {res}; expected {GOLD['q5_ask']}. Use ASK with an inner "
        f"GROUP BY ?author HAVING (COUNT(?p) > 10)."
    )
    # Shape check: a wildcard ASK { ?x ?y ?z } also returns True on a non-empty
    # graph, so require the query to actually count author papers. Without
    # these the test silently passes any non-trivial ASK.
    upper = sparql.upper()
    assert "GROUP BY" in upper, (
        "q5 must include GROUP BY — a wildcard ASK passes on any non-empty graph."
    )
    assert "COUNT" in upper, (
        "q5 must include COUNT(...) — counting per-author papers is the whole point."
    )


def test_q6_construct_2023_authoredby(g):
    result = g.query(q6())
    constructed = result.graph
    assert constructed is not None, (
        "q6 must use CONSTRUCT, not SELECT. The result must be a graph."
    )
    triples = list(constructed)
    assert len(triples) == GOLD["q6_construct_triples_2023"], (
        f"q6 emitted {len(triples)} triples; expected "
        f"{GOLD['q6_construct_triples_2023']} for :year 2023 papers."
    )


def test_q7_top_5_cited_ordered(g):
    rows = list(g.query(q7()))
    assert len(rows) == 5, f"q7 must return exactly 5 rows (LIMIT 5); got {len(rows)}."
    ccs = [int(r[1]) for r in rows]
    assert ccs == sorted(ccs, reverse=True), (
        f"q7 rows must be ORDER BY DESC(?cc); got {ccs}."
    )
    assert ccs[0] == GOLD["q7_top_cc"], (
        f"q7 top citationCount is {ccs[0]}; expected {GOLD['q7_top_cc']}. "
        f"Did you sort ascending? Did you count :cites edges (none exist)?"
    )


def test_q8_hinton_skos_match(g):
    rows = list(g.query(q8()))
    assert len(rows) == GOLD["q8_hinton_matches"], (
        f"q8 returned {len(rows)} rows; expected {GOLD['q8_hinton_matches']}. "
        f"Matching only on skos:prefLabel misses the author whose canonical "
        f"name is different but who has 'Hinton' as a skos:altLabel."
    )


# ----------------------------- Grammar coverage -------------------------------

def test_grammar_coverage_across_queries():
    """All seven SPARQL clauses must appear at least once in the suite."""
    text = "\n".join(fn().upper() for fn in (q1, q2, q3, q4, q5, q6, q7, q8))
    required = ["SELECT", "CONSTRUCT", "ASK", "FILTER", "OPTIONAL", "ORDER BY", "LIMIT"]
    missing = [k for k in required if k not in text]
    assert not missing, (
        f"Suite missing required SPARQL clauses: {missing}. "
        f"The integration rubric requires every clause to appear at least once."
    )


# ----------------------------- Round-trip Fuseki ------------------------------

def test_q1_matches_fuseki(g, fuseki_ready):
    if not fuseki_ready:
        pytest.skip("Fuseki not reachable.")
    local_count = len(list(g.query(q1())))
    fuseki_rows = _run_sparql(q1())["results"]["bindings"]
    assert local_count == len(fuseki_rows), (
        f"q1 rdflib={local_count}, fuseki={len(fuseki_rows)}."
    )


def test_q7_matches_fuseki(g, fuseki_ready):
    if not fuseki_ready:
        pytest.skip("Fuseki not reachable.")
    local_ccs = [int(r[1]) for r in g.query(q7())]
    fuseki_rows = _run_sparql(q7())["results"]["bindings"]
    fuseki_ccs = [int(b["cc"]["value"]) for b in fuseki_rows]
    assert local_ccs == fuseki_ccs, (
        f"q7 ordering disagrees between rdflib and Fuseki: {local_ccs} vs {fuseki_ccs}."
    )


# Round-trip coverage for the remaining SELECT queries. The integration's
# stated goal is "run against the live Fuseki endpoint" — every query the
# learner ships must execute on Fuseki, not only q1 and q7. A query that
# uses an undeclared prefix (or any other Fuseki-rejected construct) passes
# rdflib's permissive parser but fails on Fuseki — catching it here prevents
# the learner's work from breaking in production.

@pytest.mark.parametrize("name, fn", [
    ("q2", q2), ("q3", q3), ("q4", q4), ("q8", q8),
])
def test_select_query_matches_fuseki(name, fn, g, fuseki_ready):
    if not fuseki_ready:
        pytest.skip("Fuseki not reachable.")
    local_count = len(list(g.query(fn())))
    fuseki_rows = _run_sparql(fn())["results"]["bindings"]
    assert local_count == len(fuseki_rows), (
        f"{name} row count disagrees between rdflib ({local_count}) and "
        f"Fuseki ({len(fuseki_rows)}). Common cause: an undeclared PREFIX "
        f"that rdflib tolerates but Fuseki rejects."
    )


def test_q5_ask_matches_fuseki(g, fuseki_ready):
    if not fuseki_ready:
        pytest.skip("Fuseki not reachable.")
    local_bool = bool(g.query(q5()))
    fuseki_bool = _run_sparql(q5()).get("boolean")
    assert local_bool == fuseki_bool, (
        f"q5 ASK disagrees: rdflib={local_bool}, Fuseki={fuseki_bool}."
    )


def test_q6_construct_matches_fuseki(g, fuseki_ready):
    if not fuseki_ready:
        pytest.skip("Fuseki not reachable.")
    local_count = len(list(g.query(q6())))
    fuseki_ttl = _run_sparql(q6(), accept="text/turtle")
    fuseki_g = Graph()
    fuseki_g.parse(data=fuseki_ttl, format="turtle")
    assert local_count == len(fuseki_g), (
        f"q6 CONSTRUCT triple count disagrees: rdflib={local_count}, "
        f"Fuseki={len(fuseki_g)}. Both engines should emit the same subgraph."
    )


# ----------------------------- Deliverable check ------------------------------

def test_learner_notes_filled():
    """learner_notes.md is a required deliverable. The starter ships with
    `_TODO_` placeholders in every section; submitting without filling
    them is the same as not delivering the artifact. This test enforces
    completion of the deliverable, not the quality of the notes (TA grades
    quality)."""
    notes_path = os.path.join(os.path.dirname(__file__), "..", "learner_notes.md")
    assert os.path.exists(notes_path), (
        "learner_notes.md is missing — it is a required deliverable. See the "
        "integration guide for the template."
    )
    with open(notes_path, encoding="utf-8") as f:
        text = f.read()
    # The starter ships `_TODO …_` markers in every Intent and Result
    # section. Any remaining `_TODO` token means the learner hasn't
    # completed that section.
    remaining = text.count("_TODO")
    assert remaining == 0, (
        f"learner_notes.md still contains {remaining} placeholder marker(s) "
        f"(`_TODO …_`). Fill in every Intent and Result section for Q1–Q8 "
        f"before submitting. The TA grades the quality of the notes; the "
        f"autograder only verifies they are not left as placeholders."
    )
