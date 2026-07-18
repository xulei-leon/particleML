# FR-<identifier> <title>

- `FR-ID`: `FR-<identifier>`
- `Title`: <functional requirement title>
- `Stage`: <stage identifier or planning status>
- `Implementation order`: <number or pending>
- `Priority`: <P0/P1/P2/P3>
- `Dependencies`: <none or `FR-xxx`, `FR-yyy`>
- `Affected components`: <packages, modules, schemas, or runtime boundaries>
- `Prototype-stage requirement`: <yes/no>
- `Source type`: <SRS baseline/design decomposition/new backlog/defect fix/other>
- `Original SRS section`: <section identifier or none>

## Goal

<State the scientific or engineering outcome this requirement must achieve.>

## Requirement Description

<Describe the user or research scenario, required system behavior, capability
boundary, motivation, and relationship to the active particleML workflow.>

## High-Level Requirements

- <requirement 1>
- <requirement 2>
- <requirement 3>

## Inputs

- <input data, configuration, state, or upstream artifact 1>
- <input data, configuration, state, or upstream artifact 2>

## Outputs

- <output data, state, file, or downstream artifact 1>
- <output data, state, file, or downstream artifact 2>

## Implementation Constraints

- <Define component boundaries, schema ownership, and dependency direction.>
- <Identify the authoritative configuration and prohibit implicit defaults.>
- <Define runtime-data, provenance, and artifact-retention rules.>
- <State the qualified environment if local execution is insufficient.>

## Failure and Degradation

- <failure condition or exceptional scenario 1>
- <failure condition or exceptional scenario 2>
- <fail-closed, retry, manual-review, or terminal-failure rule>

## Acceptance Points

- <verifiable acceptance point 1>
- <verifiable acceptance point 2>
- <verifiable acceptance point 3>

## Minimum Verification

- <Add or update the relevant unit, contract, integration, or regression tests.>
- <List the critical positive and negative scenarios.>
- <List required local, CI, CMSSW, or RunPod checks without overstating evidence.>

## Out of Scope

- <explicit exclusion 1>
- <explicit exclusion 2>

## Notes

- <relationships, future extensions, unresolved decisions, or amendment rules>
