"""Eight SPARQL queries against the publications ontology.

Each function returns a SPARQL query string. See learner_notes.md for the
intent and result snapshot per query.
"""

# Hardcoded absolute namespace mapping to ensure local rdflib and Fuseki align
PREFIXES = """
PREFIX : <http://example.org/>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
"""

def q1():
    """Q1 — List all authors who have published at venue :NeurIPS."""
    return PREFIXES + """
    SELECT DISTINCT ?author
    WHERE {
        ?paper :publishedIn :NeurIPS ;
               :authoredBy ?author .
    }
    """


def q2():
    """Q2 — For each topic, count the number of papers on that topic."""
    return PREFIXES + """
    SELECT ?topic (COUNT(?paper) AS ?n)
    WHERE {
        ?paper :topic ?topic .
    }
    GROUP BY ?topic
    """


def q3():
    """Q3 — All author-coauthor pairs in canonical form."""
    return PREFIXES + """
    SELECT DISTINCT ?a ?b
    WHERE {
        ?paper :authoredBy ?a , ?b .
        FILTER (STR(?a) < STR(?b))
    }
    """


def q4():
    """Q4 — Every paper and its DOI, DOI OPTIONAL."""
    return PREFIXES + """
    SELECT ?paper ?doi
    WHERE {
        ?paper a :Paper .
        OPTIONAL { ?paper :doi ?doi . }
    }
    """


def q5():
    """Q5 — ASK whether any author has more than 10 papers."""
    return PREFIXES + """
    ASK {
        SELECT ?author
        WHERE {
            ?paper :authoredBy ?author .
        }
        GROUP BY ?author
        HAVING (COUNT(?paper) > 10)
    }
    """


def q6():
    """Q6 — CONSTRUCT a graph of 2023 papers and their authors."""
    return PREFIXES + """
    CONSTRUCT {
        ?paper :authoredBy ?author .
    }
    WHERE {
        ?paper :year 2023 ;
               :authoredBy ?author .
    }
    """


def q7():
    """Q7 — Top 5 most-cited papers by literal :citationCount, DESC."""
    return PREFIXES + """
    SELECT ?paper ?cc
    WHERE {
        ?paper :citationCount ?cc .
    }
    ORDER BY DESC(?cc)
    LIMIT 5
    """


def q8():
    """Q8 — Authors whose name matches "Hinton" via skos:prefLabel OR skos:altLabel."""
    return PREFIXES + """
    SELECT DISTINCT ?author
    WHERE {
        ?author ?labelProperty "Hinton" .
        FILTER (?labelProperty = skos:prefLabel || ?labelProperty = skos:altLabel)
    }
    """