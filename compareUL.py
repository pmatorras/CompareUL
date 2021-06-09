import os, sys
from ROOT import *# TH1D, TH2D, TFile, TTree, TCanvas, gROOT, gStyle, gSystem
import numpy as np
#TH1D test
gROOT.SetBatch(True)
c1 = TCanvas( 'c1', 'Dynamic Filling Example', 200,10, 1600, 1200 )
c1.SetLeftMargin(0.12)
#Scale histograms                                                                                   
def ScaleToInt(histo):
    norm  = histo.GetSumOfWeights()
    histo.Scale(1/norm)
    return histo
#ControlRegions = ["Zpeak_ptmiss-100to140_nojet", "Zpeak_ptmiss-100to140", "Zpeak_ptmiss-140_nojet", "Zpeak_ptmiss-140", "Zpeak_ptmiss-160_nojet", "Zpeak_ptmiss-160"]
#variables      = [ "ptll", "mt2llOptim", "mt2ll", "deltaPhiLep", "ptmiss", "mt2llOptimHighExtra", "ptmissSR", "mt2llOptimHigh"] 
years = ["2017", "2018"]
regions = ["DYValidationRegion"]
all_info = {
    "DYValidationRegion" :
    {
        "variables" :
        [ "ptll", "mt2llOptim", "mt2ll", "deltaPhiLep", "ptmiss", "mt2llOptimHighExtra", "ptmissSR", "mt2llOptimHigh"],
        "ControlRegions" :
        ["Zpeak_ptmiss-100to140_nojet", "Zpeak_ptmiss-100to140", "Zpeak_ptmiss-140_nojet", "Zpeak_ptmiss-140", "Zpeak_ptmiss-160_nojet", "Zpeak_ptmiss-160"]
    }
}

web     = os.environ["WWW"]
compweb = web+"CompareUL/"
os.system("mkdir -p "+compweb)
os.system("cp -r Figures/* "+compweb)


for tag in all_info:
    variables      = all_info[tag]["variables"]
    ControlRegions = all_info[tag]["ControlRegions"]
    for year in years:
        hfileV8        = TFile("Data/plots_"+year+"DYValidationRegion_ALL_DATA.root")
        hfileV6        = TFile("Data/plots_"+year+"DYValidationRegionV6_ALL_DATA.root")
        for region in ControlRegions:
            for var in variables:
                cr_i  = hfileV8.cd(region)
                var_i = gDirectory.cd("mt2ll")
                if cr_i is False:
                    print "something's wrong with", region 
                    continue
                if var_i is False:
                    print "something's wrong with", region
                    continue
                doLogY  = False
                doLogX  = False
                if "ptll" in var:
                    doLogY = True
                    doLogX = True
                thisfol = "Figures/"+tag+"/"+region+"/"+year+"/"
                figbase = thisfol+tag+"_"+region+"_"+year+"_"+var
                os.system("mkdir -p "+thisfol)
                legend  = TLegend(0.6,0.8,0.88,0.88);
                histoV8 = hfileV8.Get(region+"/"+var+"/histo_DATA")
                histoV6 = hfileV6.Get(region+"/"+var+"/histo_DATA")
                legend.AddEntry(histoV8, "DYValidationRegion V8     " )
                legend.AddEntry(histoV6, "DYValidationRegion V6loose" )
                histoV6.SetTitle(region+"-"+var+" "+year)
                histoV6.GetXaxis().SetTitle(var)
                histoV6.GetYaxis().SetTitle("Events")
                gPad.SetLogy(doLogY)
                #gPad.SetLogx(doLogX)
                if doLogY: histoV6.SetMinimum(1)
                #if doLogX: histoV6.GetXaxis().SetRange(1,1000)
                if "ptll" in var: histoV6.GetXaxis().SetRangeUser(0,500)
                histoV6.SetStats(False)
                histoV6.Draw()
                histoV8.Draw("Same")

                legend.Draw()
                histoV8.SetLineColor(2)
                c1.SaveAs(figbase+".png")

                histoV6Norm = ScaleToInt(histoV6)
                histoV8Norm = ScaleToInt(histoV8)
                histoV6Norm.Draw()
                histoV6Norm.GetYaxis().SetTitle("Norm. Events")
                minVal = 0
                if doLogY: minVal = 0.01
                histoV6Norm.GetYaxis().SetRangeUser(0,1)

                histoV8Norm.Draw("Same")
                histoV8.SetLineColor(2)
                legend.Draw()
                c1.SaveAs(figbase+"_scaled.png")

        #exit()

    for reg in ControlRegions:
        for year in years:
            os.system("cp "+web+"index.php "+compweb+"/"+reg+"/"+year+"/")
