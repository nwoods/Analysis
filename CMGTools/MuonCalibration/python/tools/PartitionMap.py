import ROOT

from array import array
import copy
import math
class PartitionMap(object):
    def __init__(self,ptInv,eta,phi,log = ""):

        self.dimensions={'curv':ptInv,'eta':eta,'phi':phi}
        self.map =ROOT.TH3F('map','map',len(ptInv)-1,array('f',ptInv),len(eta)-1,array('f',eta),len(phi)-1,array('f',phi))

        self.loader = None
        self.data={}
        if log != "":
            self.log = ROOT.TFile(log,"RECREATE")
        else:    
            self.log = None

        

    def limits(self):
        xmin = self.map.GetXaxis().GetXmin()
        xmax = self.map.GetXaxis().GetXmax()
        ymin = self.map.GetYaxis().GetXmin()
        ymax = self.map.GetYaxis().GetXmax()
        zmin = self.map.GetZaxis().GetXmin()
        zmax = self.map.GetZaxis().GetXmax()
        return {'curv':[xmin,xmax],'eta':[ymin,ymax],'phi':[zmin,zmax]}

    def load(self,filename,histo,data):
        if self.loader is None:
            self.loader = ROOT.TFile(filename)
        h=self.loader.Get(histo)
        self.data[data] = h.Clone()
        

    def save(self,prefix = ""):
        if self.log is not None:
            for name,histo in self.data.iteritems():
                self.log.cd()
                histo.Write(name+"_"+prefix)
            self.log.Flush()    


            

    def average(self,name,datasets):
        sumw=0.0
        sum=0.0
        for binx in range(1,self.map.GetXaxis().GetNbins()+1):
            for biny in range(1,self.map.GetYaxis().GetNbins()+1):
                for binz in range(1,self.map.GetYaxis().GetNbins()+1):
                    bin = self.bin(binx,biny,binz)
                    sum=sum+datasets[bin].sumEntries()*self.data[name].GetBinContent(bin)
                    sumw=sumw+datasets[bin].sumEntries()
        return sum/sumw             
        
            
    def declareData(self,name,defaultVal = 0.0):
        newMap = copy.deepcopy(self.map)
        newMap.SetName(name)
        
        for i in range(0,self.bins_curv()+2):
            for j in range(0,self.bins_eta()+2):
                for k in range(0,self.bins_phi()+2):
                    bin = self.bin(i,j,k)
                    newMap.SetBinContent(bin,defaultVal)
        self.data[name] = newMap

    def setData(self,name,bin,data,error = 0.0):
        self.data[name].SetBinContent(bin,data)
        self.data[name].SetBinError(bin,error)

    def getData(self,name,bin):
        return self.data[name].GetBinContent(bin)
    def getDataError(self,name,bin):
        return self.data[name].GetBinError(bin)

    def addData(self,name,bin,data,error = 0.0):
        self.data[name].SetBinContent(bin,self.data[name].GetBinContent(bin)+data)
        self.data[name].SetBinError(bin,error)

    def multiplyData(self,name,bin,data,error=0.0):
        self.data[name].SetBinContent(bin,self.data[name].GetBinContent(bin)*data)
        self.data[name].SetBinError(bin,error)

    def multiplyDataProj(self,name,binx,biny,binz,data):
        if binx == 'all':
            binsx = range(1,self.map.GetXaxis().GetNbins()+1)
        else:
            binsx = [binx]
        if biny == 'all':
            binsy = range(1,self.map.GetYaxis().GetNbins()+1)
        else:
            binsy = [biny]
        if binz == 'all':
            binsz = range(1,self.map.GetZaxis().GetNbins()+1)
        else:
            binsz = [binz]

        for bx  in binsx:
            for by  in binsy:
                for bz  in binsz:
                    self.data[name].SetBinContent(self.bin(bx,by,bz),self.data[name].GetBinContent(self.bin(bx,by,bz))*data)

    def addDataProj(self,name,binx,biny,binz,data):
        if binx == 'all':
            binsx = range(1,self.map.GetXaxis().GetNbins()+1)
        else:
            binsx = [binx]
        if biny == 'all':
            binsy = range(1,self.map.GetYaxis().GetNbins()+1)
        else:
            binsy = [biny]
        if binz == 'all':
            binsz = range(1,self.map.GetZaxis().GetNbins()+1)
        else:
            binsz = [binz]

        for bx  in binsx:
            for by  in binsy:
                for bz  in binsz:
                    self.data[name].SetBinContent(self.bin(bx,by,bz),self.data[name].GetBinContent(self.bin(bx,by,bz))+data)
            

        


    def getMap(self):
        return self.map

    def bin(self,x,y,z):
        return self.map.GetBin(x,y,z)

    def binXYZ(self,bin):
        binx = ROOT.Long(0)
        biny = ROOT.Long(0)
        binz = ROOT.Long(0)
        self.map.GetBinXYZ(bin,binx,biny,binz)

        
        return binx,biny,binz 

    def binVals(self,bin):
        binx,biny,binz = self.binXYZ(bin)
        return self.map.GetXaxis().GetBinCenter(binx), \
               self.map.GetYaxis().GetBinCenter(biny), \
               self.map.GetZaxis().GetBinCenter(binz)
    



    def binFromVals (self,x,y,z):
        binx = self.map.GetXaxis().FindBin(x)
        biny = self.map.GetYaxis().FindBin(y)
        binz = self.map.GetZaxis().FindBin(z)
        return self.bin(binx,biny,binz)


    def bins_curv(self):
        return self.map.GetNbinsX()

    def bins_eta(self):
        return self.map.GetNbinsY()

    def bins_phi(self):
        return self.map.GetNbinsZ()

    def boundaries_curv(self,bin):
        binC=ROOT.Long(0)
        binEta=ROOT.Long(0)
        binPhi=ROOT.Long(0)

        self.map.GetBinXYZ(bin,binC,binEta,binPhi)
        return (self.map.GetXaxis().GetBinLowEdge(binC),self.map.GetXaxis().GetBinUpEdge(binC))

    def boundaries_eta(self,bin):
        binC=ROOT.Long(0)
        binEta=ROOT.Long(0)
        binPhi=ROOT.Long(0)

        self.map.GetBinXYZ(bin,binC,binEta,binPhi)
        return (self.map.GetYaxis().GetBinLowEdge(binEta),self.map.GetYaxis().GetBinUpEdge(binEta))

    def boundaries_phi(self,bin):
        binC=ROOT.Long(0)
        binEta=ROOT.Long(0)
        binPhi=ROOT.Long(0)

        self.map.GetBinXYZ(bin,binC,binEta,binPhi)
        return (self.map.GetZaxis().GetBinLowEdge(binPhi),self.map.GetZaxis().GetBinUpEdge(binPhi))
    

    def smearEbE2D(self,data,shift = 1.0,errorScale=1.0,updateMass = True):
        random = ROOT.TRandom3(101082)
        newData = ROOT.RooDataSet(data.GetName()+'cal',data.GetName(),data.get())
        for evt in range(0,data.numEntries()):
            line = data.get(evt)

            errx = errorScale*2*line.find('massErrRaw1').getVal()*line.find('curvRaw1').getVal()/line.find('massRaw').getVal()
            erry = errorScale*2*line.find('massErrRaw2').getVal()*line.find('curvRaw2').getVal()/line.find('massRaw').getVal()

            s1=random.Gaus(0.0,errx)
            s2=random.Gaus(0.0,erry)

            c1 = shift*line.find('curvRaw1').getVal()+s1
            c2 = shift*line.find('curvRaw2').getVal()+s2

            if c1<=0:
                continue
            if c2<=0:
                continue
            
            line.find('curvRaw1').setVal(c1)
            line.find('curvRaw2').setVal(c2)

            v1=ROOT.TLorentzVector()
            v1.SetPtEtaPhiM(1./line.find('curvRaw1').getVal(),
                                   line.find('etaRaw1').getVal(),
                                   line.find('phiRaw1').getVal(),
                                   0.1056583715)

            
            v2=ROOT.TLorentzVector()
            v2.SetPtEtaPhiM(1./line.find('curvRaw2').getVal(),
                                   line.find('etaRaw2').getVal(),
                                   line.find('phiRaw2').getVal(),
                                   0.1056583715)

            if updateMass:
                line.find('massRaw').setVal((v1+v2).M())

            


            newData.add(line)

        return newData


    def smear2D(self,data,w,resolution=0.02):
        random = ROOT.TRandom3(101082)
        newData = ROOT.RooDataSet(data.GetName()+'cal',data.GetName(),data.get())
        for evt in range(0,data.numEntries()):
            line = data.get(evt)

            errx = resolution*line.find('curvRaw1').getVal()
            erry = resolution*line.find('curvRaw2').getVal()


#            print 'before',line.find('curvRaw1').getVal(),line.find('curvRaw2').getVal(),line.find('massRaw').getVal()

            line.find('curvRaw1').setVal(line.find('curvRaw1').getVal()+random.Gaus(0.0,errx))
            line.find('curvRaw2').setVal(line.find('curvRaw2').getVal()+random.Gaus(0.0,erry))

            v1=ROOT.TLorentzVector()
            v1.SetPtEtaPhiM(1./line.find('curvRaw1').getVal(),
                                   line.find('etaRaw1').getVal(),
                                   line.find('phiRaw1').getVal(),
                                   w.var('muMass').getVal())
            
            v2=ROOT.TLorentzVector()
            v2.SetPtEtaPhiM(1./line.find('curvRaw2').getVal(),
                                   line.find('etaRaw2').getVal(),
                                   line.find('phiRaw2').getVal(),
                                   w.var('muMass').getVal())

            line.find('massRaw').setVal((v1+v2).M())

#            print 'after',line.find('curvRaw1').getVal(),line.find('curvRaw2').getVal(),line.find('massRaw').getVal()
            
            newData.add(line)

        return newData





