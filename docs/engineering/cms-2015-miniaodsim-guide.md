# CMS 2015 MINIAODSIM Beginner Usage Guide

## 1. Purpose

This guide explains how to access and use the CMS 2015 MINIAODSIM samples selected for the ParticleML top-tagging study. It is written for readers who have not previously worked with CMS Open Data.

By the end of the guide, you will be able to:

1. understand what the dataset contains;
2. obtain an official list of source files;
3. stream a file or download one file for a local test;
4. inspect a MiniAOD file in the correct CMS software environment;
5. understand how the project converts CMS events into model-ready HDF5 data.

This guide is based on the [CMS 2015 MINIAODSIM feasibility analysis](../research/assessments/cms-2015-miniaodsim-feasibility.md). The analysis reached a **conditional-go** decision: the required information exists, but the project-specific CMSSW extraction pilot has not yet passed the E0 validation gates.

## 2. What This Dataset Is

The source data are simulated proton-proton collision events recorded in CMS **MiniAOD** format. The files use ROOT as their storage container, but the event content consists of CMS-specific C++ objects. They are not ordinary flat ROOT tables and are not ready to be passed directly to a neural network.

The hierarchy relevant to this project is:

```text
dataset record
  -> ROOT source files
     -> collision events
        -> reconstructed AK8 jets
           -> particle-flow constituents
              -> kinematics, charge, particle identity, and track information
```

The machine-learning task is binary boosted-top tagging:

- **Signal:** a reconstructed AK8 jet from the TT sample, matched to a fully hadronic generator-level top-quark decay.
- **Background:** a reconstructed AK8 jet from one of the QCD samples.

An event is one simulated collision. A jet is a collimated spray of particles reconstructed inside an event. A jet constituent is one reconstructed particle-flow candidate assigned to that jet.

## 3. Selected CMS Records

The study freezes the following records:

| Role | Record | Sample | Files | Size | DOI |
|---|---:|---|---:|---:|---|
| Signal source | 19980 | Inclusive TT, ext3 | 2,413 | 3.051 TiB | [10.7483/OPENDATA.CMS.JJEM.1DKC](https://doi.org/10.7483/OPENDATA.CMS.JJEM.1DKC) |
| Background | 18373 | QCD, generated pT 470-600 GeV | 89 | 0.121 TiB | [10.7483/OPENDATA.CMS.5DBS.XCW8](https://doi.org/10.7483/OPENDATA.CMS.5DBS.XCW8) |
| Background | 18376 | QCD, generated pT 600-800 GeV | 91 | 0.126 TiB | [10.7483/OPENDATA.CMS.3Y72.BWW4](https://doi.org/10.7483/OPENDATA.CMS.3Y72.BWW4) |
| Background | 18377 | QCD, generated pT 800-1,000 GeV | 98 | 0.130 TiB | [10.7483/OPENDATA.CMS.SGRV.4ABD](https://doi.org/10.7483/OPENDATA.CMS.SGRV.4ABD) |
| Background diagnostic | 18355 | QCD, generated pT 1,000-1,400 GeV | 89 | 0.100 TiB | [10.7483/OPENDATA.CMS.WOP0.TFY9](https://doi.org/10.7483/OPENDATA.CMS.WOP0.TFY9) |
| Background diagnostic | 18358 | QCD, generated pT 1,400-1,800 GeV | 9 | 0.014 TiB | [10.7483/OPENDATA.CMS.N49K.1FTR](https://doi.org/10.7483/OPENDATA.CMS.N49K.1FTR) |

Together, the records contain 2,789 files, about 113 million events, and 3.542 TiB of source data.

> Do not download the complete corpus to a personal computer. Start with one file. Production extraction should stream files on CERN-adjacent or other high-throughput compute infrastructure.

The QCD pT ranges describe the generator-level production samples. They are not reconstructed-jet pT bins.

## 4. Required Software

For a first exercise, install:

- Git;
- Python 3;
- Docker Desktop with the Linux container engine enabled;
- at least 10 GB for the CMSSW image, plus about 2 GB if one source file will be downloaded.

The production environment fixed by the CMS records is:

```text
CMSSW release: CMSSW_7_6_7
Container: cmsopendata/cmssw_7_6_7-slc6_amd64_gcc493
Global tag: 76X_mcRun2_asymptotic_RunIIFall15DR76_v1
```

Run the following commands from the project root. In PowerShell:

```powershell
docker --version
docker info
New-Item -ItemType Directory -Force data\cms2015\raw, data\cms2015\output
```

`docker info` must show a working Linux engine. Creating the two directories does not download any CMS data.

## 5. Obtain the Official File List

Each CERN Open Data record exposes metadata through an API. The following Python standard-library script writes a tab-separated manifest for one record. Save it as `list_cms_record.py` outside the repository or paste it into a Python session.

```python
import csv
import json
import sys
import urllib.request

record_id = int(sys.argv[1])
url = f"https://opendata.cern.ch/api/records/{record_id}"

with urllib.request.urlopen(url) as response:
    record = json.load(response)

files = [
    item
    for index in record["metadata"]["_file_indices"]
    for item in index["files"]
]

with open(f"record-{record_id}.tsv", "w", newline="", encoding="utf-8") as output:
    writer = csv.writer(output, delimiter="\t", lineterminator="\n")
    writer.writerow(["record_id", "pfn", "adler32", "size_bytes"])
    for item in sorted(files, key=lambda value: value["uri"]):
        writer.writerow([
            record_id,
            item["uri"],
            item["checksum"].removeprefix("adler32:"),
            item["size"],
        ])

print(f"Wrote {len(files)} files for record {record_id}")
```

Run it for a small QCD record first:

```powershell
python list_cms_record.py 18358
Get-Content record-18358.tsv -TotalCount 3
```

Run it for all frozen records when preparing the persistent project manifest:

```powershell
19980, 18373, 18376, 18377, 18355, 18358 | ForEach-Object {
    python list_cms_record.py $_
}
```

Every manifest row contains:

- `record_id`: the CERN Open Data record;
- `pfn`: the canonical XRootD file address;
- `adler32`: the checksum published by CERN;
- `size_bytes`: the expected file size.

Keep the exact PFN. The project assigns train, validation, and test splits by hashing this exact string.

The generated files are convenient, header-bearing working tables. For the formal reproducibility artifact, combine only their data rows, sort the complete set, omit the header, use exactly `record_id<TAB>pfn<TAB>adler32<TAB>size_bytes<LF>`, and record its SHA-256. This distinction matters because even a header or different line ending changes the hash.

## 6. Stream or Download One File

### 6.1 Recommended: stream the file

CMSSW and XRootD can read a PFN directly without storing the complete file locally:

```text
root://eospublic.cern.ch//eos/opendata/cms/...
```

Streaming is the normal production approach. It avoids copying terabytes of source data, but it still requires a reliable, high-throughput network path.

### 6.2 Optional: download one file for a local exercise

Start the CMS 2015 container from PowerShell:

```powershell
docker run -it --name particleml-cms2015 `
  -v "${PWD}:/work" `
  cmsopendata/cmssw_7_6_7-slc6_amd64_gcc493 /bin/bash
```

The image initializes `CMSSW_7_6_7` automatically. Inside the container, confirm the environment:

```bash
echo "$CMSSW_VERSION"
which cmsRun
```

Copy the first PFN from a manifest and download it with checksum verification:

```bash
xrdcp --cksum adler32 \
  'root://eospublic.cern.ch//eos/opendata/cms/...' \
  /work/data/cms2015/raw/sample.root
```

Then compare the downloaded checksum with the `adler32` field in the manifest:

```bash
xrdadler32 /work/data/cms2015/raw/sample.root
```

Do not continue if the checksum or file size differs from the manifest.

To leave and later reopen the same container:

```bash
exit
```

```powershell
docker start -i particleml-cms2015
```

## 7. Inspect the MiniAOD File

### 7.1 Check that the file opens

Inside the CMSSW container:

```bash
edmFileUtil /work/data/cms2015/raw/sample.root
```

To inspect the stored CMS products:

```bash
edmDumpEventContent /work/data/cms2015/raw/sample.root | grep -E \
  'slimmedJetsAK8|packedPFCandidates|prunedGenParticles|slimmedGenJetsAK8|offlineSlimmedPrimaryVertices'
```

The project requires these products:

| CMS product | Meaning | Project use |
|---|---|---|
| `slimmedJetsAK8` | Reconstructed anti-kT, R=0.8 jets | Jet selection and jet axis |
| `packedPFCandidates` | Reconstructed particle-flow candidates | Jet constituents and A-D features |
| `prunedGenParticles` | Generator particles | Hadronic-top signal truth matching |
| `slimmedGenJetsAK8` | Generator-level AK8 jets | Pilot diagnostic |
| `offlineSlimmedPrimaryVertices` | Reconstructed primary vertices | Longitudinal impact-parameter reference |

If a file does not contain the required products, record the PFN and stop processing that file.

### 7.2 Optional metadata inspection with Uproot

Uproot is useful for checking ROOT keys and branch names without compiling a CMSSW analyzer:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install uproot
```

```python
import uproot

path = "data/cms2015/raw/sample.root"
with uproot.open(path) as source:
    events = source["Events"]
    print("events:", events.num_entries)
    for name in events.keys():
        if any(term in name for term in ("slimmedJetsAK8", "packedPFCandidates")):
            print(name)
```

This is an inspection step only. Do not use raw packed members as final physical impact-parameter values. CMSSW must decode `dxy`, `dz`, their uncertainties, and jet-daughter references.

## 8. Run a Standard CMS Beginner Example

The official Physics Object Extractor Tool (POET) is a useful first end-to-end exercise for learning how MiniAOD is processed. It does not implement the ParticleML AK8 constituent and top-truth extraction.

Inside the CMSSW container:

```bash
cd /code/CMSSW_7_6_7/src
git clone https://github.com/cms-opendata-analyses/PhysObjectExtractorTool.git
cd PhysObjectExtractorTool
git checkout 2015MiniAOD
scram b
cd PhysObjectExtractor
cmsRun python/poet_cfg.py
```

The example processes 1,000 simulated MiniAOD events and writes a smaller ROOT file. Successful completion demonstrates the basic workflow:

```text
MiniAOD input -> cmsRun -> EDAnalyzer -> flat ROOT output
```

For this project, POET is a learning exercise, not the production extractor.

## 9. Project-Specific Extraction

The project requires one CMSSW EDAnalyzer that performs the following operations for every source file:

1. read `slimmedJetsAK8`;
2. keep jets with `500 <= pT < 1000 GeV` and `abs(eta) < 2.0`;
3. resolve each jet's packed particle-flow daughters;
4. sort constituents by descending pT and retain at most 150;
5. decode the complete A-D feature set;
6. assign TT signal labels using last-copy, fully hadronic top matching and daughter containment;
7. use only QCD records for background labels;
8. write a compact flat ROOT file with features, labels, masks, identifiers, and provenance.

The feature views are nested:

| View | Constituent features |
|---|---|
| A | `delta_eta`, wrapped `delta_phi`, `log_pt`, `log_energy` |
| B | A plus `charge` |
| C | B plus charge-independent `pid_type` |
| D | C plus decoded `dxy`, `dxyError`, `dz(0)`, and `dzError` |

PID must map `abs(pdgId)` to charged hadron, neutral hadron, photon, electron, muon, or unknown. Neutral candidates and candidates without usable track details receive zero in D fields, while missingness is counted separately.

The project-specific analyzer does not yet exist in this repository. Therefore, the commands in Sections 5-8 are executable now, while the complete A-D extraction remains an implementation and E0-validation task.

## 10. File-Level Data Splits

Split source files before extracting jets. Use the exact UTF-8 PFN from the sorted manifest:

```python
import hashlib

def split_for_pfn(pfn: str) -> str:
    bucket = int(hashlib.sha256(pfn.encode("utf-8")).hexdigest(), 16) % 10
    if bucket == 0:
        return "test"
    if bucket == 1:
        return "validation"
    return "training"

assert split_for_pfn("root://example/file.root") in {
    "training", "validation", "test"
}
```

This keeps all jets from one event and source file in the same split. Do not remove the protocol, lowercase the PFN, or otherwise normalize it before hashing.

## 11. Convert the Flat ROOT Output to HDF5

After the CMSSW pilot is validated, a separate modern Python environment converts the compact ROOT output into one HDF5 dataset with the full D schema. A-D views are sliced from this one tensor so every experiment uses identical jets, ordering, masks, and splits.

The intended OmniLearned-compatible structure is:

| HDF5 entry | Content |
|---|---|
| `data` | Particle tensor with the full D feature schema |
| `pid` | Jet label: top or QCD |
| `global` | Optional jet-level audit variables; not a primary classifier input |

Read a produced file with:

```python
import h5py

with h5py.File("cms2015_jets.h5", "r") as source:
    print(list(source.keys()))
    print("data:", source["data"].shape, source["data"].dtype)
    print("pid:", source["pid"].shape, source["pid"].dtype)
    if "global" in source:
        print("global:", source["global"].shape)

    first_jet = source["data"][0]
    first_label = source["pid"][0]
    print("first jet:", first_jet.shape)
    print("first label:", first_label)
```

Before training, verify:

- tensor shapes and feature order;
- mask and padding behavior;
- absence of NaN and infinity;
- at most 150 retained constituents;
- label counts by class and split;
- no file or event overlap across splits;
- no truth, record, process, or file identifiers in model inputs.

Fit normalization, optional pT/eta reweighting, PID vocabulary, and impact-parameter transforms on the training split only, then freeze them for validation and test data.

## 12. Recommended First Session

For a first successful session, use this order:

1. generate `record-18358.tsv` and inspect its first rows;
2. start the CMS 2015 Docker container;
3. stream one PFN with `edmFileUtil`, or download one file with `xrdcp`;
4. verify its checksum if downloaded;
5. confirm the five required CMS products with `edmDumpEventContent`;
6. run the 1,000-event POET example;
7. stop before bulk downloading or treating raw packed branches as model features.

Completing these steps means that data discovery, access, integrity checking, CMSSW startup, MiniAOD inspection, and a standard extraction example all work on your machine.

## 13. Common Problems

| Problem | Likely cause | Action |
|---|---|---|
| `docker info` cannot reach the daemon | Docker Desktop or its Linux engine is not running | Start Docker Desktop and select Linux containers |
| `xrdcp` is very slow or times out | Poor route to CERN EOS | Stream only one test file locally; move production near CERN or to a measured high-throughput host |
| `edmDumpEventContent` is unavailable | Command is running outside the CMSSW container | Re-enter with `docker start -i particleml-cms2015` |
| Checksum differs | Incomplete or corrupted transfer | Delete only that local copy and repeat the transfer |
| Uproot shows packed members but values look unusual | PackedCandidate values use CMS compression and references | Decode them through CMSSW accessors |
| Too few selected TT jets | Inclusive TT has low boosted-top yield | Run the required 5-10-file yield pilot before choosing the training scale |
| A QCD record has few selected jets | Generator-level and reconstructed pT are different | Plot selected reconstructed AK8 pT by record before excluding bins |

## 14. Scientific Rules That Must Not Be Skipped

- Do not use unmatched TT jets as QCD background.
- Do not use generator truth, record ID, process ID, file ID, or class-derived values as model inputs.
- Do not apply a top-mass or Soft-Drop mass window to the primary sample.
- Do not silently lower the 500 GeV jet-pT threshold to increase yield.
- Do not fit preprocessing or reweighting parameters on validation or test data.
- Do not claim the final dataset is validated until the E0 pilot checks daughter references, decoded impact parameters, truth labels, missingness, yield, split integrity, leakage, and output schema.

## 15. Further Reading

- [Project feasibility analysis](../research/assessments/cms-2015-miniaodsim-feasibility.md)
- [CMS guide: running analysis code with Docker](https://opendata.cern.ch/docs/cms-guide-docker)
- [CMS guide: getting started with MiniAOD](https://opendata.cern.ch/docs/cms-getting-started-miniaod)
- [CMS 2015 Physics Object Extractor Tool](https://github.com/cms-opendata-analyses/PhysObjectExtractorTool/tree/2015MiniAOD)
- [CMSSW 7.6 PackedCandidate interface](https://github.com/cms-sw/cmssw/blob/CMSSW_7_6_X/DataFormats/PatCandidates/interface/PackedCandidate.h)
- [OmniLearned custom-data format](https://github.com/ViniciusMikuni/OmniLearned/blob/5091595d226b6021e967ab2ecfff832f40c026f6/README.md#creating-your-own-dataset)
