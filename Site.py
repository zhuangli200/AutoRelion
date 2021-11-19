############################################################################
#   Written by Zhuang Li, Purdue University. Last modified at Nov 19, 2021 #
############################################################################
hubu = {}
hubu["domain_name"] = "hubu.edu.cn"
hubu["mail_client"] = "mail"
hubu["cluster"] = "202.114.156.70"
hubu["gctf_exe"] = "/home/t20210106/.local/apps/external/GCTF_v1.18_sm30-75_cu10.1"
hubu["motioncorr2_exe"] = "/home/t20210106/.local/apps/external/MotionCor2_1.4.5_Cuda101-10-22-2021"
#Microscope Information
hubu["defaultVoltage"] = 300
hubu["defaultCs"] = 2.7
hubu["defaultEPS"] = 15
hubu["defaultExpTime"] = 2.5
hubu["defaultMoviePath"] = "movies/*.tiff"
hubu["defaultMode"] = "2" # 2 for super-resolution mode, and 1 for counting mode
hubu["defaultFrameNr"] = 40
hubu["defaultMicsPath"] = "DW/*.mrc"
hubu["defaultApix"] = 0.85
hubu["defaultBoxSize"] = 128
#Computation Information
hubu["defaultSleepTime"] = "5"
hubu["defaultMpiNr"] = "1"

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
purdue["defaultMode"] = 2 
purdue["defaultMicsPath"] = "DW/*.mrc"
purdue["defaultApix"] = 1.05
purdue["defaultBoxSize"] = 128
purdue["gain-movie-operation"] = "asis" #flip rotate
#Computation Information
purdue["defaultSleepTime"] = "5"
purdue["defaultMpiNr"] = "1"
purdue["sync"] = "globus"
# The following $prefix cannot be changed
purdue["queue_cmd"] = "sbatch" #  or PBS
purdue["queue_template"]= """<<EOF
#! /bin/bash
#SBATCH --job-name=$prefix
#SBATCH --ntasks=3
#SBATCH --partition=chang-gpu
#SBATCH --cpus-per-task=2
#SBATCH --time=0
#SBATCH --mem=30G
#SBATCH --gres=gpu:2
export CUDA_DEVICE_ORDER=PCI_BUS_ID"""
#purdue["link_cmd"] = "ln -s"
#purdue["data_prefix"] = ""
#purdue["link_dw_template"] = "rsync -azvr user@192.168.1.1:/net/em/leginon/{session}/rawdata/*-DW.mrc {mics_path}"
#purdue["link_dw_template"] = "rsync -azvr user@192.168.1.1:/net/em/leginon/{session}/rawdata/*-DW.mrc {mics_path}"
#purdue["link_movie_template"] = "rsync -azvr user@192.168.1.1:/net/em/frames/{session}/rawdata/*.tif {movie_path}"
#purdue["link_movie_template"] = "rsync -azvr user@192.168.1.1:/net/em/frames/{session}/rawdata/*.tif {movie_path}"
#purdue["link_dw_template"] = "globus transfer $NYSBC_GLOBUS_ID:/gpfs/leginon/$NYSBC_USERNAME/$1/rawdata/*DW.mrc $LOCAL_GLOBUS_ID:$LOCAL_FOLDER/$1/DW/ --recursive --label $1$2"

site = hubu