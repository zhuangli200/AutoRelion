############################################################################
#   Written by Zhuang Li, Purdue University. Last modified at 2021-03-01   #
############################################################################

#code section for assembling bash template
HEADER = """#! /bin/bash
##################################################
#    Author: Zhuang Li, Purdue University        #
#        Generated at : {current_time}              #
#   This script only works for Relion 3.1        #
##################################################

submit2d(){{
  mkdir -p stars Class2D/job999
  prefix=$(date "+%H%M%S")
  starfile="stars/"$prefix".star"
  touch stars/done.list
  grep -v -f stars/done.list Extract/{extract_job}/particles.star  > $starfile
  if [ $(wc -l $starfile | cut -d " " -f 1) -lt 50000 ];then
    /bin/rm $starfile
  else
    sbatch <<EOF
#! /bin/bash
#SBATCH --job-name=$prefix
#SBATCH --ntasks=3
#SBATCH --partition=chang-gpu
#SBATCH --cpus-per-task=2
#SBATCH --time=0
#SBATCH --mem=30G
#SBATCH --gres=gpu:2
export CUDA_DEVICE_ORDER=PCI_BUS_ID
echo "CUDA_VISIBLE_DEVICES = $CUDA_VISIBLE_DEVICES"
mpirun -np 3 `which relion_refine_mpi` --o Class2D/job999/$prefix --i $starfile --dont_combine_weights_via_disc --preread_images --pool 30 --pad 2 --ctf  --iter 25 --tau2_fudge 2 --particle_diameter {mask_diameter} --K 50 --flatten_solvent --zero_mask  --strict_highres_exp 8 --oversampling 1 --psi_step 12 --offset_range 5 --offset_step 2 --norm --scale  --j 2 --gpu ""  --pipeline_control Class2D/job999/
EOF
    if [ $? -eq 0 ];then
      col=$(head -n 40 $starfile |grep _rlnMicrographName|cut -d "#" -f 2)
      tail -n +40 $starfile | awk -v c=$col '{{print $c}}'|sed '/^$/d'| sort | uniq >> stars/done.list
    else
      echo "Failed to submit job"
      /bin/rm $starfile
    fi
  fi
}}

#Start of the script
/bin/rm 12345.done 1345.done 2>/dev/null
PENALTY_VALUE=4
while [ $PENALTY_VALUE -gt 0 ]
do
"""
TAIL = """  
done
mkdir -p Trash && touch 1345.done
#To deletete all the old picking and run a new one, run the following commands:
#/bin/rm -rf Autopick/job*/* Extract/job*/*
"""

IMPORT_SECTION = """
  touch import.lock
  {skip_link}#LINK_CMD
  #IMPORT_CMD
  if [ $? -eq 0 ];then
    echo '++++++++++++++++++++++++++++'
    /bin/rm import.lock
    sleep {time}
  else
    echo -e "\\033[1;31mFailed at Import Step...\\033[0m"
    /bin/rm import.lock
    exit -1
  fi
"""


MC_SECTION = """
  touch mc.lock
  #MC_CMD
  if [ $? -eq 0 ];then
    echo '++++++++++++++++++++++++++++'
    /bin/rm mc.lock
    sleep {time}
  else
    echo -e "\\033[1;31mFailed at Motion Correction Step...\\033[0m"
    /bin/rm mc.lock
    exit -1
  fi
"""

CTF_SECTION = """
  touch ctf.lock 
  #CTF_CMD
  if [ $? -eq 0 ];then
    echo '++++++++++++++++++++++++++++'
    /bin/rm ctf.lock
    sleep {time}
  else
    echo -e "\\033[1;31mFailed at Ctf Estimation Step...\\033[0m"
    /bin/rm ctf.lock
    exit -1
  fi
"""
AUTOPK_SECTION = """
  touch autopk.lock
  #ECHO_CMD
  #AUTOPK_CMD
  if [ $? -eq 0 ];then
    echo '++++++++++++++++++++++++++++'
    /bin/rm autopk.lock
    sleep {time}
  else
    echo -e "\\033[1;31mFailed at Auto-picking Step...\\033[0m"
    /bin/rm autopk.lock
    exit -1
  fi
"""


EXTRACT_SECTION = """
  touch extract.lock 
  OLD_STACK_NR=$(find Extract/{extract_job} -name "*.mrcs" | wc -l)
  /bin/rm Extract/{extract_job}/particles.star Extract/{extract_job}/particles.star.old 2>/dev/null
  #EXTRACT_CMD
  if [ $? -eq 0 ];then
    echo '++++++++++++++++++++++++++++'
    /bin/rm extract.lock
    sleep {time}
    sleep {time}
  else
    echo -e "\\033[1;31mFailed at Particle Extraction Step...\\033[0m"
    /bin/rm extract.lock
    exit -1
  fi

  NEW_STACK_NR=$(find Extract/{extract_job} -name "*.mrcs" | wc -l)
  if [ $NEW_STACK_NR -gt $OLD_STACK_NR ];then
    echo -e "\\033[1;32mNew particles imported...\\033[0m"
    PENALTY_VALUE=3
    {auto2d}submit2d
  else
    echo -e "\\033[1;33mNo new particles imported...\\033[0m"
    let PENALTY_VALUE--
  fi
  """

#bash template for collect mode with/without motion correction
#Cannot handle link problem for now
import_section = IMPORT_SECTION.replace("#IMPORT_CMD", """{import_cmd}""")
mc_section = MC_SECTION.replace("#MC_CMD", """mpirun -np {mpi} {mc_cmd}""")
ctf_section = CTF_SECTION.replace("#CTF_CMD", """mpirun -np {mpi} {ctf_cmd}""")
autopk_section = AUTOPK_SECTION.replace("#AUTOPK_CMD", """mpirun -np {mpi} {autopk_cmd}""").replace("#ECHO_CMD", """{autopk_prefix}""")
extract_section = EXTRACT_SECTION.replace("#EXTRACT_CMD", """mpirun -np 2 {extract_cmd}""")
collect_template5 = HEADER + import_section + mc_section + ctf_section + autopk_section + extract_section + TAIL
collect_template4 = HEADER + import_section + ctf_section + autopk_section + extract_section + TAIL


#bash template for auto mode with motion correction
x0 = """ln -s /net/em/frames/{session}/rawdata movies 2>/dev/null"""
x1 = """ relion_import  --do_movies  --optics_group_name "opticsGroup1" --angpix {half_apix} --kV {voltage} --Cs {cs} --Q0 0.1 --beamtilt_x 0 --beamtilt_y 0 --i "{movies}" --odir Import/job001/ --ofile movies.star --pipeline_control Import/job001/"""
x3 = """ mpirun -np {mpi} `which relion_run_motioncorr_mpi` --i Import/job001/movies.star --o MotionCorr/job002/ --first_frame_sum 1 --last_frame_sum -1 --use_motioncor2  --motioncor2_exe {motioncorr2} --other_motioncor2_args " -Tor 0.5 -Iter 7 " --gpu "" --bin_factor 2 --bfactor 250 --dose_per_frame {dose} --preexposure 0 --patch_x 7 --patch_y 5 --gainref {gain} --gain_rot 2 --gain_flip 0 --dose_weighting  --only_do_unfinished --pipeline_control MotionCorr/job002/"""
x4 = """ mpirun -np {mpi} `which relion_run_ctffind_mpi` --i MotionCorr/job002/corrected_micrographs.star --o CtfFind/job003/ --Box 512 --ResMin 30 --ResMax 5 --dFMin 5000 --dFMax 50000 --FStep 500 --dAst 100 --use_gctf --gctf_exe {gctf} --EPA --gpu "" --only_do_unfinished   --pipeline_control CtfFind/job003/"""
x5a = """mpirun -np {mpi} `which relion_autopick_mpi` --i CtfFind/job003/micrographs_ctf.star --odir AutoPick/job004/ --pickname autopick --ref {ref} --invert  --ctf  --ang 5 --shrink 0.5 --lowpass 20 --angpix {apix} --angpix_ref {ref_apix} --threshold 0.2 --min_distance 90 --max_stddev_noise 1.1 --gpu "" --only_do_unfinished   --pipeline_control AutoPick/job004/"""
x5b = """mpirun -np 8 `which relion_autopick_mpi` --i CtfFind/job003/micrographs_ctf.star --odir AutoPick/job004/ --pickname autopick --LoG  --LoG_diam_min {mind} --LoG_diam_max {maxd} --shrink 0 --lowpass 20 --LoG_adjust_threshold 1 --only_do_unfinished --pipeline_control AutoPick/job004/ """
x5x = """echo CtfFind/job003/micrographs_ctf.star > AutoPick/job004/coords_suffix_autopick.star """
x6 = """mpirun -np 2 `which relion_preprocess_mpi` --i CtfFind/job003/micrographs_ctf.star --coord_dir AutoPick/job004/ --coord_suffix _autopick.star --part_star Extract/job005/particles.star --part_dir Extract/job005/ --extract --extract_size {boxsize} --scale {half_boxsize} --norm --bg_radius {bg_radius} --white_dust -1 --black_dust -1 --invert_contrast --only_do_unfinished --pipeline_control Extract/job005/ """

import_section = IMPORT_SECTION.replace("#LINK_CMD", x0).replace("#IMPORT_CMD", x1)
mc_section = MC_SECTION.replace("#MC_CMD", x3)
ctf_section = CTF_SECTION.replace("#CTF_CMD", x4)
autopk_section_a = AUTOPK_SECTION.replace("#AUTOPK_CMD", x5a).replace("#ECHO_CMD", x5x) 
autopk_section_b = AUTOPK_SECTION.replace("#AUTOPK_CMD", x5b).replace("#ECHO_CMD", x5x)
extract_section = EXTRACT_SECTION.replace("#EXTRACT_CMD", x6)
auto_template5 = HEADER + import_section + mc_section + ctf_section + autopk_section_a + extract_section + TAIL
auto_template5_blob = HEADER + import_section + mc_section + ctf_section + autopk_section_b + extract_section + TAIL

#bash template for auto mode without motion correction
#This "DW" folder needs cannot be fixed
y0 = """mkdir -p DW && ln -s /net/em/leginon/{session}/rawdata/*DW.mrc DW/ 2>/dev/null"""
y1 = """relion_import  --do_micrographs  --optics_group_name "opticsGroup1" --angpix {apix} --kV {voltage} --Cs {cs} --Q0 0.1 --beamtilt_x 0 --beamtilt_y 0 --i "{micrographs}" --odir Import/job001/ --ofile micrographs.star --pipeline_control Import/job001/ """
y3 = """mpirun -np {mpi} `which relion_run_ctffind_mpi` --i Import/job001/micrographs.star --o CtfFind/job002/ --Box 512 --ResMin 30 --ResMax 5 --dFMin 5000 --dFMax 50000 --FStep 500 --dAst 100 --use_gctf --gctf_exe {gctf} --EPA --gpu "" --only_do_unfinished --pipeline_control CtfFind/job002/ """
y4a = """mpirun -np {mpi} `which relion_autopick_mpi` --i CtfFind/job002/micrographs_ctf.star --odir AutoPick/job003/ --pickname autopick --ref {ref} --invert  --ctf  --ang 5 --shrink 0.5 --lowpass 20 --angpix {apix} --angpix_ref {ref_apix} --threshold 0.2 --min_distance 90 --max_stddev_noise 1.1 --gpu "" --only_do_unfinished --pipeline_control AutoPick/job003/"""
y4b = """mpirun -np 8 `which relion_autopick_mpi` --i CtfFind/job002/micrographs_ctf.star --odir AutoPick/job003/ --pickname autopick --LoG  --LoG_diam_min {mind} --LoG_diam_max {maxd} --shrink 0 --lowpass 20 --LoG_adjust_threshold 1 --only_do_unfinished --pipeline_control AutoPick/job003/ """
y4y = """echo CtfFind/job002/micrographs_ctf.star > AutoPick/job003/coords_suffix_autopick.star """
y5 = """mpirun -np 2 `which relion_preprocess_mpi` --i CtfFind/job002/micrographs_ctf.star --coord_dir AutoPick/job003/ --coord_suffix _autopick.star --part_star Extract/job004/particles.star --part_dir Extract/job004/ --extract --extract_size {boxsize} --scale {half_boxsize} --norm --bg_radius {bg_radius} --white_dust -1 --black_dust -1 --invert_contrast --only_do_unfinished --pipeline_control Extract/job004/ """

import_section = IMPORT_SECTION.replace("#LINK_CMD", y0).replace("#IMPORT_CMD", y1)
ctf_section = CTF_SECTION.replace("#CTF_CMD", y3)
autopk_section_a = AUTOPK_SECTION.replace("#AUTOPK_CMD", y4a).replace("#ECHO_CMD", y4y)
autopk_section_b = AUTOPK_SECTION.replace("#AUTOPK_CMD", y4b).replace("#ECHO_CMD", y4y)
extract_section = EXTRACT_SECTION.replace("#EXTRACT_CMD", y5)
auto_template4 = HEADER + import_section + ctf_section + autopk_section_a + extract_section + TAIL
auto_template4_blob = HEADER + import_section + ctf_section + autopk_section_b + extract_section + TAIL

#RELION schedule command
relion_pipeliner_cmd5 = """relion_pipeliner --addJob Import && relion_pipeliner --addJob MotionCorr --addJobOptions 'Input movies STAR file: == Import/job001/movies.star' && relion_pipeliner --addJob CtfFind --addJobOptions 'Input micrographs STAR file: == MotionCorr/job002/corrected_micrographs.star;Use Gctf instead? == Yes' && relion_pipeliner --addJob AutoPick --addJobOptions 'Input micrographs for autopick: == CtfFind/job003/micrographs_ctf.star.star;2D references: == ref.mrcs' && relion_pipeliner --addJob Extract --addJobOptions 'Input coordinates:  == AutoPick/job004/coords_suffix_autopick.star;micrograph STAR file:  == CtfFind/job003/micrographs_ctf.star'"""
relion_pipeliner_cmd4 = """relion_pipeliner --addJob Import && relion_pipeliner --addJob CtfFind --addJobOptions 'Input micrographs STAR file: == Import/job001/micrographs.star;Use Gctf instead? == Yes' && relion_pipeliner --addJob AutoPick --addJobOptions 'Input micrographs for autopick: == CtfFind/job002/micrographs_ctf.star;2D references: == ref.mrcs' && relion_pipeliner --addJob Extract --addJobOptions 'Input coordinates:  == AutoPick/job003/coords_suffix_autopick.star;micrograph STAR file:  == CtfFind/job002/micrographs_ctf.star'"""

#Provide common parameter when start a new relion project 
relion_gui_parameters = {}
relion_gui_parameters["movie_import"] = "Input files: == {movies}\nNode type: == 2D micrograph movies (*.mrcs, *.tiff)"
relion_gui_parameters["image_import"] = "Input files: == {micrographs}\nNode type: == 2D micrographs/tomograms (*.mrc)"
relion_gui_parameters["mc"] = """Pixel size (A): == {half_apix}
Bfactor: == 250
Binning factor: == 2
Do dose-weighting? == Yes
Use RELION's own implementation? == No
Dose per frame (e/A2): == {dose}
Gain-reference image: == {gain}
MOTIONCOR2 executable: == {motioncorr2}
Gain rotation: == 90 degrees (1)
Input movies STAR file: == Import/job001/movies.star
Other MOTIONCOR2 arguments == -Tor 0.5 -Iter 7
Number of patches X: == 7
Number of patches Y: == 5
Number of GPUs == 4
Voltage (kV): == {voltage}"""

relion_gui_parameters["gctf"]="""Magnified pixel size (Angstrom): == {apix}
Spherical aberration (mm): == 2.7
Perform equi-phase averaging? == Yes
Ignore 'Searches' parameters? == No
Gctf executable: == {gctf}
Input micrographs STAR file: == MotionCorr/job002/corrected_micrographs.star
Voltage (kV): == {voltage}
Amplitude contrast: == 0.1
Use CTFFIND-4.1? == No
Use Gctf instead? == Yes
Use micrograph without dose-weighting? == No"""

relion_gui_parameters["autopick"] = """Pixel size in micrographs (A) == {apix}
Pixel size in references (A) == {ref_apix}
Input micrographs for autopick: == CtfFind/job003/micrographs_ctf.star
2D references: == {pick_template}
Minimum inter-particle distance (A): == 90
Number of MPI procs: == {mpi}
Number of GPUs == 4
Shrink factor: == 0.5
Picking threshold: == 0.2
Use GPU acceleration? == Yes"""

relion_gui_parameters["extract"] = """Pixel size (A) == {apix}
Input coordinates:  == AutoPick/job004/coords_suffix_autopick.star
Rescale particles? == Yes
Particle box size (pix): == {boxsize}
Number of MPI procs: == {mpi}
Re-scaled size (pixels):  == {boxsize / 2}
micrograph STAR file:  == CtfFind/job003/micrographs_ctf.star
"""

relion_gui_parameters["manpick"] = """
# version 30001

data_job

_rlnJobType                             3
_rlnJobIsContinue                       0
 

# version 30001

data_joboptions_values

loop_ 
_rlnJobOptionVariable #1 
_rlnJobOptionValue #2 
    angpix         -1 
 black_val          0 
blue_value          0 
color_label rlnParticleSelectZScore 
  ctfscale          1 
  diameter         10 
  do_color         No 
  do_queue         No 
do_startend         No 
  fn_color         "" 
     fn_in CtfFind/job002/micrographs_ctf.star 
  highpass         -1 
   lowpass         20 
  micscale        0.1 
min_dedicated          0 
other_args         "" 
      qsub     sbatch 
qsub_extra1 0-12:00:00 
qsub_extra2         30 
qsub_extra3          1 
qsub_extra4         "" 
qsubscript /apps/relion/slurm-template.sh 
 queuename  chang-gpu 
 red_value          2 
sigma_contrast          3 
 white_val          0 
 
"""
