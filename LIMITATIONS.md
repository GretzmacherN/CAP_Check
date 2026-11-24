# Limitations: cap_preprocessing_20261120_210737

This record documents what was run and what can and cannot be verified from Git and the archived outputs. It does not claim that every stage can be reproduced from its recorded commit.

## Commits and run mode

The stages ran on six different commits: 74d4395, 9124e1a, c4bec59, 38764bd, 8189a95 and 1012ae6. Only stage 01 ran through Papermill, one executed copy per sample (43 samples). All other stages were run interactively, cell by cell in PyCharm. Interactive runs have no executed copy, so the saved notebook (with outputs and execution counts) is the only record of what ran. Several commits in the history carry the message "added 005 to paths.py". The record identifies commits by hash, not by message.

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
- The launch wrapper `notebooks/001_Papermill.ipynb` is not recoverable. Its run-time version hashes to 25627e1f..., which matches neither the committed nor the working version. The wrapper's exposed settings (RUN_DEMO, DEMO_IDS, KERNEL_NAME) are not recorded per sample.
- Coverage: the 43 executed samples equal the 43 cohort rows with include = True and files present.

## Post-run changes

- **00:** Two read-only cells were added at the top (provenance and package checks). No analysis line was removed or changed. Cells 0 and 1 carry outputs from diagnostic runs, and the notebook's execution counts show a kernel restart.
- **02:** `model.save(..., overwrite=True)` replaces `overwrite=False`, so re-running would overwrite the saved model without an error. A diagnostic cell that read from an earlier run folder (preprocessing_test_003) was removed. An empty cell (index 272) never ran. Both export cells ran (`cell_metadata.csv`, `barcode_table.csv`), and both files exist in the stage's tables folder. The diff shows a reordering only; nothing changed in the outputs.
- **03b:** Read-only cells were added. One of them (index 3) ran late in the session, after the analysis cells, and the counts show a kernel restart.
- **03d:** A diagnostic git cell was removed, and four cells were moved (gene_order, load_hpa, score_hpa, the hpa_summary rank line). In the saved session the moved cells ran in their current order, and each dependency runs before the cell that uses it. The recorded provenance hash, however, matches the committed order, not the order that produced the saved outputs. Whether the committed order gives identical results is not verified. Only a rerun from the commit can settle that.

## Notebook defects in the frozen code

These defects were found during review. They are documented, not corrected, because changing the notebooks would change the code this record describes.

- The `001_Papermill` markdown says a full run deletes the existing `01_preprocessing` stage. The notebook contains no deletion code and refuses to write into an existing stage. The markdown is out of date.
- `001_Papermill` imports `shutil`, which it doesn't use.
- `000_Raw_Data_And_Cohort`, `001_Papermill` and `001_Preprocessing` contain diagnostic cells (environment and Git printouts, a provenance probe, and a stray `#None` comment in the parameters cell). They don't alter outputs.
- `001_Preprocessing` checks for `notebooks/001_preprocessing.ipynb` in lowercase, but the file is `001_Preprocessing.ipynb`. This works on Windows but fails on a case-sensitive file system.
- Stage 01 reads the cohort release file in `config/`. That file was git-ignored in the working repository during the analysis. It is committed in this submission as a separate commit after the freeze, so the frozen analysis commit does not contain it.

## Environment

- ALRA was installed from GitHub HEAD and is not version-pinned. fastRPCA was skipped (optional, needs Rtools).
- R and Python package versions are recorded in each stage's provenance.
- The Windows environment was not validated from a fresh install.
- A stale editable install pointed Python at an older checkout (CAP_PREVERSION). Runs used PYTHONPATH to override it. `.env` still contains an older CAP_RUN_ID.

## Data and outputs

- The cohort release file was git-ignored in the working repository during the analysis. It contains coded patient IDs and is committed in this submission as a separate commit after the freeze. Stage 00 does not read it; stage 01 does.
- Large outputs are in D:\CAP_Data. The output manifest in run_records/ was built before the notebook archive existed, so it covers the run folder only.
- This record describes the final run. The stage records don't include timestamps or attempt history, so earlier attempts are not documented here.
- The notebooks as they were at the end of the run, with outputs and execution counts, are in D:\CAP_Data\runs\cap_preprocessing_20261120_210737\notebooks_with_outputs. Their SHA-256 checksums are in SHA256SUMS.csv. The six notebooks for stages 003a to 005 (003a, 003b, 003c, 003d, 004 and 005) were checked against those checksums, and all match. The other archived notebooks reflect the state at archive time, after their documented post-run edits.
- The submission repository's history is the frozen analysis commit, then one documentation commit correcting the README and this note, then one commit adding the cohort release file, then one documentation commit for the data source and release-file description.
