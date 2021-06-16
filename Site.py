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
#Microscope Information
purdue["defaultVoltage"] = 300
purdue["defaultCs"] = 2.7
purdue["defaultEPS"] = 20
purdue["defaultExpTime"] = 3.12
purdue["defaultMoviePath"] = "rawdata/*.tif"
purdue["defaultFrameNr"] = 40
purdue["defaultGain"] = "rawdata/references/"
purdue["defaultMode"] = 2 # 1 for super-resolution mode, and 2 for counting mode
purdue["defaultMicsPath"] = "DW/*.mrc"
purdue["defaultApix"] = 1.05
purdue["defaultBoxSize"] = 128
purdue["gain-movie-operation"] = "asis" #flip rotate
purdue["defaultSleepTime"] = "5"
purdue["defaultMpiNr"] = "1"
purdue["cmd"] = {}
purdue["queue"] = "sbatch"
purdue["queue_partition"] = "chang-gpu"

site = purdue