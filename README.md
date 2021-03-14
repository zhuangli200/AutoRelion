**Introduction:**  
This program is designed for generating a robust script for on-the-fly data processing. It combines user input and relion commands to generate a bash script for automatic pre-processing, including steps of Import, Motion Correction, Ctf estimation, particle picking, particle extraction, and optionally 2d classification. Basically, it works pretty much like the cryosparc live.  
  
**Prerequisite:**  
RELION 3.0/3.1 is in your environment.  
Python 3.7 or above. Some common modules, such as argparse and glob, are needed.  
  
**Notice:**  
The program is designed for on-the-fly data processing, it is meaningless to use this program if you start data processing after the data collection finishes.  It is also meaningless if the newly collected data are not readilt accessed. 
  
For sake of ease of use, the program is designed in sacrifise of fexibility. For instance, user can only use motioncorr2 to do motion corrections, gctf  to do ctf estimation, relion picking(with or without template) for particle picking. Also, some parameters are not adjustable.  
  
Since the program is designed based on the setting of Purdue cryo-EM facility, adjustment needs to be done to fit your local settings. A major difference among different institutions is how the movies or motion corrected images to you relion folder are imported. For instance, the cryo-EM data can be locally accessed. While others may need  "rsync" or other syncing tools to transfer the newly collected data to local storage. In this case, the commands in template files need to be modified. 2D classiification job is submited to job queue via slurm. While others may use different slurm parameters or even "qsub" command. 
  

**Usage:**  
The program is designed in the two different modes, auto and collect mode.  
  
In auto mode, the program will initiate a relion project and create a series of jobs for you to visualize, and generate a bash script for you to run in the terminal. The auto mode works in the following scenarios:  
- If you had a template for particle picking, and want to leave the motion correction to external program  
    `python 12345.py auto`  
- If you collect on a brand new sample(therefore you don't have a template for particle picking), and want to leave the motion correction to external program.  
    `python 12345.py auto --new_sample`  
- If have a template for particle picking, and wanna do motion correction for the possible particle polishing.  
    `python 12345.py auto --do_motioncorrection`  
- If you collect on a brand new sample, and want to leave the motion correction to external program.  
    `python 12345.py auto --new_sample --do_motioncorrection`  
- Optionally, you can ask the program to run 2d classification for you.  
    `python 12345.py auto --new_sample --do_motioncorrection --run2d`  
  
If you had setup a relion project, fine tuned some parameters based on the early data, and wanna continue processing the upcoming data, you need the "collect" mode. To use the collect mode, you need to tell the program the extraction job number with  correct settings, and the program will collect all the commands of its parents and assemble them into a ready-to-go bash script.  
In this mode, the --new_sample --do_motioncorrection parameters won't work at all.  
  
`python 12345.py collect`   
`python 12345.py collect --run2d`  

In both modes, depending on a motion correction job is included or not, a bash script named 1345.sh (no motion correction) or 12345.sh (with motion correction) is generated.  