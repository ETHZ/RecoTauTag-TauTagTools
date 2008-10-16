from ROOT import gSystem, gDirectory, gROOT, TCanvas, TF1, TPad, TChain,TH1, TTree, TEventList, TEntryList, THStack, TColor, TFile, gStyle

gROOT.SetBatch(True)
gROOT.SetBatch(True)

isolateFirst = True

SignalRecoTreeName = "pfTauDecayModeHighEfficiency"
BackgroundRecoTreeName = "pfTauDecayModeHighEfficiency"

def getEntryList(chain, cut, name, subsetEntryList = 0):
   if subsetEntryList != 0:
      chain.SetEntryList(subsetEntryList)

   entryListName = chain.GetName() + "_" + name
   chain.Draw(">>%s" % entryListName, cut, "entrylist")
   output = gDirectory.Get(entryListName)
   chain.GetEntryList() #free entrylist
   chain.SetEntryList(0)
   return output

chainInfoFile            = TFile.Open("chainInfo.root", "RECREATE")

SignalData = "finishedJobsSignal/*.root"
BackgroundData = "finishedJobsBackground/*.root"

SignalTruthChain = TChain("truth")
SignalRecoChain  = TChain(SignalRecoTreeName)

print "Added %i signal files." % SignalTruthChain.Add(SignalData);
SignalRecoChain.Add(SignalData);
SignalTruthChain.SetName("SignalTruth")
SignalRecoChain.SetName("SignalReco")

BackgroundTruthChain = TChain("truth")
BackgroundRecoChain  = TChain(BackgroundRecoTreeName)
print "Added %i backgroudn files." % BackgroundTruthChain.Add(BackgroundData);
BackgroundRecoChain.Add(BackgroundData);
BackgroundTruthChain.SetName("BackgroundTruth")
BackgroundRecoChain.SetName("BackgroundReco")

SignalRecoChain.AddFriend(SignalTruthChain)
BackgroundRecoChain.AddFriend(BackgroundTruthChain)

listOfChains = [ SignalRecoChain, BackgroundRecoChain ]
entryListsToWrite = []

for chain in listOfChains:
   chainName = chain.GetName()
   print "Getting all entry list for ", chainName
   allEntryList = getEntryList(chain, "", "All")
   entryListsToWrite.append(allEntryList)
   print "Getting non null entry list for ", chainName
   nonNullList = getEntryList(chain, "!__ISNULL__", "NonNull")
   entryListsToWrite.append(nonNullList)
   isNullList = getEntryList(chain, "__ISNULL__", "IsNull")
#   isNullList = allEntryList.Clone()
#   isNullList.SetName(chainName + "_" + "IsNull")
#   isNullList.Subtract(nonNullList)
   entryListsToWrite.append(isNullList)

   print "Getting Standard Iso"
   standardIso = getEntryList(chain, "!__ISNULL__ && OutlierAngle@.size() == 0 && DecayMode <= 12 && TrackPt@.size() != 1 && !__PREFAIL__", "StandardIso")
   entryListsToWrite.append(standardIso)

   print "Getting Loosest Iso"
   loosestIso = getEntryList(chain, "!__ISNULL__ && Alt$(NeutralOutlierPt[0],0) < 1.5 && Alt$(ChargedOutlierPt[0],0) < 1 && DecayMode <= 12 && TrackPt@.size() != 1 && !__PREFAIL__", "Iso15GeV")
   entryListsToWrite.append(loosestIso)

   print "Getting Loose Iso"
   looseIso = getEntryList(chain, "OutlierPt[0] < 1.0", "Iso10GeV", loosestIso)
   looseIso.Add(standardIso)
   entryListsToWrite.append(looseIso)

   print "Getting prepass"
   prePass     = getEntryList(chain, "__PREPASS__", "PrePass", nonNullList)
   entryListsToWrite.append(prePass)
   print "Getting prefail, and two tracks"
   preFail     = getEntryList(chain, "__PREFAIL__ || TrackPt@.size() == 1 || DecayMode > 12", "PreFail", nonNullList)
   entryListsToWrite.append(preFail)
   print "Getting MVA applicable"
   everyThingElse = nonNullList.Clone()
   failsIso = nonNullList.Clone()

   failsIso.Subtract(prePass)
   failsIso.Subtract(preFail)
   failsIso.Subtract(loosestIso)
   failsIso.SetName(chainName+"_FailsIso")
   entryListsToWrite.append(failsIso)

   if isolateFirst:
      everyThingElse = loosestIso.Clone()
   else:
      everyThingElse.Subtract(preFail)

   everyThingElse.Subtract(prePass)
   everyThingElse.SetName(chainName + "_PreMVA")
   entryListsToWrite.append(everyThingElse)
   print "Getting one prong"
   oneProng = getEntryList(chain, "DecayMode < 5", "OneProng", everyThingElse)
   entryListsToWrite.append(oneProng)
   threeProng = getEntryList(chain, "DecayMode > 9 && DecayMode <= 12", "ThreeProng", everyThingElse)
   entryListsToWrite.append(threeProng)
   print "Getting single pion"
   singlePion = getEntryList(chain, "DecayMode == 0", "SinglePion", oneProng)
   entryListsToWrite.append(singlePion)
   print "Getting rho "
   RhoResonance = getEntryList(chain, "DecayMode == 1", "RhoResonance", oneProng)
   entryListsToWrite.append(RhoResonance)
   print "Getting single prong a"
   AResonanceOneProng = getEntryList(chain, "DecayMode > 1", "AResonanceOneProng", oneProng)
   entryListsToWrite.append(AResonanceOneProng)

print "Signal entries: %i" % SignalTruthChain.GetEntries()
print "Background entries: %i" % BackgroundTruthChain.GetEntries()

for aEntryList in entryListsToWrite:
   print "Entry list %s: %i" % (aEntryList.GetName(), aEntryList.GetN())
   aEntryList.Write()

SignalTruthChain.Write()
SignalRecoChain.Write()
BackgroundTruthChain.Write()
BackgroundRecoChain.Write()

chainInfoFile.Close();








