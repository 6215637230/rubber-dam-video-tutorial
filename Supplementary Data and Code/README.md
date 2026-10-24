# Data and code for the simulated methodological worked example

All 189 records, 378 paired-rating rows and constructed retrieval logs are simulated. No actual videos were accessed or rated, no human assessors participated, and no historical search was performed. Identifiers beginning SIM and example.invalid URLs are test labels. These materials support the explicitly simulated worked example only.

## Contents
- records/: six CSVs for metadata, paired and final items, resolution, query settings and retrieval slots.
- original_outputs/: the existing generated CSV tables, dictionary and full-precision JSON.
- additional_outputs/: all 84 pairwise confidence intervals, metadata summaries, PEMAT denominators, VIFs and exploratory deletion sensitivity outputs.
- code/generate_simulated_package.py: original generator and statistics script, unchanged.
- code/additional_analysis.py: the existing extra numerical analyses with portable paths; the original plotting block is omitted. Numerical formulas, sequence and seed are unchanged.
- code/reproduce.py: runs both stages into a separate reproduced/ directory and compares all nested numeric and nonnumeric outputs with the archived JSON.

## Reproduce
Use Python 3.12.14 and NumPy 2.3.5. From the extracted directory run:

    python code/reproduce.py

This command can take several minutes. It does not overwrite the archived records or outputs. A successful run writes reproduced/verification.json. Other compatible versions may differ in the last digits; the comparison uses relative tolerance 1e-9 and absolute tolerance 1e-10. The script fails on an unmatched value instead of silently accepting it.

Seeds are 2026090702 for construction, 2026090703 for the original statistics and 2026090801 for additional analyses. The draw sequence in the scripts is part of reproducibility. Regeneration is a check of the same fixed example, not a second independent simulation scenario. Bootstrap samples and permutations are conditional calculations within that dataset.

The original generator writes a historical Chinese README along with its reproduced outputs. Its prohibition on presenting these records as real observational evidence remains applicable. Its wording predates the present explicitly simulated article and is not a description of a newly collected real dataset.

The two Word documents are a narrative reorganization of these unchanged numerical records. Manuscript Figure 2 now shows domain coverage and Figure 3 source comparisons. Figure rendering is not part of the numerical reproduction command. Dataset consistency does not establish clinical validity, human-rater reliability, or statistical performance across independent generated datasets.

The archive is prepared for local sharing. No public repository deposition or journal upload is implied.
