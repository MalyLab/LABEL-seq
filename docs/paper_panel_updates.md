# Paper panels to replace — since the rSASA / HGFR update (2026-10-01)

Panels already replaced in the paper: everything touched by the buried = rSASA < 0.25
change (Fig 3b, ED 3b, ED 3e) and the MET → HGFR relabel. The list below is what
changed **after** that, in the order the fixes were made. Each item names the file
to take from `output/figures/` and why it changed. "Content" = data changed;
nothing below is a pure styling change.

Checked by diffing every regenerated file against the previous one with
timestamps, matplotlib's random SVG ids and PyMOL ray-tracing noise removed —
so a panel not listed here is unchanged.

## 1. ARAF domains from a CD-search of native ARAF (2ecf9d2)

The 2025-08-20 NCBI CD-search for ARAF was run on a sequence with 66 extra
N-terminal residues, so every ARAF domain and site was 66 residues off.

| paper panel | file | what changes |
|---|---|---|
| **ED 1a** | `fig1/ED_1a_drawproteins.svg` (`.png`) | ARAF row only: kinase 309–573, RBD 19–91, CRD 96–147. |

## 2. ARAF active site corrected; one border rule in ED 7a (bd603c6)

The same shift had put ARAF's `active_site` on 2 spurious residues and missed the
real 46 (316–471).

| paper panel | file | what changes |
|---|---|---|
| **ED 3b** | `fig2/ED 3c.svg` | "Active site" category gains ARAF's 46 positions. |
| **ED 3e** | `fig2/ED 3e.svg` | Same. |
| **Fig 4c** | `fig4/4c_structural_enrichment_forest.svg` | Missense AS OR 2.64 → 3.05; deletion AS 1.98 → 2.35; missense buried 2.25 → 2.07; deletion buried 2.64 → 2.50; nonsense AS 0.56 → 1.01 (q 0.95); nonsense buried 1.05 → 0.98. |
| **Fig 4d** | `fig4/4d_ontology_composition.svg` | ARAF DNs move from buried to active site; 82% of DN assignments unchanged. |
| **ED 7a** | `fig4/ExtDataDN7a_per_protein_squares.svg` | ARAF AS and buried cells; and the square border now has one rule, q < 0.01 with OR > 1. |

Text numbers to update with these: Fig 4c ORs above; ARAF buried 1,846 of 3,235
DNs (1,760, 95%, in the kinase domain), OR 4.14, q 6.3e-236; ARAF AS 385, OR 2.01.

## 3. Depletion null set no longer drops 47 real positions (this commit)

The missense set tested for depletion was `min_nt_changes == 1 & gnomad_mappable`.
`gnomad_mappable` came from the retired position-offset gnomAD lookup and was
False at 47 positions that do have GRCh38 coordinates (KRAS 151–188, the 4B
exon; BRAF 762–766; KSR1 503–507; SOS1 939) — some of which are even observed in
gnomAD. The filter is now `min_nt_changes == 1`, which is the restriction the test
needs; 352 SNV-reachable missense variants (6 DN) rejoin, out of 66,245.

| paper panel | file | what changes |
|---|---|---|
| **Fig 4 depletion** (her `4f`; the text cites it as Fig. 4h) | `fig4/4f_depletion_pooled.svg` | Counts shift slightly (gnomAD DN 191/4,563 → 192/4,569; low 724/10,256 → 726/10,309; high 930/7,175 → 937/7,208); every OR moves by < 0.01. **One star changes: GENIE DN `**` → `*`** (q 0.007 → 0.013, OR 0.84 → 0.85). Nonsense rows unchanged. |
| **ED 7f** | `fig4/ExtDataDN7f_depletion_heatmap.svg` | KRAS cells change. Significance changes: gnomAD KRAS DN `*` → `**` (OR 0.12 → 0.11); GENIE KRAS low `*` → ns (OR 0.55 → 0.69); GENIE EGFR DN `*` → ns (counts unchanged; BH q 0.048 → 0.052). |

Text numbers: any quoted DN-vs-WT-like depletion OR or count (e.g. gnomAD DN OR
0.26, 192 of 4,569; GENIE DN OR 0.85, q 0.013).

## 4. ED 8b refitted on the current tables (this commit)

The per-protein factor table ED 8b reads was fitted on 2026-08-28, in the old
repository, from the tables of that date. It is now refitted by
`scripts/fit_buffering_factors_per_protein.py` on the cohort Fig 5f / ED 8c use
(44,905 classified kinase-domain missense; 40,041 with every predictor — the
rest lack a kinase-JSD value), with the same model (univariate multinomial logit
per protein and feature, ≥ 5 positions per class).

| paper panel | file | what changes |
|---|---|---|
| **ED 8b** | `fig5/ExtDataHSP908b_per_protein_univariate_r2.svg` (and `_horizontal`) | **ARAF gains an "Active site" cell** (blank before: the shifted annotation left 2 positions): Buffered vs WT-like β = 0.59, p = 1.2e-9. The interface row is now the curated 4 Å PDB interface, so its label changes from "Any interface" (the old table's `at_any_interface`) to "Protein interface", and its cells change: **RET (β −1.23) and MEK2 (−1.35) gain cells, ARAF flips 0.74 → −0.08**, CRAF/KSR2/EGFR/BRAF/MEK1 within 0.05. "Interface degree" now counts that interface's partners — RET's cell moves 0.03 → −1.24. Everything else agrees with the old fit (r = 0.986 over the Buffered-vs-WT-like coefficients both fits estimate; feature ranking unchanged: ΔΔG, relative SASA, contacts 12 Å, depth, contacts 8 Å, JSD). |

## 5. Two figure bugs found while checking the legends (this commit)

| paper panel | file | what changes |
|---|---|---|
| **Fig 1c** | `fig1/1c_waterfall.svg` | EGFR's catalytic-lysine marker was keyed to K753M, which in EGFR is P753 — no marker was drawn. Now K745M (ERBB2's K753M, its own catalytic lysine, unchanged). |
| **Fig 5a** | `fig5/5a_hsp90i_measurement_wheel.svg` | WT rows no longer counted as variants: centre label 106,655 → **106,642**, and each protein's n drops by its WT rows. |

| **ED 1a** | `fig1/ED_1a_drawproteins.svg` | Adds the BRAF-specific region (41–106) from the curated bounds; NCBI CD-search has no domain there. The other domains stay NCBI, as descriptive annotation. |

Legend only (no code change): Fig 1b activity n = **183,552** (Fig 1b's filter already excluded WT).

## 6. ED 9 violins: the reference group is every scored position (this commit)

The violin group labelled "All (domain)" was never restricted to domains — the code
fills it with every scored position of the protein. Relabelled "All positions"; no
values change.

| paper panel | file |
|---|---|
| **Fig 6b (bottom) / ED 9d** | `fig6/braf_braf_violins.pdf` |
| **ED 9f** | `fig6/craf_interface_violins.pdf` |
| **ED 9h** | `fig6/braf_itch_violins.pdf` |

Fig 4f's data table (`fig4/fig3i_class_depletion_pooled.tsv`) now carries the same
four-tier stars as the plotted annotation; the panel itself is unchanged.

## 7. ED 1d compares single-nucleotide missense variants, as its legend says (this commit)

The GENIE-enrichment heatmap's table was meant to be basal-activity missense (its own
header comment says so) but never filtered on variant type, so every fraction and every
Fisher reference set also held synonymous, nonsense, frameshift, standard and WT rows.
Now single-nucleotide missense only.

| paper panel | file | what changes |
|---|---|---|
| **ED 1d** | `fig2/ED 3f.svg` | Fractions recomputed on 1-nt missense. Outlines: Pooled "All GENIE" none → black; MEK1 "All GENIE" gray → black; MEK2 "All GENIE" none → black and "≥ 5" gray → black; RET "≥ 5" none → gray; ARAF and HGFR "All GENIE" gray → none. Same 12 proteins. |

Fig 1b (`fig1/1b_replicates.svg`) no longer plots the 43 WT rows; the panel is
pixel-identical (they sat at 1,1) and r is unchanged.

## Not affected

* **Fig 5 / ED 8 other than ED 8b** — re-run after the ARAF fix; every panel identical.
* **Fig 6e–i** — re-run; every panel identical.
* **Fig 1–3 otherwise, Fig 6a–d** — read nothing that changed.

## Still open — decide before the panels are final

* **Fig 4b** — the ERBB2 "??" placeholder.
* **ED 3b/3e** — which test the stars use.
* **WT dependence** — "seven vs five" in the text.
* **Fig 6e–i** — KRAS No_treatment ΔCIAR panel; 9MF0 chains A/B vs E/F.
