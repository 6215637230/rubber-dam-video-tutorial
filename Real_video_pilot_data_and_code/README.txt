REAL VIDEO EVIDENCE PILOT — 22 October 2026

This package contains observed public-video metadata and AI-assisted evidence annotations. It is separate from the simulated 189-record archive Supplementary Data and Code.zip. No invented video, human rating, consensus, or clinical total is included.

15 supplied entries map to 14 unique IDs. Entry 13 duplicates entry 12. Entry 10 has official metadata but inaccessible content and remains in the denominator for access reporting. Canonical links remove share/tracking query parameters. This was an author-supplied convenience set, not a systematic search; no query/rank/locale history has been reconstructed.

E = affirmative content related to the named domain identified in the reviewed evidence. E may be a brief explanation, incomplete demonstration or discussion of a disputed claim; it does not mean correct, complete or safe.
U = not established in the reviewed evidence. U is unresolved, not absent and not a zero score.
X = content unavailable. X is missing, not not-applicable and not a zero score.
Evidence flags MUST NOT be mapped to clinical scores 0, 1 or 2. The clinical_score column is intentionally empty. In particular, do not convert a count of E flags to a 0–20 completeness total or classify it with the 12/18 thresholds.

Methods: YouTube official automatic English transcripts with selected frames/storyboards; TikTok one-second frame samples with on-screen text; Bilibili ten-second samples, targeted frames, on-screen Chinese text and contextual review of faster-whisper base multilingual int8 machine transcripts. Machine transcriptions are not certified and some speech terms are inaccurate. No accepted procedural speech evidence was obtained from the four TikTok ASR files. No continuous human audiovisual review or paired clinician ratings occurred. Model-generated annotations require author and clinical review.

Clinical rating template: clinical_rating_template_NOT_OBSERVED.csv is EMPTY. Its R1/R2 rows are slots for future human assessors, not existing observations. A full review, documented expertise/calibration and separate original judgments are required before it can be analyzed. Reconcile disagreements in a new file without overwriting original ratings. Apply instrument-specific rules if adding generic instruments. No generic-instrument clinical scores have been assigned here.

Reproduce the limited pilot audit with Python 3.10 or later (standard library only):
    python code/pilot_analysis.py
Run from any working directory. Outputs are written to outputs/. The script validates IDs, duplicate links, the 14 x 10 evidence grid, evidence provenance, missingness and denominator accounting. It does not scrape sites, generate scores, modify the simulated archive, compute human agreement or run clinical regression/AUC. If actual clinical item scores are entered later, a total is only produced when all ten are present; the future human-rating template requires a separate reviewed analysis entry point.

Files: records/video_intake.csv (15 rows), video_metadata.csv (14 rows), domain_evidence.csv (140 rows), clinical_rating_template_NOT_OBSERVED.csv (28 empty rater slots); provenance/access_and_evidence_log.json; code/pilot_analysis.py; outputs/pilot_summary.json and two summary CSVs.

No third-party video, full transcript or creator image is redistributed in this package. Evidence summaries are concise paraphrases with time references. The public links may change or become unavailable; the annotated evidence is an access-date snapshot. The original downloaded media, frame samples and unverified transcripts remain private working materials and are not publication attachments.

Public repository: NOT YET CREATED. Authors must deposit the original simulation archive, this package and the Vector_Figures folder and supply an actual public release URL/DOI. A local ZIP is not a public repository. This package is a review draft; authors remain responsible for checking evidence and completing clinical evaluation.
