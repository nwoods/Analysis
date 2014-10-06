from defs import *


#load the ratio of signal and background and the slopes
pmap = PartitionMap(curvArr,etaArr,phiArr,"kalmanTargetJpsi.root")

pmap.load('JDataFits.root','slope_fit','slope')
pmap.load('JDataFits.root','BKGoverSIGNAL_fit','ratio')
pmap.declareData('mass',0.0)

builder = DataSetBuilder(pmap,w,'../../data/JGEN.root','data',50000000)
builder.load("JGEN_Input.root")

w.var('massRaw').setBins(50)
w.var('massRaw').setMin(2.9)
w.var('massRaw').setMax(3.3)

w.factory('RooExponential::pdf(massRaw,slope[-1,-8.,10])')


def estimate(minMass,maxMass,bkg=True):
    for bin,data in builder.data('pos').iteritems():
        NSIG = data.numEntries()
        ratio = pmap.getData('ratio',bin)
        
        #for this bin generate a background sample
        slope = pmap.getData('slope',bin)
        w.var('slope').setVal(slope)
        dataset = w.pdf('pdf').generate(ROOT.RooArgSet(w.var('massRaw')),NSIG*ratio)
        dataset.append(data)
        dataset=dataset.reduce('massRaw>'+str(minMass)+'&&massRaw<'+str(maxMass))
        if not bkg:
            dataset = data.reduce('massRaw>'+str(minMass)+'&&massRaw<'+str(maxMass))
        pmap.setData('mass',bin,dataset.mean(w.var('massRaw')),0.0)
          
    pmap.save('fit')      
          
