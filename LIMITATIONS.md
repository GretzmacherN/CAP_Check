# Limitations: cap_preprocessing_20261120_210737

This record documents what was run and what can and cannot be verified from Git and the archived outputs. It does not claim that every stage can be reproduced from its recorded commit.

## Commits and run mode

The stages ran on six different commits: 74d4395, 9124e1a, c4bec59, 38764bd, 8189a95 and 1012ae6. Only stage 01 ran through Papermill, one executed copy per sample (43 samples). All other stages were run interactively, cell by cell in PyCharm. Interactive runs have no executed copy, so the saved notebook (with outputs and execution counts) is the only record of what ran.

## Dirty stages

Stages 01, 02, 03a, 03b, 03d and 05 were dirty at run time, mainly from saved notebook outputs. Stage 03d also ran while notebooks 001, 002, 003a, 003b and 003c had uncommitted changes. Stages 00, 03c and 04 were clean. The dirty flags are historical and do not change when the record is committed.

## Notebook integrity (audit)

| Stage | Run code matches run commit | Current file matches run | Status |
|---|---|---|---|
| 00 | Yes | No | Two read-only diagnostic cells added after the run |
| 01 | Driver: No; analysis code: Yes | Driver: No | See the 01 section |
| 02 | Yes | No | Post-run edits; see below |
| 03a | Yes | Yes | Verified. The committed version was restored after output stripping; the archive keeps the outputs. |
| 03b | Yes | No | Read-only cells added after the run |
| 03c | Yes | Yes | Verified. The committed version was restored after output stripping; the archive keeps the outputs. |
| 03d | Yes | No | Cell removal and reordering; see below |
| 04 | Yes | Yes | Verified |
| 05 | No (the run used uncommitted code) | Yes | The run code equals the current file and the committed version. |

## Stage 01

- The analysis notebook `notebooks/001_Preprocessing.ipynb` at commit 9124e1a is identical, cell for cell, to all 43 executed copies.
- The launch wrapper `notebooks/001_Papermill.ipynb` is not recoverable. Its run-time version hashes to 25627e1f…, which matches neither the committed nor the working version. The wrapper's exposed settings (RUN_DEMO, DEMO_IDS, KERNEL_NAME) are not recorded per sample.
- Coverage: the 43 executed samples equal the 43 cohort rows with include = True and files present.

## Post-run changes

- **00:** Two read-only cells were added at the top (provenance and package checks). No analysis line was removed or changed. Cells 0 and 1 carry outputs from diagnostic runs, and the notebook's execution counts show a kernel restart.
- **02:** `model.save(..., overwrite=True)` replaces `overwrite=False`, so re-running would overwrite the saved model without an error. A diagnostic cell that read from an earlier run folder (preprocessing_test_003) was removed. An empty cell (index 272) never ran. Both export cells ran (`cell_metadata.csv`, `barcode_table.csv`), and both files exist in the stage's tables folder. The diff shows a reordering only; nothing changed in the outputs.
- **03b:** Read-only checks were added. One of them (index 3) ran late in the session, after the analysis cells, and the counts show a kernel restart.
- **03d:** A diagnostic git cell was removed, and four cells were moved (gene_order, load_hpa, score_hpa, the hpa_summary rank line). In the saved session the moved cells ran in their current order, and each dependency runs before the cell that uses it. The recorded provenance hash, however, matches the committed order, not the order that produced the saved outputs. Whether the committed order gives identical results is not verified. Only a rerun from the commit can settle that.

## Environment

- ALRA was installed from GitHub HEAD and is not version-pinned. fastRPCA was skipped (optional, needs Rtools).
- R and Python package versions are recorded in each stage's provenance.
- The Windows environment was not validated from a fresh install.
- A stale editable install pointed Python at an older checkout (CAP_PREVERSION). Runs used PYTHONPATH to override it. `.env` still contains an older CAP_RUN_ID.

## Data and outputs

- The cohort file (config/cohort_release_2026-11-13.csv) is excluded from Git because it contains coded patient IDs, so the repository alone cannot regenerate stage 00.
- Large outputs and the notebooks with outputs are in D:\CAP_Data and are verified by the SHA-256 manifest in run_records/.
- Stages 003a to 05 were rerun in this run after deleting earlier attempts. Those earlier attempts are not part of this record.
- Notebooks as they were at the end of the run, with outputs and execution counts, are in D:\CAP_Data\...\notebooks_with_outputs, with SHA-256 checksums in SHA256SUMS.csv. The output manifest was built before this archive, so the checksums file is the reference for these notebooks.
- The notebooks in `notebooks_with_outputs` are checked with SHA-256 checksums in `SHA256SUMS.csv`. Stages 03a, 03c, 04 and 05 match the recorded hash in the archive; the other archived notebooks reflect the state at archive time, after their documented post-run edits.