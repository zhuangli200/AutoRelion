############################################################################
#   Written by Zhuang Li, Purdue University. Last modified at 2021-03-03   #
############################################################################
import argparse
import glob
from RelionTools import *
from TabComplete import tabComplete
from Site import site


def check_user_input(k,v):
    if k in ["voltage","eps","frames","camera_mode", "boxsize","mind","maxd"]:
        try:
            int(v)
        except ValueError:
            print_warning("You should input an integer")
            return
    if k in ["cs","exp_time", "apix","ref_apix"]:
        try:
            float(v)
        except ValueError:
            print_warning("What you provided is wrong")

    if k == "ref":
        if not glob.glob(v):
            print_warning("{} file are not found".format(k))
            return
    if k in ["motioncorr2", "gctf"]:
        if glob.glob(v):
            if subprocess.getstatusoutput(v)[0]:
                print_warning("The {} program is not executable".format(k))
                return 
        else:
            print_warning("{} file is not Found".format(k))
            return
    if k == "boxsize":
        if int(v) % 2 :
            print_warning("You should provide an even number for the boxsize. Preferred box sizes include 128, 160, 192, 256")
            return
    if k == "camera_mode":
        if v not in "12":
            print_warning("You should specifiy the mode 1 or mode 2")
            return
    return True

def update_global_parameters(args):
    comm = {}
    if args.mode == "collect":
        comm["mask_diameter"] = "-1"
    if args.run2d:
        # check if queue command is available
        comm["queue_template"] = site["queue_template"]
        comm["auto2d"] = ""
        print_info("To avoid conflict between this script and submitted 2D classification:")
        print_info("run bash script as an interactive job and submit 2D job to the queue")
    else:
        comm["auto2d"] = "#"
        comm["queue_template"] = "xxxx"

    comm["current_time"] = date.today().strftime("%b-%d-%Y")
    comm["time"] = site["defaultSleepTime"]
    comm["mpi"] = site["defaultMpiNr"]
    return comm

def update_parameters(args):
    preference = {
        "voltage":["Voltage of microscope (kV)", site["defaultVoltage"]],
        "cs":["Spheric abeeration (mm)", site["defaultCs"]],
        "eps": ["Eletron per second (from Digital Micrograph)", site["defaultEPS"]],
        "exp_time": ["Exposure time (in seconds)", site["defaultExpTime"]],
        "movies": ["Filepath of movies",site["defaultMoviePath"]],
        "frames": ["Number of movie frames", site["defaultFrameNr"]],
        "motioncorr2":["Filepath of the motioncorr2 program",site["motioncorr2_exe"]],
        "camera_mode":["Data collection mode\n(1): Counting mode\n(2): Super-resolution mode",site["defaultMode"]],
        "micrographs":["Filepath of the dose-weighted images",site["defaultMicsPath"]],
        "gctf": ["Filepath of the gctf program", site["gctf_exe"]],
        "apix":["Physical Pixel size (angstrom)", site["defaultApix"]],
        "boxsize":["==Very Important==\nEstimated box size for particle extraction (pixel)", site["defaultBoxSize"]],
        "ref":["2D stacks for particle picking", "ref.mrcs"],
        "ref_apix":["Pixel size of picking template", 2.1],
        "mind":["Minimum diameter of particles (angstrom)", 80],
        "maxd":["Maximum diameter of particles (angstrom)", 120]}

    params = {}

    if not subprocess.getstatusoutput(site["gctf_exe"])[0]:
        preference.pop("gctf")
        params["gctf"] = site["gctf_exe"]

    if args.do_motion_correction:
        preference.pop("micrographs")
        if not subprocess.getstatusoutput("ldd " + site["motioncorr2_exe"])[0]:
            preference.pop("motioncorr2")
            params["motioncorr2"] = site["motioncorr2_exe"]
    else:
        for k in ["eps", "exp_time", "movies", "frames", "motioncorr2","camera_mode"]:
            preference.pop(k)

    if args.new_sample:
        preference.pop("ref")
        preference.pop("ref_apix")
    else:
        preference.pop("mind")
        preference.pop("maxd")

    for ele in preference.keys():
        while True:
            info = "{:<40}:\033[31m{:>60}\033[0m\nOr:    ".\
                format(preference[ele][0], str(preference[ele][1]))
            user_input = tabComplete(info)
            if user_input:
                value = user_input
            else:
                value = preference[ele][1]
            if check_user_input(ele, value):
                params[ele] = value
                break
    
    if args.do_motion_correction:
        params["dose"] = round(int(params["eps"]) * float(params["exp_time"]) \
            / float(params["apix"]) / float(params["apix"]) / int(params["frames"]), 2)
        #need to double check the following codes
        params["half_apix"] = float(params["apix"]) / int(params["camera_mode"])
        params["extract_job"] = "job005"
    else:
        params["extract_job"] = "job004"
    
    params["half_boxsize"] = int(int(params["boxsize"]) / 2)
    params["bg_radius"] = int(int(params["boxsize"]) / 4 * 0.75)
    params["mask_diameter"] = int(int(params["boxsize"]) * float(params["apix"]) * 0.9 // 2 * 2)
    print_dict(params)
    return params

def ArgumentParse():
    parser = argparse.ArgumentParser(fromfile_prefix_chars='@',\
        formatter_class=argparse.RawDescriptionHelpFormatter,\
        description='\033[31mAutomatic Relion Scheduler\033[0m')
    parser.add_argument("mode", choices = ["auto","collect"], type = str, \
        help = "Required: Specify which mode you would like to run")
    parser.add_argument("--do_motion_correction", action='store_true', \
        help = "Optional: If specified, will do motion correction, otherwise will be skipped")
    parser.add_argument("--new_sample", action='store_true', \
        help = "Optional: If specified, will pick particles without templates")
    parser.add_argument("--run2d", action = 'store_true', \
        help = "Optional: If specified, will submit 2d classification to slurm queue")
    args = parser.parse_args()
    return args

if __name__ == "__main__":
    args = ArgumentParse()
    comm = update_global_parameters(args)
    version = get_relion_version()
    if version == "3.0":
        from Template30 import *
    elif version == "3.1":
        from Template31 import *
    elif version == "4.0":
        from Template40 import *
    else:
        print_error("Unsupported relion version")

    if args.mode == "auto":
        create_relion_project(version, gui = relion_gui_parameters["manpick"])
        params = update_parameters(args)
        print_info("Will schedule RELION JOBS, and generate ready-to-use bash file")
        if args.do_motion_correction:
            pipeliner = relion_pipeliner_cmd5
            bash_file = "12345.sh"
            if args.new_sample:
                template = auto_template5_blob
            else:
                template = auto_template5
        else:
            pipeliner = relion_pipeliner_cmd4
            bash_file = "1345.sh"
            if args.new_sample:
                template = auto_template4_blob
            else:
                template = auto_template4
        
        execute_relion_pipeliner(pipeliner)

        try:
            params.update(comm)
            with open(bash_file, "w") as fp:
                fp.write(template.format(**params))
            print_info("Generated bash file for auto run")
        except OSError as e:
            print_error(e)

        change_script_permission(bash_file)

    elif args.mode == 'collect':
        print_warning("Cannot handle link job for now, you need to edit the bash file mannually")
        if not is_relion_folder():
            print_error("Not in a relion folder")

        if version == "3.0":
            para_list = subprocess.getstatusoutput("relion")[1].split("\n")
            para_dict = relion_cmd_parser(para_list, sync = args.sync)
        elif version == "3.1":
            nr = int(input("Extract job nr:\n"))
            content = get_pipeline_input()
            p = get_parent_job(nr,content)
            para_dict = collect_relion_commands(nr,p)
        else:
            print_error("Unknown relion version")

        logic_check(para_dict)
        if "mc_cmd" in para_dict.keys():
            bash_file = "12345.sh"
            ct = collect_template5
        else:
            bash_file = "1345.sh"
            ct = collect_template4

        para_dict.update(comm)
        with open(bash_file, "w") as fp:
            fp.write(ct.format(**para_dict))

        change_script_permission(bash_file)

    else:
        print_error('Unknown mode')