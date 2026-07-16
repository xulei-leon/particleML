# FR-DATA-002 CMS Extraction

- `FR-ID`: `FR-DATA-002`
- `Title`: CMS extraction
- `Phase`: Phase 3 - CMSSW Extractor and E0
- `Development Order`: 10
- `Priority`: P0
- `Prerequisites`: `FR-DATA-001`, `FR-DATA-003`, `FR-DATA-006`, `FR-REP-001`
- `Affected Packages`: `cmssw/ParticleMLExtractor/`, `configs/`, CMSSW integration tests
- `Prototype Phase`: Yes
- `Source Type`: SRS baseline
- `Original SRS Section`: Software Requirements Specification §4, FR-DATA-002

## Goal

Produce compact, provenance-complete ROOT artifacts from the frozen CMS 2015 MiniAOD simulation without coupling legacy CMSSW code to the modern ML stack.

## Requirement Description

The pinned CMSSW extractor shall read frozen source files, apply the approved corrected-AK8 selection, resolve packed daughters, assign leakage-safe labels, and write raw A-D constituent fields, identities, cutflow, and provenance.

## High-Level Requirements

- Run in CMSSW 7.6.7 with the approved container and global tag.
- Store source identity, split bucket, event/jet identity, corrected kinematics, label, vertex diagnostics, raw constituents, track state, truth audit fields, and cutflow.
- Sort constituents later in the conversion boundary; retain sufficient original daughter identity for deterministic tie-breaking.
- Keep HDF5 normalization, view construction, models, and statistics outside CMSSW.
- Qualify the extraction host with one TT and one QCD file before the E0 batch.

## Inputs

- Frozen source manifest and exact PFNs.
- Versioned extraction configuration and research-plan selection policy.
- CMS MiniAODSIM files accessed directly through filesystem or HTTP/HTTPS-compatible data paths.

## Outputs

- One compact flat ROOT artifact per extraction job.
- Job metadata with container digest, Git commit, source hash, cutflow, timing, and structured failures.

## Implementation Constraints

- Production extraction runs only on a qualified POSIX host with measured EOS/XRootD performance.
- Do not introduce an intermediate web service or mirror the multi-terabyte corpus locally.
- Truth and pileup audit fields must never enter model tensors.

## Failure and Degradation

- Missing products, unresolved daughters, invalid PV access, non-finite values, or provenance mismatches fail the file with `EXTRACT_*` errors.
- Quarantine failed files and retain structured evidence; do not silently skip required record coverage.

## Acceptance Criteria

- A qualified-host fixture job writes the required tree and metadata with stable identities.
- At least 5-10 TT files and multiple files from every candidate QCD record are processed for E0.
- Product checks, throughput, CPU/event, wall time, failure rate, and compact size are retained.
- The extractor output is accepted by the cloud conversion pipeline without CMSSW dependencies.

## Minimum Verification

- CMSSW configuration and hand-inspected fixture jobs on the qualified extraction host.
- Product, daughter-resolution, output-layout, cutflow, and structured-failure checks.
- Retain tested commit, container digest, logs, and output hashes as evidence.

## Out of Scope

- Canonical HDF5 conversion or normalization.
- Model training, metrics, and report generation.

## Notes

- Source contracts: architecture §5.1 and implementation specification §3.1.
- Evidence target: E0 compact ROOT and extraction report.
