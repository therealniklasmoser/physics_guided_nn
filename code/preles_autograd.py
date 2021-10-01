# dependencies
import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from ctypes import *
import math
import torch
from numba import jit, cuda

c_path = "./src/"


# call function similar to preles.R
def PRELES(par, tair, vpd, precip, co2, fapar, GPPmeas=np.nan, ETmeas=np.nan, SWmeas=np.nan,
           p=[np.nan] * 30, doy=[np.nan],
           logflag=0, control=0, pft="evergreen", parmodel=0, lat=np.nan, par0=np.nan):
    par = par.detach().numpy()
    tair = tair.detach().numpy()
    vpd = vpd.detach().numpy()
    precip = precip.detach().numpy()
    co2 = co2.detach().numpy()
    fapar = fapar.detach().numpy()
    doy = doy.detach().numpy()
    print(doy)

    leng = 1
    if np.isnan(GPPmeas):
        GPPmeas = np.array([-999.] * leng)
    if np.isnan(ETmeas):
        ETmeas = np.array([-999.] * leng)
    if np.isnan(SWmeas):
        SWmeas = np.array([-999.] * leng)
    transp = np.array([-999.] * leng)
    evap = np.array([-999.] * leng)
    fWE = np.array([-999.] * leng)

    if not control:  # default set for conifer sites in scandinavia calibrated.
        defaults = [413.0,  ## 1 soildepth
                    0.450,  ## 2 ThetaFC
                    0.118,  ## 3 ThetaPWP
                    3.,  ## 4 tauDrainage
                    ## GPP_MODEL_PARAMETERS
                    0.7457,  ## 5 betaGPP
                    10.93,  ## 6 tauGPP
                    -3.063,  ## 7 S0GPP
                    17.72,  ## 8 SmaxGPP
                    -0.1027,  ## 9 kappaGPP
                    0.03673,  ## 10 gammaGPP
                    0.7779,  ## 11 soilthresGPP
                    0.500,  ## 12 b.CO2, cmCO2
                    -0.364,  ## 13 x.CO2, ckappaCO2
                    ## EVAPOTRANSPIRATION_PARAMETERS
                    0.2715,  ## 14 betaET
                    0.8351,  ## 15 kappaET
                    0.07348,  ## 16 chiET
                    0.9996,  ## 17 soilthresET
                    0.4428,  ## 18 nu ET
                    ## SNOW_RAIN_PARAMETERS
                    1.2,  ## 19 Meltcoef
                    0.33,  ## 20 I_0
                    4.970496,  ## 21 CWmax, i.e. max canopy water
                    0.,  ## 22 SnowThreshold,
                    0.,  ## 23 T_0,
                    160.,  ## 24 SWinit, ## START INITIALISATION PARAMETERS
                    0.,  ## 25 CWinit, ## Canopy water
                    0.,  ## 26 SOGinit, ## Snow on Ground
                    20.,  ## 27 Sinit ##CWmax
                    -999.,  ## t0 fPheno_start_date_Tsum_accumulation; conif -999, for birch 57
                    -999.,  ## tcrit, fPheno_start_date_Tsum_Tthreshold, 1.5 birch
                    -999.  ##tsumcrit, fPheno_budburst_Tsum, 134 birch]
                    ]
    if control:  # peltoniemi et al. 2015 Boreal Env. Res. for Hyytiala
        defaults = [413.0,
                    0.450, 0.118, 3., 0.748464, 12.74915, -3.566967, 18.4513, -0.136732,
                    0.033942, 0.448975, 0.500, -0.364, 0.33271, 0.857291, 0.041781,
                    0.474173, 0.278332, 1.5, 0.33, 4.824704, 0., 0., 180., 0., 0., 10.,
                    -999., -999., -999.]

    p = p.detach().numpy()

    if np.sum(np.isnan(p)) > 0:
        idx = [i for i, x in enumerate(p) if np.isnan(x)]
        for i in idx:
            p[i] = defaults[i]

    if pft != "evergreen":
        if len(doy) == 1:
            if np.isnan(doy) or np.sum(np.isnan(p[27:30])) > 0:
                return
        else:
            nn = [n for n in doy if n == np.nan]
            if len(nn) >= 1 or np.sum(np.isnan(p[27:30])) > 0:
                return

    if pft == "evergreen":
        if np.sum(np.isnan(p[27:30])):
            print("Phenology parameters given, but not implemented in the model for conifers.")
        p[27] = -999.

    if pft == "evergreen":
        if np.isnan(doy):
            doy = list(range(1, 366)) * math.ceil(leng / 365)
            doy = doy[0:(leng + 1)]
            doy = [int(d) for d in doy]


    # Set Parameters
    p1 = np.array(p[0])
    p2 = np.array(p[1])
    p3 = np.array(p[2])
    p4 = np.array(p[3])
    p5 = np.array(p[4])
    p6 = np.array(p[5])
    p7 = np.array(p[6])
    p8 = np.array(p[7])
    p9 = np.array(p[8])
    p10 = np.array(p[9])
    p11 = np.array(p[10])
    p12 = np.array(p[11])
    p13 = np.array(p[12])
    p14 = np.array(p[13])
    p15 = np.array(p[14])
    p16 = np.array(p[15])
    p17 = np.array(p[16])
    p18 = np.array(p[17])
    p19 = np.array(p[18])
    p20 = np.array(p[19])
    p21 = np.array(p[20])
    p22 = np.array(p[21])
    p23 = np.array(p[22])
    p24 = np.array(p[23])
    p25 = np.array(p[24])
    p26 = np.array(p[25])
    p27 = np.array(p[26])
    p28 = np.array(p[27])
    p29 = np.array(p[28])
    p30 = np.array(p[29])

    control = np.array(control, dtype=np.intc)
    logflag = np.array(logflag, dtype=np.intc)
    NofDays = np.array(leng, dtype=np.intc)
    day = np.array(doy, dtype=np.intc)
    # Outputs
    GPP = np.empty(leng, np.double)
    ET = np.empty(leng, np.double)
    SW = np.empty(leng, np.double)
    SOG = np.empty(leng, np.double)
    fS = np.empty(leng, np.double)
    fD = np.empty(leng, np.double)
    fW = np.empty(leng, np.double)
    fE = np.empty(leng, np.double)
    Throughfall = np.empty(leng, np.double)
    Interception = np.empty(leng, np.double)
    Snowmelt = np.empty(leng, np.double)
    Drainage = np.empty(leng, np.double)
    Canopywater = np.empty(leng, np.double)
    S = np.empty(leng, np.double)

    # Load C library
    lib = CDLL(''.join((c_path, 'call_preles.so')))
    preles = lib.call_preles
    # define types of required call_preles().c inputs
    preles.argtypes = [np.ctypeslib.ndpointer(dtype=np.double)] * 9 + [np.ctypeslib.ndpointer(dtype=np.double)] * 14 + \
                      [np.ctypeslib.ndpointer(dtype=np.double)] * 30 + [np.ctypeslib.ndpointer(dtype=np.intc)] * 4 + \
                      [np.ctypeslib.ndpointer(dtype=np.double)] * 3
    # outputs
    preles.restype = c_void_p

    preles(
        # inputs
        par, tair, vpd, precip, co2, fapar, GPPmeas, ETmeas, SWmeas,
        # Outputs
        GPP, ET, SW, SOG, fS, fD, fW, fE, Throughfall,
        Interception, Snowmelt, Drainage, Canopywater, S,
        # Parameters
        p1, p2, p3, p4, p5, p6, p7, p8, p9, p10, p11, p12, p13, p14, p15,
        p16, p17, p18, p19, p20, p21, p22, p23, p24, p25, p26, p27, p28, p29, p30,

        control, logflag, NofDays, day,
        transp,
        evap,
        fWE)

    return torch.tensor(GPP, dtype=torch.float, requires_grad=True), torch.tensor(ET, dtype=torch.float, requires_grad=True)

data_path = "./data/"
data = pd.read_csv(''.join((data_path, "testdat.csv")))
# INPUTS
PAR = torch.tensor(data['PAR'], dtype=torch.float64)
TAir = torch.tensor(data['TAir'], dtype=torch.float64)
VPD = torch.tensor(data['VPD'], dtype=torch.float64)
Precip = torch.tensor(data['Precip'], dtype=torch.float64)
CO2 = torch.tensor(data['CO2'], dtype=torch.double)
fAPAR = torch.tensor(data['fAPAR'], dtype=torch.double)
DOY = torch.tensor(data['DOY'], dtype=torch.float64)

# PARAMETERS
df = torch.tensor([
    413, 0.45, 0.118, 3, 0.7457, 10.93, -3.063,
             17.72, -0.1027, 0.03673, 0.7779, 0.5, -0.364, 0.2715,
             0.8351, 0.07348, 0.9996, 0.4428, 1.2, 0.33, 4.970496,
             0, 0, 160, 0, 0, 0, -999, -999, -999
], dtype=torch.float64)


par = torch.autograd.Variable(PAR, requires_grad=True)
tair = torch.autograd.Variable(TAir, requires_grad=True)
vpd = torch.autograd.Variable(VPD, requires_grad=True)
precip = torch.autograd.Variable(Precip, requires_grad=True)
co2 = torch.autograd.Variable(CO2, requires_grad=True)
fapar = torch.autograd.Variable(fAPAR, requires_grad=True)
doy = torch.autograd.Variable(DOY, requires_grad=True)
p = torch.autograd.Variable(df, requires_grad=True)

GPP, ET = PRELES(par=par[0], tair=tair[0], vpd=vpd[0], precip=precip[0], co2=co2[0], fapar=fapar[0], p=p, doy=doy[0])

gpp = par*2

print(GPP, ET)
print(GPP.grad_fn, ET.grad_fn)
print(gpp.grad_fn)
jit(target='cuda')
def bw(op):
    return op.backward()

print('do backward')
bw(GPP)
print(par.grad)
print(p.grad)
print(PRELES.grad_fn)