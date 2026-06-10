"""Eight SPARQL queries against the publications ontology.

Each function returns a SPARQL query string. See learner_notes.md for the
intent and result snapshot per query.
"""


def q1():
    """Q1 — List all authors who have published at venue :NeurIPS.

    Variables in the SELECT: ?author.
    """
    # TODO: SELECT distinct authors of papers where ?paper :publishedIn :NeurIPS.
    return ""


def q2():
    """Q2 — For each topic, count the number of papers on that topic.

    Variables in the SELECT: ?topic ?n.
    Use GROUP BY ?topic and COUNT(?paper) AS ?n.
    """
    # TODO: SELECT with GROUP BY topic.
    return ""


def q3():
    """Q3 — All author-coauthor pairs in canonical form.

    Variables in the SELECT: ?a ?b.

    Two requirements (omit either and the row count is wrong):
    1. `SELECT DISTINCT ?a ?b` — coauthors who share multiple papers
       otherwise produce one row per shared paper (~230 rows on this
       fixture); DISTINCT collapses them to one row per pair (~215).
    2. `FILTER (str(?a) < str(?b))` — without it, each unordered pair
       appears twice (a,b) and (b,a).
    """
    # TODO: SELECT DISTINCT ?a ?b WHERE { ?p :authoredBy ?a, ?b . FILTER ... }
    return ""


def q4():
    """Q4 — Every paper and its DOI, DOI OPTIONAL.

    Variables in the SELECT: ?paper ?doi.
    The :doi triple must live inside OPTIONAL { ... } — putting it in the
    main WHERE drops papers without a DOI.
    """
    # TODO: ?paper a :Paper . OPTIONAL { ?paper :doi ?doi } .
    return ""


def q5():
    """Q5 — ASK whether any author has more than 10 papers.

    Returns a boolean.
    """
    # TODO: ASK against a sub-SELECT that COUNTs papers per author with HAVING.
    return ""


def q6():
    """Q6 — CONSTRUCT a graph of 2023 papers and their authors.

    Returns triples ?paper :authoredBy ?author for papers with :year 2023.
    """
    # TODO: CONSTRUCT { ... } WHERE { ?paper :year 2023 ; :authoredBy ?author }
    return ""


def q7():
    """Q7 — Top 5 most-cited papers by literal :citationCount, DESC.

    Variables in the SELECT: ?paper ?cc.
    """
    # TODO: ORDER BY DESC(?cc) LIMIT 5 against ?paper :citationCount ?cc.
    return ""


def q8():
    """Q8 — Authors whose name matches "Hinton" via skos:prefLabel OR skos:altLabel.

    Variables in the SELECT: ?author.
    """
    # TODO: union of prefLabel / altLabel matches on "Hinton".
    return ""
