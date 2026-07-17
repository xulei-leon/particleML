"""Pinned CMSSW 7.6.7 configuration for the particleML compact extractor."""

from __future__ import print_function

import FWCore.ParameterSet.Config as cms
from FWCore.ParameterSet.VarParsing import VarParsing

CONTAINER_IMAGE = "cmsopendata/cmssw_7_6_7-slc6_amd64_gcc493"
GLOBAL_TAG = "76X_mcRun2_asymptotic_RunIIFall15DR76_v1"
UNRESOLVED = "UNRESOLVED"

options = VarParsing("analysis")
options.register("recordId", 0, VarParsing.multiplicity.singleton, VarParsing.varType.int, "CMS record ID")
options.register("canonicalPFN", UNRESOLVED, VarParsing.multiplicity.singleton, VarParsing.varType.string, "Exact manifest PFN")
options.register("split", UNRESOLVED, VarParsing.multiplicity.singleton, VarParsing.varType.string, "Frozen PFN split")
options.register("sourceManifestSha256", UNRESOLVED, VarParsing.multiplicity.singleton, VarParsing.varType.string, "Exact manifest digest")
options.register("gitCommit", UNRESOLVED, VarParsing.multiplicity.singleton, VarParsing.varType.string, "Tested Git commit")
options.register("containerDigest", UNRESOLVED, VarParsing.multiplicity.singleton, VarParsing.varType.string, "Resolved container digest")
options.register("isSignal", False, VarParsing.multiplicity.singleton, VarParsing.varType.bool, "TT signal record")
options.parseArguments()

required = {
    "recordId": options.recordId,
    "canonicalPFN": options.canonicalPFN,
    "split": options.split,
    "sourceManifestSha256": options.sourceManifestSha256,
    "gitCommit": options.gitCommit,
    "containerDigest": options.containerDigest,
}
if options.recordId <= 0 or any(value == UNRESOLVED for value in required.values() if isinstance(value, str)):
    raise RuntimeError("EXTRACT_CONFIGURATION: every provenance option must be resolved")
if options.split not in ("train", "validation", "test"):
    raise RuntimeError("EXTRACT_CONFIGURATION: split must use the frozen vocabulary")

process = cms.Process("PARTICLEML")
process.load("Configuration.StandardSequences.Services_cff")
process.load("Configuration.StandardSequences.GeometryRecoDB_cff")
process.load("Configuration.StandardSequences.MagneticField_cff")
process.load("Configuration.StandardSequences.FrontierConditions_GlobalTag_condDBv2_cff")
from Configuration.AlCa.GlobalTag import GlobalTag

process.GlobalTag = GlobalTag(process.GlobalTag, GLOBAL_TAG, "")
process.maxEvents = cms.untracked.PSet(input=cms.untracked.int32(options.maxEvents))
process.source = cms.Source(
    "PoolSource",
    fileNames=cms.untracked.vstring(options.inputFiles),
    skipBadFiles=cms.untracked.bool(False),
)
process.TFileService = cms.Service("TFileService", fileName=cms.string(options.outputFile))

process.extractor = cms.EDAnalyzer(
    "ParticleMLExtractor",
    jets=cms.InputTag("slimmedJetsAK8"),
    packedCandidates=cms.InputTag("packedPFCandidates"),
    genParticles=cms.InputTag("prunedGenParticles"),
    primaryVertices=cms.InputTag("offlineSlimmedPrimaryVertices"),
    recordId=cms.uint32(options.recordId),
    canonicalPFN=cms.string(options.canonicalPFN),
    split=cms.string(options.split),
    sourceManifestSha256=cms.string(options.sourceManifestSha256),
    gitCommit=cms.string(options.gitCommit),
    containerImage=cms.string(CONTAINER_IMAGE),
    containerDigest=cms.string(options.containerDigest),
    globalTag=cms.string(GLOBAL_TAG),
    isSignal=cms.bool(options.isSignal),
    qcdRecordIds=cms.vuint32(18355, 18358, 18373, 18376, 18377),
)
process.path = cms.Path(process.extractor)
