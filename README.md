# Breast cancer single-cell and proteomic analysis

This repository contains the analysis notebooks and shared Python helpers for breast-cancer single-cell and proteomic analyses. The workflow reanalyses filtered count matrices from GSE161529 and includes separate analyses of epithelial cell states, antigen expression, normal-tissue protein reference data, and published proteomics cohorts.

Tumour-derived epithelium is defined by specimen origin. CNV-high status is a sensitivity definition, not a complete malignancy classifier. Antigen detection is based on raw UMI counts; ALRA values are used only for exploratory diagnostics. Protein abundance associations do not demonstrate molecular interaction or same-cell co-expression.

## Reproducibility record

This repository is the record of analysis run `cap_preprocessing_20261120_210737`, frozen at the commit tagged `freeze-cap_preprocessing_20261120_210737`.

- [LIMITATIONS.md](LIMITATIONS.md) states what the record establishes and what it does not, including stages run interactively, post-run notebook edits, and the Papermill launch wrapper whose run-time version could not be recovered.
- [run_records/](run_records/) contains the per-stage provenance, input checksums, notebook audit, and the output manifest.
- [VALIDATION.md](VALIDATION.md) describes what has and has not been validated.

## Repository layout and data

The repository root is this directory, identified by `pyproject.toml`. Large inputs and run outputs are kept outside the repository under `CAP_DATA_ROOT`. The repository includes selected frozen reference files under `data/frozen/` and their checksum manifest under `data/manifests/`.

The path helper reads two configuration values:

```text
CAP_DATA_ROOT=C:/path/to/CAP_Data
CAP_RUN_ID=your_run_id
```

The same `CAP_RUN_ID` identifies all stages of one analysis run. Use a new ID for each new run. The path helper derives the input and output locations from `CAP_DATA_ROOT`, so no other environment variables are needed. Set these values in your shell, or in a local `.env` file based on [`.env.example`](.env.example). Local `.env` files are not tracked by Git.

Expected external inputs include:

- Filtered GSE161529 matrices: `$CAP_DATA_ROOT/raw/gse161529/raw_counts/`
- Shared feature file: `$CAP_DATA_ROOT/raw/gse161529/features.tsv`
- GENCODE annotation: `$CAP_DATA_ROOT/references/gencode/gencode.v50.annotation.gtf.gz`
- CellTypist model: `$CAP_DATA_ROOT/references/celltypist/model_from_pal.pkl`
- HPA reference archive: `$CAP_DATA_ROOT/references/hpa/dvp_cell_type_group_data.tsv.zip`
- Three-proteome supplements: `$CAP_DATA_ROOT/references/proteomics/`

The proteomics directory must contain `Lee_MOESM2_ESM.csv`, `Lehmann.csv`, `mmc2.xlsx`, `cd-22-0200_table_s3_suppst3.xlsx`, `cd-22-0200_table_s1_suppst1.csv`, `h.all.v2026.1.Hs.symbols.gmt`, and `lee_uniprot_gene_mapping.csv`.

The cohort is defined by `000_Raw_Data_And_Cohort.ipynb`, which builds the sample sheet from the raw library files and the exclusion rules recorded in that notebook. Stage 01 additionally requires the frozen cohort release `config/cohort_release_2026-11-13.csv`. That file is not included in this repository because it is git-ignored, and it must be supplied separately. [State how it can be obtained.] The 01 driver checks that the release's included samples match the 00 sample sheet.

## Environment and setup

The reported Windows environment is named `cap-rerun`. From PowerShell, activate it, install this repository in editable mode, and register the notebook kernel:

```powershell
conda activate cap-rerun
Set-Location C:\path\to\CAP_Analysis
python -m pip install -e .
python -m ipykernel install --user --name cap-rerun --display-name "Python (cap-rerun)"
```

Start Jupyter or the IDE from inside the repository directory so the path helper can locate `pyproject.toml`. Restart the notebook kernel after changing the package or environment.

The checked-in `environment.yml` and `environment_R.json` record an Apple Silicon/macOS environment. They are not validated Windows lockfiles. The Windows R setup and the current validation limits are described in [ENVIRONMENT.md](ENVIRONMENT.md). A fresh Windows installation and the complete R-dependent single-cell workflow have not yet been confirmed.

## Notebook workflow

The core single-cell chain is `000` → `001` → `002` → `003a` → `003b` → `003c` → `004`. Notebook `001_Papermill.ipynb` is the driver: it runs `001_Preprocessing.ipynb` once per included sample, passing the sample ID as a parameter. Notebooks `003d_Normal_Tissue_Protein.ipynb` and `005_Three_Proteome.ipynb` are independent of that single-cell chain.

| Notebook | Stage | Purpose |
|---|---|---|
| [000_Raw_Data_And_Cohort.ipynb](notebooks/000_Raw_Data_And_Cohort.ipynb) | `00_cohort` | Inventory raw libraries and write the cohort table. |
| [001_Papermill.ipynb](notebooks/001_Papermill.ipynb) | `01_preprocessing` | Run per-sample preprocessing through Papermill. |
| [001_Preprocessing.ipynb](notebooks/001_Preprocessing.ipynb) | `01_preprocessing` | Preprocess one library; normally invoked by the Papermill driver. |
| [002_Celltype_ID.ipynb](notebooks/002_Celltype_ID.ipynb) | `02_cell_annotation` | Integrate the atlas and annotate cell types. |
| [003a_Epithelial_Integration.ipynb](notebooks/003a_Epithelial_Integration.ipynb) | `03a_epithelial_integration` | Integrate epithelial cells and perform the CNV sensitivity analysis. |
| [003b_Meta_Programmes.ipynb](notebooks/003b_Meta_Programmes.ipynb) | `03b_meta_programmes` | Score meta-programmes and compare cell states. |
| [003c_Antigen_Coexpression.ipynb](notebooks/003c_Antigen_Coexpression.ipynb) | `03c_antigen_coexpression` | Analyse antigen detection, donor comparisons, and sensitivities. |
| [003d_Normal_Tissue_Protein.ipynb](notebooks/003d_Normal_Tissue_Protein.ipynb) | `03d_normal_tissue_protein` | Analyse normal-tissue protein reference data. |
| [004_Programme_Summary.ipynb](notebooks/004_Programme_Summary.ipynb) | `04_programme_summary` | Summarise programme scores across epithelial clusters. |
| [005_Three_Proteome.ipynb](notebooks/005_Three_Proteome.ipynb) | `05_three_proteome` | Analyse prespecified protein-abundance associations across three proteomics cohorts. |

Use a fresh kernel for each notebook. Run the core chain in order. Run `003d` and `005` separately when their inputs are available. The notebooks in this repository are output-stripped; the executed outputs are kept outside the repository, as described under Run outputs.

## Run outputs

Stage outputs are stored outside the repository under:

```text
$CAP_DATA_ROOT/runs/$CAP_RUN_ID/<stage>/
```

The stage directories are `00_cohort`, `01_preprocessing`, `02_cell_annotation`, `03a_epithelial_integration`, `03b_meta_programmes`, `03c_antigen_coexpression`, `03d_normal_tissue_protein`, `04_programme_summary`, and `05_three_proteome`. Depending on the stage, outputs include H5AD objects, models, tables, figures, logs, and executed notebooks. Each stage directory also holds its `run_provenance.json` and `input_checksums.json`.

**Known limitation,
**Rerun behaviour:** the notebooks refuse to write into an existing stage directory. Use a new `CAP_RUN_ID` for any test or rerun. A failed run's partial stage must be removed by hand, after its contents have been checked.

Figures should be saved through the shared helpers in [`src/cap/figures.py`](src/cap/figures.py). Path and run configuration is implemented in [`src/cap/paths.py`](src/cap/paths.py), and provenance helpers are in [`src/cap/provenance.py`](src/cap/provenance.py).
