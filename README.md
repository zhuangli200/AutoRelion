**Introduction:**  
This program is designed for generating a robust script for on-the-fly data processing. It combines user input and relion commands to generate a bash script for automatic pre-processing, including steps of `Import`, `Motion Correction`, `Ctf estimation`, `particle picking`, `particle extraction`, and optionally `2d classification`. Basically, it works pretty much like the cryosparc live.  
  
**Prerequisite:**  
RELION 3.0/3.1 is in your environment.  
Python 3.7 or above. Some common modules, such as argparse and glob, are needed.  
  
**Notice:**  
The program is designed for on-the-fly data processing. Therefore, it is meaningless to use this program if the data collection is finished.  It is also meaningless if the newly collected data are not readily accessed. 
  
For sake of ease of use, the program is designed in sacrifice of flexibility. For instance, user can only use motioncorr2 to do motion corrections, gctf to do ctf estimation, relion picking (with or without template) for particle picking. Also, most of not-so-important parameters are not adjustable.  
  
Since the program is designed based on the setting of Purdue cryo-EM facility, adjustment is needed to fit your local settings. A major difference among different institutions is how the movies or motion-corrected images are imported to your relion folder . For instance, the cryo-EM data can be locally accessed, while others may need  `rsync`, `globus`, or other syncing tools to transfer the newly collected data to local storage. In this case, the commands in template files need to be modified. 2D classification job is submited to job queue via `slurm`, while others may use different slurm parameters or other job queueing system. 
  

**Usage:**  
The program is designed in the two different modes which are `auto` and `collect` mode.  
  
In auto mode, the program will initiate a relion project and schedule a series of relion jobs, and generate a bash script for you to run in the terminal. While the scirpt is running in terminal, you can inspect the newest result such as accuracy of CTF estimation and particle picking in relion GUI. The auto mode works in the following scenarios:
- If you don't have a template for particle picking, and import movies to relion folder.
    `python 12345.py auto --new_sample --do_motioncorrection`
- If you don't have a template for particle picking, and import motion-corrected images to relion folder.
    `python 12345.py auto --new_sample`
- If you had a proper template for particle picking, and import movies to relion folder.
    `python 12345.py auto --do_motioncorrection`
- If you had a proper template for particle picking, and import motion-corrected images to relion folder.
    `python 12345.py auto`

- Optionally, you can ask the program to run 2d classification for you.  
    `python 12345.py auto --new_sample --do_motioncorrection --run2d`  


If you created a relion project, tuned some parameters with the early data, and would like to continue processing the upcoming data, you need the `collect` mode. The program will ask you the extraction job number with correct settings, so it can collect the commands of its parent jobs and assemble them into a ready-to-go bash script.  
In this mode, the `--new_sample` and `--do_motioncorrection` parameters are ignored, so you don't have to specify it.

Example commands:  
`python 12345.py collect`   
`python 12345.py collect --run2d`  


In both modes, depending on a motion correction job is included or not, a bash script named 1345.sh (no motion correction) or 12345.sh (with motion correction) will be generated.  