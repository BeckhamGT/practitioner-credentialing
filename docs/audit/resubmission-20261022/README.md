# Independent audit evidence

These files document the audit of passed commit `cbc1d70a40724f48d82aaf074c8bb2dc131fb7f7`. They are not new assessed snapshots, a submission receipt, learner approval, or a replacement for genuine Entire records. No runtime implementation was changed.

- `baseline-results.json`, `execution-log.json`, `tests.txt`, `tests-receipt.json`: actual fresh tests and isolated 1→2→3 replay; exact published workflow hashes reproduced.
- `independent-workflow-checks.json`: all 120 original-CSV/report comparisons, computed without importing product business logic.
- `additional-independent-checks.json`, `audit_checks.py`: original source metadata, dates, all policy-version citations, selected case comparisons and proposed application-fragment schema validation. The proposal count is a mechanical representation experiment, not approval of new business outcomes.
- `diagnostic-probes.json`, `probes.py`: four deliberately synthetic counterexamples to claimed reusable behavior. Every invented source remains in a temporary SYNTH dataset. These probes expose failures; they are not added passing product tests.
- `proposed-APP014-batch1.json`: clearly labeled individual application proposal; not a complete batch, not written to required snapshot paths.
- `fresh-synthetic-proof.json`: newly rerun, explicitly synthetic workflow demo. Its absolute paths refer to this local audit's disposable output.
- `fresh-policy-comparison.json`: freshly retrieved core-policy text versus the original archive; differences are extraction formatting/list numbering, not an authorized new export convention.
- `capture-remote-comparison.json`, `capture-record-comparison.json`: fresh public readback, Git object and actual payload comparisons. No conversation was reconstructed and no sync was inferred from configuration. The local current audit continues in the genuine live transcript; a new audit commit/checkpoint has not yet been created.
- `external-state-observations.json`: analyst's explicit read-only observations of GitHub, Tacitt and Classroom. It is not presented as a platform-generated receipt.
- `preservation.json`: all 197 pre-existing tracked files unchanged; original interview matches Downloads byte-for-byte; schema hash unchanged.

Full raw command stdout/stderr and fresh input/state trees remain under `.local/resubmission-audit-20261022/`. `reproduce.py` is the exact wrapper used; it intentionally fails if its output directory already exists. For another independent replay, use a fresh output directory in a copy of that wrapper, preserve this audit's evidence, and run from the repository root with the existing `.venv`. Run `probes.py` and `audit_checks.py` from the repository root after creating the audit output directory. They only write their own audit evidence and use temporary stores for synthetic probes. They do not repair or replace original inputs, histories or reports.

The audit report and requirements matrix are the review entrypoints. New files remain local and uncommitted pending this audit review; the passed public revision has not changed. No privacy, publication or resubmission operation was performed.
