# -------------- DecayMode occupancies -------------- 
# store the releative signal and background fractions 
# (after lead track preselection) for the different   
# reconstructed decay modes used in the TaNC.         
# NB samples: signal - ZTT, QCD - QCDForPF_cfi        
TaNC_DecayModeOccupancy = {}
TaNC_DecayModeOccupancy['OneProngNoPiZero']                            = (0.314712, 0.176440)
TaNC_DecayModeOccupancy['OneProngOnePiZero']                           = (0.361116, 0.193352)
TaNC_DecayModeOccupancy['OneProngTwoPiZero']                           = (0.126279, 0.086276)
TaNC_DecayModeOccupancy['ThreeProngNoPiZero']                          = (0.150425, 0.256841)
TaNC_DecayModeOccupancy['ThreeProngOnePiZero']                         = (0.047468, 0.287091)

#------Occupancy Summary--------
# DecayMode                  Signal(%)     Bkg(%)
# OneProngNoPiZero               31.5%      17.6%
# OneProngOnePiZero              36.1%      19.3%
# OneProngTwoPiZero              12.6%       8.6%
# ThreeProngNoPiZero             15.0%      25.7%
# ThreeProngOnePiZero             4.7%      28.7%

CutSet_TaNC_OnePercent = {}
CutSet_TaNC_OnePercent['cvCut']                                        = 0.441572 # +/-0.049355
CutSet_TaNC_OnePercent['OneProngNoPiZero']                             = -0.328014
CutSet_TaNC_OnePercent['OneProngOnePiZero']                            = -0.381954
CutSet_TaNC_OnePercent['OneProngTwoPiZero']                            = -0.358321
CutSet_TaNC_OnePercent['ThreeProngNoPiZero']                           = 0.269862
CutSet_TaNC_OnePercent['ThreeProngOnePiZero']                          = 0.553145

CutSet_TaNC_HalfPercent = {}
CutSet_TaNC_HalfPercent['cvCut']                                       = 0.692367 # +/-0.022659
CutSet_TaNC_HalfPercent['OneProngNoPiZero']                            = 0.200438
CutSet_TaNC_HalfPercent['OneProngOnePiZero']                           = 0.050101
CutSet_TaNC_HalfPercent['OneProngTwoPiZero']                           = 0.224262
CutSet_TaNC_HalfPercent['ThreeProngNoPiZero']                          = 0.597459
CutSet_TaNC_HalfPercent['ThreeProngOnePiZero']                         = 0.844925

CutSet_TaNC_QuarterPercent = {}
CutSet_TaNC_QuarterPercent['cvCut']                                    = 0.848267 # +/-0.015411
CutSet_TaNC_QuarterPercent['OneProngNoPiZero']                         = 0.501530
CutSet_TaNC_QuarterPercent['OneProngOnePiZero']                        = 0.519533
CutSet_TaNC_QuarterPercent['OneProngTwoPiZero']                        = 0.526413
CutSet_TaNC_QuarterPercent['ThreeProngNoPiZero']                       = 0.841846
CutSet_TaNC_QuarterPercent['ThreeProngOnePiZero']                      = 0.941477

CutSet_TaNC_TenthPercent = {}
CutSet_TaNC_TenthPercent['cvCut']                                      = 0.938022 # +/-0.011358
CutSet_TaNC_TenthPercent['OneProngNoPiZero']                           = 0.818959
CutSet_TaNC_TenthPercent['OneProngOnePiZero']                          = 0.771675
CutSet_TaNC_TenthPercent['OneProngTwoPiZero']                          = 0.769673
CutSet_TaNC_TenthPercent['ThreeProngNoPiZero']                         = 0.925709
CutSet_TaNC_TenthPercent['ThreeProngOnePiZero']                        = 0.983095

CutSet_TaNC_TwentiethPercent = {}
CutSet_TaNC_TwentiethPercent['cvCut']                                  = 0.962972 # +/-0.005440
CutSet_TaNC_TwentiethPercent['OneProngNoPiZero']                       = 0.898613
CutSet_TaNC_TwentiethPercent['OneProngOnePiZero']                      = 0.856870
CutSet_TaNC_TwentiethPercent['OneProngTwoPiZero']                      = 0.904960
CutSet_TaNC_TwentiethPercent['ThreeProngNoPiZero']                     = 0.953780
CutSet_TaNC_TwentiethPercent['ThreeProngOnePiZero']                    = 0.984664


#------BMP Cut Summary----------
#                                 Fake Rate  SignalEff     OneProngNoPiZero    OneProngOnePiZero    OneProngTwoPiZero   ThreeProngNoPiZero  ThreeProngOnePiZero
# OnePercent                         0.996%      64.7%              -0.3280              -0.3820              -0.3583               0.2699               0.5531
# HalfPercent                        0.494%      57.6%               0.2004               0.0501               0.2243               0.5975               0.8449
# QuarterPercent                     0.249%      48.3%               0.5015               0.5195               0.5264               0.8418               0.9415
# TenthPercent                       0.099%      34.6%               0.8190               0.7717               0.7697               0.9257               0.9831
# TwentiethPercent                   0.049%      24.9%               0.8986               0.8569               0.9050               0.9538               0.9847
