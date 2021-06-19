import os, sys, optparse
from ROOT import *# TH1D, TH2D, TFile, TTree, TCanvas, gROOT, gStyle, gSystem
import numpy as np
gROOT.SetBatch(True)
c1 = TCanvas( 'c1', 'Dynamic Filling Example', 200,10, 1600, 1200 )
c1.SetLeftMargin(0.12)
#Scale histograms                                                                                   
def ScaleToInt(histo):
    norm  = histo.GetSumOfWeights()
    histo.Scale(1/norm)
    return histo

def GetRanges(histo1, histo2, isLog=False):
    maxVal = max(histo1.GetMaximum(), histo2.GetMaximum())
    minVal = min(histo1.GetMinimum(1e-8), histo2.GetMinimum(1e-8))
    multip = 1.05
    if isLog: multip =1.2
    histo1.GetYaxis().SetRangeUser(minVal,multip*maxVal)

all_info = {
    "DYValidationRegion" :
    {
        "variables"      :
        [ "ptll", "mt2llOptim", "mt2ll", "deltaPhiLep", "ptmiss", "mt2llOptimHighExtra", "ptmissSR", "mt2llOptimHigh"],
        "ControlRegions" :
        ["Zpeak_ptmiss-100to140_nojet", "Zpeak_ptmiss-100to140", "Zpeak_ptmiss-140_nojet", "Zpeak_ptmiss-140", "Zpeak_ptmiss-160_nojet", "Zpeak_ptmiss-160"],
        "years"          : ["2017"] ,
        "tweaks"         : ["SmearEENoiseDPhiHEM", ""]
    },


    "DYControlRegion"    :
    {
        "variables"      :
        ["Lep2pt","ptmisssig", "deltaRLep", "njets", "ptll", "Lep1pt", "jetpt", "dPhiMinlepptmiss", "mt2ll", "deltaPhiLep",
  	 "nbjets", "mll", "ptmiss", "dPhillptmiss", "nPV", "dPhijet0ptmiss", "dPhijet1ptmiss",	 "mTllptmiss"],
        "ControlRegions" :
        ["DY_ee", "DY_mm", "DY_ee_jet", "DY_mm_jet"],
        "years"          : ["2017"],
        "tweaks"         : ["SmearEENoiseDPhiHEM", "SmearDPhiHEM", "SmearVetoNoiseEEDPhiHEM"]
    },
    
    "HighPtMissControlRegion"    :
    {
        "variables"      :
        ["Lep2pt","ptmisssig", "deltaRLep", "njets", "ptll", "Lep1pt", "jetpt", "dPhiMinlepptmiss", "mt2ll", "deltaPhiLep",
  	 "nbjets", "mll", "ptmiss", "dPhillptmiss", "nPV", "dPhijet0ptmiss", "dPhijet1ptmiss",	 "mTllptmiss"],
        "ControlRegions" :
        ["VR1_Tag_em", "VR1_Tag_sf", "VR1_Veto_em", "VR1_Veto_sf"],
        "years"          : ["2017"],
        "tweaks"         : ["SmearEENoiseDPhiHEM", "SmearDPhiHEM", "SmearVetoNoiseEEDPhiHEM"]
    }
        
}
extraCRs= ["Veto0_Tag", "Veto0_Tag_highptmiss", "Veto0_Veto", "Veto0_Veto_highptmiss",
           "Veto1_Tag", "Veto1_Tag_highptmiss", "Veto1_Veto", "Veto2_Veto_highptmiss",
           "Veto2_Tag", "Veto2_Tag_highptmiss", "Veto2_Veto", "Veto2_Veto_highptmiss"]

VetoNoiseEEvars = ["dPhiEENoisePtMissPt50", "HTForwardSoft", "HTForwardSoft", "jetRawPtEENoise", "dPhiEENoisePtMissPt15NoRawCut", "dPhiEENoisePtMissPt30NoRawCut" , "dPhiEENoisePtMissHard", "dPhiEENoisePtMissPt15", "HTForward", "dPhiEENoisePtMissPt30"]
usage  = 'usage: %prog [options]'
parser = optparse.OptionParser(usage)
parser.add_option('-t', '--test'     , dest = 'test'     , help = 'Just some plots  ', default = False, action = 'store_true')
(opt, args) = parser.parse_args()

def fileismissing(filenm):
    skip = False
    if os.path.isfile(filenm) is False:
        print "\nFILE MISSING: "+filenm+"\n"
        skip = True
    return skip
web     = os.environ["WWW"]
compweb = web+"CompareUL/"
doTest  = opt.test
for tag in all_info:
    #if "Control" not in tag: continue
    tweaks         = all_info[tag]["tweaks"]
    for tweak in tweaks:
        variables      = all_info[tag]["variables"]
        ControlRegions = all_info[tag]["ControlRegions"]
        if "VetoNoiseEE" in tweak :
            ControlRegions += extraCRs
            variables       = VetoNoiseEEvars
        for year in all_info[tag]["years"]:
            hfileV8nm  = "Data/plots_"+year+tag+tweak+"V8_ALL_DATA.root"
            hfileV6nm  = "Data/plots_"+year+tag+tweak+"V6_ALL_DATA.root"
            missV8     = fileismissing(hfileV8nm)
            missV6     = fileismissing(hfileV6nm)
            if missV8 or missV6: continue
            hfileV8 = TFile(hfileV8nm)
            hfileV6 = TFile(hfileV6nm)
            for region in ControlRegions:
                folloc  = year+"/"+tag+"/"+tweak+"/"+region+"/"
                thisfol = "Figures/"+folloc
                webloc  = compweb+folloc
                nplots  = 0
                for var in variables:
                    if nplots>0 and doTest: continue
                    cr_i  = hfileV8.cd(region)
                    var_i = gDirectory.cd(var)
                    if cr_i is False:
                        print "something's wrong with", year+tag+tweak, "region", region
                        exit()
                        continue
                    if var_i is False:
                        print "something's wrong with", region
                        continue
                    doLogY  = False
                    doLogX  = False
                    if "ptll" in var:
                        doLogY = True
                        doLogX = True
                    figbase = tag+tweak+"_"+year+"_"+region+"_"+var
                    os.system("mkdir -p "+thisfol)
                    legend  = TLegend(0.6,0.8,0.88,0.88);
                    histoV8 = hfileV8.Get(region+"/"+var+"/histo_DATA")
                    histoV6 = hfileV6.Get(region+"/"+var+"/histo_DATA")
                    legend.AddEntry(histoV8, region+"V8     " )
                    legend.AddEntry(histoV6, region+"V6loose" )
                    histoV6.SetTitle(region+tweak+"-"+var+" "+year)
                    histoV6.GetXaxis().SetTitle(var)
                    histoV6.GetYaxis().SetTitle("Events")
                    gPad.SetLogy(doLogY)
                    GetRanges(histoV6, histoV8)
                    if "ptll" in var: histoV6.GetXaxis().SetRangeUser(0,500)
                    histoV6.SetStats(False)
                    histoV6.Draw()
                    histoV8.Draw("Same")
                    histoV8.SetLineWidth(0)
                    histoV8.SetMarkerStyle(3)
                    histoV8.SetMarkerSize(2)
                    histoV8.SetMarkerColor(2)
                    legend.Draw()
                    histoV8.SetLineColor(2)

                    nV6 = histoV6.GetSumOfWeights()
                    nV6i = histoV6.GetEntries()
                    nV8 = histoV8.GetSumOfWeights()
                    #print nV6, nV6i
                    c1.SaveAs(thisfol+figbase+".png")

                    gPad.SetLogy(True)
                    GetRanges(histoV6,histoV8, True)
                    histoV6.Draw()
                    histoV8.Draw("Same")
                    c1.SaveAs(thisfol+"log_"+figbase+".png")

                    gPad.SetLogy(False)
                    histoV6Norm = ScaleToInt(histoV6)
                    histoV8Norm = ScaleToInt(histoV8)
                    histoV6Norm.Draw("")
                    histoV6Norm.GetYaxis().SetTitle("Norm. Events")
                    histoV8Norm.Draw("Same")
                    legend.Draw()
                    GetRanges(histoV6Norm, histoV8Norm, doLogY)
                    c1.SaveAs(thisfol+"scaled_"+figbase+".png")

                    gPad.SetLogy(True)
                    histoV6Norm.Draw()
                    histoV8Norm.Draw("Same")
                    legend.Draw()
                    GetRanges(histoV6Norm, histoV8Norm, True)
                    c1.SaveAs(thisfol+"log_scaled_"+figbase+".png")

                    nplots+=1
                os.system("mkdir -p "                + webloc)
                os.system("cp " + thisfol + "/* "    + webloc)
                os.system("cp " + web + "index.php " + compweb)

                otherfol = ''
                for folsplit in folloc.split('/'):
                    otherfol += folsplit+'/'
                    if folsplit =='': continue
                    os.system('cp '+web+'index.php ' + compweb+otherfol) 

            #exit()

