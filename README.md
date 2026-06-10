# Integration 9A — SPARQL Query Suite

Follow the learner-facing integration guide on the AISPIRE course site.

**Deliverables:**

1. Implement `q1()` through `q8()` in `queries.py` per each docstring. Together the eight queries must exercise SELECT / CONSTRUCT / ASK / FILTER / OPTIONAL / ORDER BY / LIMIT.
2. Fill in `learner_notes.md` with a one-sentence intent and a first-5-row snapshot per query.
3. Open a PR with `learner_notes.md` rendered (or linked) in the description.

`load_dataset.py` is complete — bring up Fuseki, run it once, then `pytest tests/ -v`.

Local run:

```bash
pip install -r requirements.txt
docker compose up -d
python load_dataset.py
pytest tests/ -v
```

---

## License

This repository is provided for educational use only. See [LICENSE](LICENSE) for terms.

You may clone and modify this repository for personal learning and practice, and reference code you wrote here in your professional portfolio. Redistribution outside this course is not permitted.
