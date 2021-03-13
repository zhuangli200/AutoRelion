############################################################################
#   Written by Zhuang Li, Purdue University. Last modified at 2021-03-01   #
############################################################################
#Purdue Specific parameters
purdue ={}
purdue["domain_name"] = "purdue.edu"
purdue["mail_client"] = "mail"
purdue["cluster"] = "gilbreth.rcac.purdue.edu"
purdue["em_server"] = "/net/em"
purdue["appion_server"] = "https://mercury.rcac.purdue.edu"
purdue["appion_loi"] = "https://mercury.rcac.purdue.edu/myamiweb/queuecount.php?expId="
purdue["gctf_exe"] = "/apps/gctf/Gctf_v1.06/bin/Gctf-v1.06_sm_20_cu8.0_x86_64"
purdue["e2proc2d_exe"] = "/apps/eman2/EMAN2_2.22/bin/e2proc2d.py"
purdue["motioncorr2_exe"] = "/apps/motioncor2/1.2.1/MotionCor2_1.2.1-Cuda80"
purdue["microscope"] = {}
purdue["microscope"]["KriosG3"] = {"voltage":"300", "cs":"2.7", "camera":"K3"}
purdue["microscope"]["KriosG4"] = {"voltage":"300", "cs":"2.7", "camera":"K3"}
purdue["microscope"]["Talos"] = {"voltage":"200", "cs":"2.7", "camera":"K2"}
purdue["queue"] = "sbatch"
purdue["queue_partition"]= "chang-gpu"
purdue["cmd"] = {}

site = purdue