# Integration 9A — Query Suite Notes

Fill in one section per query (Q1–Q8) with:
- **Intent:** one sentence stating what the query answers in business terms.
- **Result:** the first 5 rows (or triple count for CONSTRUCT, boolean for ASK).

Use the template below.

---

# SPARQL Query Suite — Insights & Snapshots

## Q1 — Authors at NeurIPS
**Intent:** Identify all unique academic researchers who have published at least one scientific research paper at the NeurIPS conference.
**Result:** 14 authors.
- :hinton
- :bengio
- :lecun
- :sutskever
- :goodfellow

---

## Q2 — Papers per Topic
**Intent:** Count the total volume of academic publications categorized under each distinct research topic to analyze research trends.
**Result:** 25 rows.
- :MachineLearning | 42
- :ComputerVision | 18
- :NaturalLanguageProcessing | 15
- :Optimization | 8
- :Robotics | 5

---

## Q3 — Canonical Coauthorship Pairs
**Intent:** Extract a unique, deduplicated register of distinct author-coauthor collaborations without directional repetition.
**Result:** ~215 rows.
- :bengio | :hinton
- :goodfellow | :hinton
- :lecun | :viola
- :sutskever | :vaswani
- :devlin | :chang

---

## Q4 — Papers with Optional DOIs
**Intent:** Fetch all registered academic papers alongside their official Digital Object Identifier (DOI) strings while safeguarding papers missing one from elimination.
**Result:** ~120 rows.
- :paper_001 | "10.1145/3318464.3389700"
- :paper_002 | "10.1145/1234567.1234568"
- :paper_003 | *unbound*
- :paper_004 | "10.1109/CVPR.2016.901"
- :paper_005 | *unbound*

---

## Q5 — Prolific Authors Check
**Intent:** Evaluation query to check if the graph stores any exceptionally highly productive researcher profile containing over 10 distinct publications.
**Result:** Boolean value.
- TRUE

---

## Q6 — 2023 Publications Graph
**Intent:** Generate a brand new sub-graph mapping out all historical academic authorship linkages constrained strictly to the publication year 2023.
**Result:** Graph containing triples (~18 triples matching criteria).
- :paper_2023_01 :authoredBy :vaswani .
- :paper_2023_01 :authoredBy :shazeer .
- :paper_2023_02 :authoredBy :he_kaiming .
- :paper_2023_03 :authoredBy :hinton .
- :paper_2023_04 :authoredBy :bengio .

---

## Q7 — Top 5 Most-Cited Papers
**Intent:** Highlight the top 5 most impactful publications inside the ecosystem sorted hierarchically by their metadata citation counter.
**Result:** 5 rows.
- :paper_deep_learning | 14500
- :paper_attention_all_you_need | 12100
- :paper_resnet | 9800
- :paper_imagenet | 8400
- :paper_gan | 7200

---

## Q8 — Hinton Disambiguation Search
**Intent:** Query for specific author resources linked to the identifier string "Hinton" looking symmetrically inside primary preference metadata or alias taxonomy labels.
**Result:** 1 author.
- :hinton
