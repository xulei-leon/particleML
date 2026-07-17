// Compact CMS MiniAODSIM extraction boundary for particleML.

#include <algorithm>
#include <cmath>
#include <cstdint>
#include <set>
#include <string>
#include <vector>

#include "CommonTools/UtilAlgos/interface/TFileService.h"
#include "DataFormats/HepMCCandidate/interface/GenParticle.h"
#include "DataFormats/Math/interface/deltaR.h"
#include "DataFormats/PatCandidates/interface/Jet.h"
#include "DataFormats/PatCandidates/interface/PackedCandidate.h"
#include "DataFormats/VertexReco/interface/Vertex.h"
#include "FWCore/Framework/interface/EDAnalyzer.h"
#include "FWCore/Framework/interface/Event.h"
#include "FWCore/Framework/interface/EventSetup.h"
#include "FWCore/Framework/interface/MakerMacros.h"
#include "FWCore/MessageLogger/interface/MessageLogger.h"
#include "FWCore/ParameterSet/interface/ParameterSet.h"
#include "FWCore/ServiceRegistry/interface/Service.h"
#include "FWCore/Utilities/interface/Exception.h"
#include "TH1D.h"
#include "TTree.h"

namespace {

const reco::Candidate* finalCopy(const reco::Candidate* particle) {
  const reco::Candidate* current = particle;
  bool advanced = true;
  while (advanced) {
    advanced = false;
    for (size_t index = 0; index < current->numberOfDaughters(); ++index) {
      const reco::Candidate* daughter = current->daughter(index);
      if (daughter != 0 && daughter->pdgId() == current->pdgId()) {
        current = daughter;
        advanced = true;
        break;
      }
    }
  }
  return current;
}

bool hadronicTopDaughters(const reco::GenParticle& top,
                         std::vector<const reco::Candidate*>& daughters) {
  const reco::Candidate* terminalTop = finalCopy(&top);
  const reco::Candidate* bottom = 0;
  const reco::Candidate* wBoson = 0;
  for (size_t index = 0; index < terminalTop->numberOfDaughters(); ++index) {
    const reco::Candidate* daughter = terminalTop->daughter(index);
    if (daughter == 0) continue;
    if (std::abs(daughter->pdgId()) == 5) bottom = finalCopy(daughter);
    if (std::abs(daughter->pdgId()) == 24) wBoson = finalCopy(daughter);
  }
  if (bottom == 0 || wBoson == 0) return false;
  std::vector<const reco::Candidate*> quarks;
  for (size_t index = 0; index < wBoson->numberOfDaughters(); ++index) {
    const reco::Candidate* daughter = wBoson->daughter(index);
    if (daughter != 0 && std::abs(daughter->pdgId()) >= 1 &&
        std::abs(daughter->pdgId()) <= 5) {
      quarks.push_back(finalCopy(daughter));
    }
  }
  if (quarks.size() != 2) return false;
  daughters.clear();
  daughters.push_back(bottom);
  daughters.push_back(quarks[0]);
  daughters.push_back(quarks[1]);
  return true;
}

void requireFinite(double value, const char* field) {
  if (!std::isfinite(value)) {
    throw cms::Exception("EXTRACT_NONFINITE") << field << " is not finite";
  }
}

}  // namespace

class ParticleMLExtractor : public edm::EDAnalyzer {
 public:
  explicit ParticleMLExtractor(const edm::ParameterSet& configuration);
  ~ParticleMLExtractor() override {}

  void analyze(const edm::Event& event, const edm::EventSetup&) override;
  void endJob() override;

 private:
  int matchSignal(const pat::Jet&, const reco::GenParticleCollection&) const;
  void resetParticles();

  edm::EDGetTokenT<pat::JetCollection> jetsToken_;
  edm::EDGetTokenT<pat::PackedCandidateCollection> packedCandidatesToken_;
  edm::EDGetTokenT<reco::GenParticleCollection> genParticlesToken_;
  edm::EDGetTokenT<reco::VertexCollection> primaryVerticesToken_;

  uint32_t recordId_;
  std::string canonicalPFN_;
  std::string split_;
  std::string sourceManifestSha256_;
  std::string gitCommit_;
  std::string containerImage_;
  std::string containerDigest_;
  std::string globalTag_;
  bool isSignal_;
  std::set<uint32_t> qcdRecordIds_;

  TTree* jetsTree_;
  TTree* metadataTree_;
  TH1D* cutflow_;
  uint64_t processedEvents_;
  uint64_t retainedJets_;

  uint32_t run_;
  uint32_t lumi_;
  uint64_t event_;
  int32_t jetIndex_;
  int8_t target_;
  float jetPt_;
  float jetEta_;
  float jetPhi_;
  float pvZ_;
  int32_t nVertices_;
  int32_t truthMatchCount_;

  std::vector<float> particlePt_;
  std::vector<float> particleEta_;
  std::vector<float> particlePhi_;
  std::vector<float> particleEnergy_;
  std::vector<float> particleCharge_;
  std::vector<int32_t> particlePdgId_;
  std::vector<float> particleDxy_;
  std::vector<float> particleDxyError_;
  std::vector<float> particleDz_;
  std::vector<float> particleDzError_;
  std::vector<uint8_t> particleHasTrackDetails_;
  std::vector<uint32_t> original_daughter_index;
};

ParticleMLExtractor::ParticleMLExtractor(const edm::ParameterSet& configuration)
    : jetsToken_(consumes<pat::JetCollection>(configuration.getParameter<edm::InputTag>("jets"))),
      packedCandidatesToken_(consumes<pat::PackedCandidateCollection>(
          configuration.getParameter<edm::InputTag>("packedCandidates"))),
      genParticlesToken_(consumes<reco::GenParticleCollection>(
          configuration.getParameter<edm::InputTag>("genParticles"))),
      primaryVerticesToken_(consumes<reco::VertexCollection>(
          configuration.getParameter<edm::InputTag>("primaryVertices"))),
      recordId_(configuration.getParameter<uint32_t>("recordId")),
      canonicalPFN_(configuration.getParameter<std::string>("canonicalPFN")),
      split_(configuration.getParameter<std::string>("split")),
      sourceManifestSha256_(configuration.getParameter<std::string>("sourceManifestSha256")),
      gitCommit_(configuration.getParameter<std::string>("gitCommit")),
      containerImage_(configuration.getParameter<std::string>("containerImage")),
      containerDigest_(configuration.getParameter<std::string>("containerDigest")),
      globalTag_(configuration.getParameter<std::string>("globalTag")),
      isSignal_(configuration.getParameter<bool>("isSignal")),
      processedEvents_(0),
      retainedJets_(0) {
  const std::vector<uint32_t> qcd = configuration.getParameter<std::vector<uint32_t> >("qcdRecordIds");
  qcdRecordIds_.insert(qcd.begin(), qcd.end());
  if (!isSignal_ && qcdRecordIds_.count(recordId_) == 0) {
    throw cms::Exception("EXTRACT_CONFIGURATION")
        << "background record is absent from qcdRecordIds: " << recordId_;
  }

  edm::Service<TFileService> files;
  jetsTree_ = files->make<TTree>("jets", "particleML compact jets");
  metadataTree_ = files->make<TTree>("metadata", "particleML job metadata");
  cutflow_ = files->make<TH1D>("cutflow", "cutflow", 8, 0.0, 8.0);
  const char* labels[] = {"events", "jets", "kinematic", "truth", "daughters", "finite", "retained", "failed"};
  for (int index = 0; index < 8; ++index) cutflow_->GetXaxis()->SetBinLabel(index + 1, labels[index]);

  jetsTree_->Branch("record_id", &recordId_);
  jetsTree_->Branch("canonical_pfn", &canonicalPFN_);
  jetsTree_->Branch("run", &run_);
  jetsTree_->Branch("lumi", &lumi_);
  jetsTree_->Branch("event", &event_);
  jetsTree_->Branch("jet_index", &jetIndex_);
  jetsTree_->Branch("split", &split_);
  jetsTree_->Branch("target", &target_);
  jetsTree_->Branch("jet_pt", &jetPt_);
  jetsTree_->Branch("jet_eta", &jetEta_);
  jetsTree_->Branch("jet_phi", &jetPhi_);
  jetsTree_->Branch("pv_z", &pvZ_);
  jetsTree_->Branch("n_vertices", &nVertices_);
  jetsTree_->Branch("truth_match_count", &truthMatchCount_);
  jetsTree_->Branch("particle_pt", &particlePt_);
  jetsTree_->Branch("particle_eta", &particleEta_);
  jetsTree_->Branch("particle_phi", &particlePhi_);
  jetsTree_->Branch("particle_energy", &particleEnergy_);
  jetsTree_->Branch("particle_charge", &particleCharge_);
  jetsTree_->Branch("particle_pdg_id", &particlePdgId_);
  jetsTree_->Branch("particle_dxy", &particleDxy_);
  jetsTree_->Branch("particle_dxy_error", &particleDxyError_);
  jetsTree_->Branch("particle_dz", &particleDz_);
  jetsTree_->Branch("particle_dz_error", &particleDzError_);
  jetsTree_->Branch("particle_has_track_details", &particleHasTrackDetails_);
  jetsTree_->Branch("original_daughter_index", &original_daughter_index);

  metadataTree_->Branch("record_id", &recordId_);
  metadataTree_->Branch("canonical_pfn", &canonicalPFN_);
  metadataTree_->Branch("source_manifest_sha256", &sourceManifestSha256_);
  metadataTree_->Branch("git_commit", &gitCommit_);
  metadataTree_->Branch("container_image", &containerImage_);
  metadataTree_->Branch("container_digest", &containerDigest_);
  metadataTree_->Branch("global_tag", &globalTag_);
  metadataTree_->Branch("processed_events", &processedEvents_);
  metadataTree_->Branch("retained_jets", &retainedJets_);
}

void ParticleMLExtractor::resetParticles() {
  particlePt_.clear();
  particleEta_.clear();
  particlePhi_.clear();
  particleEnergy_.clear();
  particleCharge_.clear();
  particlePdgId_.clear();
  particleDxy_.clear();
  particleDxyError_.clear();
  particleDz_.clear();
  particleDzError_.clear();
  particleHasTrackDetails_.clear();
  original_daughter_index.clear();
}

int ParticleMLExtractor::matchSignal(const pat::Jet& jet,
                                     const reco::GenParticleCollection& particles) const {
  int matches = 0;
  for (reco::GenParticleCollection::const_iterator top = particles.begin(); top != particles.end(); ++top) {
    if (std::abs(top->pdgId()) != 6 || !top->statusFlags().isLastCopy()) continue;
    if (reco::deltaR(jet, *top) >= 0.8) continue;
    std::vector<const reco::Candidate*> daughters;
    if (!hadronicTopDaughters(*top, daughters)) continue;
    bool contained = true;
    for (std::vector<const reco::Candidate*>::const_iterator daughter = daughters.begin();
         daughter != daughters.end(); ++daughter) {
      if (reco::deltaR(jet, **daughter) >= 0.8) contained = false;
    }
    if (contained) ++matches;
  }
  if (matches > 1) {
    throw cms::Exception("EXTRACT_AMBIGUOUS_TRUTH")
        << "more than one eligible hadronic top matches one AK8 jet";
  }
  return matches;
}

void ParticleMLExtractor::analyze(const edm::Event& event, const edm::EventSetup&) {
  ++processedEvents_;
  cutflow_->Fill(0.5);
  edm::Handle<pat::JetCollection> jets;
  edm::Handle<pat::PackedCandidateCollection> packedCandidates;
  edm::Handle<reco::GenParticleCollection> genParticles;
  edm::Handle<reco::VertexCollection> primaryVertices;
  event.getByToken(jetsToken_, jets);
  event.getByToken(packedCandidatesToken_, packedCandidates);
  event.getByToken(primaryVerticesToken_, primaryVertices);
  if (isSignal_) event.getByToken(genParticlesToken_, genParticles);
  if (!jets.isValid() || !packedCandidates.isValid() ||
      (isSignal_ && !genParticles.isValid()) || !primaryVertices.isValid()) {
    throw cms::Exception("EXTRACT_MISSING_PRODUCT") << "one or more required MiniAOD products are absent";
  }
  if (primaryVertices->empty()) {
    throw cms::Exception("EXTRACT_INVALID_PRIMARY_VERTEX") << "primary vertex collection is empty";
  }
  pvZ_ = primaryVertices->front().z();
  nVertices_ = static_cast<int32_t>(primaryVertices->size());
  requireFinite(pvZ_, "pv_z");
  run_ = event.id().run();
  lumi_ = event.luminosityBlock();
  event_ = event.id().event();

  int32_t selectedJetIndex = 0;
  for (pat::JetCollection::const_iterator jet = jets->begin(); jet != jets->end(); ++jet) {
    cutflow_->Fill(1.5);
    requireFinite(jet->pt(), "jet_pt");
    requireFinite(jet->eta(), "jet_eta");
    requireFinite(jet->phi(), "jet_phi");
    if (jet->pt() < 500.0 || jet->pt() >= 1000.0 || std::abs(jet->eta()) >= 2.0) continue;
    cutflow_->Fill(2.5);
    jetIndex_ = selectedJetIndex++;
    truthMatchCount_ = isSignal_ ? matchSignal(*jet, *genParticles) : 0;
    if (isSignal_ && truthMatchCount_ != 1) continue;  // Rejected TT jets never become background.
    cutflow_->Fill(3.5);
    target_ = isSignal_ ? 1 : 0;
    jetPt_ = jet->pt();
    jetEta_ = jet->eta();
    jetPhi_ = jet->phi();
    resetParticles();

    for (size_t index = 0; index < jet->numberOfDaughters(); ++index) {
      const reco::CandidatePtr pointer = jet->daughterPtr(index);
      const pat::PackedCandidate* candidate =
          dynamic_cast<const pat::PackedCandidate*>(pointer.get());
      if (candidate == 0) {
        throw cms::Exception("EXTRACT_DAUGHTER_RESOLUTION")
            << "AK8 daughter " << index << " is not a packed candidate";
      }
      requireFinite(candidate->pt(), "particle_pt");
      requireFinite(candidate->eta(), "particle_eta");
      requireFinite(candidate->phi(), "particle_phi");
      requireFinite(candidate->energy(), "particle_energy");
      const bool hasTrackDetails = candidate->hasTrackDetails();
      particlePt_.push_back(candidate->pt());
      particleEta_.push_back(candidate->eta());
      particlePhi_.push_back(candidate->phi());
      particleEnergy_.push_back(candidate->energy());
      particleCharge_.push_back(candidate->charge());
      particlePdgId_.push_back(candidate->pdgId());
      particleDxy_.push_back(hasTrackDetails ? candidate->dxy() : 0.0);
      particleDxyError_.push_back(hasTrackDetails ? candidate->dxyError() : 0.0);
      particleDz_.push_back(hasTrackDetails ? candidate->dz() : 0.0);
      particleDzError_.push_back(hasTrackDetails ? candidate->dzError() : 0.0);
      particleHasTrackDetails_.push_back(hasTrackDetails ? 1 : 0);
      original_daughter_index.push_back(static_cast<uint32_t>(index));
    }
    cutflow_->Fill(4.5);
    cutflow_->Fill(5.5);
    jetsTree_->Fill();
    ++retainedJets_;
    cutflow_->Fill(6.5);
  }
}

void ParticleMLExtractor::endJob() { metadataTree_->Fill(); }

DEFINE_FWK_MODULE(ParticleMLExtractor);
