############################################################################
#   Written by Zhuang Li, Purdue University. Last modified at 2021-03-03   #
############################################################################
import argparse
import glob
from RelionTools import *
from TabComplete import tabComplete
from Site import site


def check_user_input(k,v):
    if k in ["gain", "ref"]:
        if not glob.glob(v):
            print_warning("{} files are not found".format(k))
            return
        #print_warning("Make sure they will be linked to current folder later")
        #if k == "gain":
        #    if not check_mc_command(movies, gain):
        #        return
    if k in ["motioncorr2", "gctf"]:
        if glob.glob(v):
            if subprocess.getstatusoutput(v)[0]:
                print_warning("The {} program is not executable".format(k))
                return True
        else:
            print_warning("{} file is not Found".format(k))
            return
    if k == "eps":
        if v < 10 or v > 40:
            print_warning("Not a good choice, something wrong?")
            return
    if k == "boxsize":
        if int(v) % 2 :
            print_warning("You should provide an even number for the boxsize")
            return
    if k == "session":
        if not re.match(r"\d{2}[a-z]{3}\d{2}[a-z]", v):
            print_warning("Invalid session name was provided")
            return
    return True

def update_global_parameters(args):
    comm = {}
    if args.mode == "collect":
        comm["mask_diameter"] = "-1"
        comm["session"] = "XXX"
    if args.run2d:
        comm["auto2d"] = ""
        print_info("To make full use of the computation resouce,")
        print_info("run bash script on aries/taurus, and submit 2D job on gemini/spindle/orion")
    else:
        comm["auto2d"] = "#"

    if args.skip_link:
        comm["skip_link"] = "#"
    else:
        comm["skip_link"] = ""
    comm["current_time"] = date.today().strftime("%b-%d-%Y")
    return comm

def update_parameters(args):
    preference = {
        "voltage":["Voltage of microscope in kv", "300"],
        "cs":["spheric abeeration in mm", 2.7],
        "eps": ["Eletron per second (from Digital Micrograph)", 20],
        "exp_time": ["Exposure time in seconds", 3.12],
        "movies": ["Filepath of movies","rawdata/*.tif"],
        "frames": ["Movie frames", 40 ],
        "gain": ["Filepath of gain reference", "rawdata/references/21jan14b_xxx_norm_0.mrc"],
        "motioncorr2":["Filepath of the motioncorr2 executable",site["motioncorr2_exe"]],
        "micrographs":["Filepath of the dose-weighted images","DW/*.mrc"],
        "gctf": ["Filepath of the gctf executable", site["gctf_exe"]],
        "apix":["Physical Pixel size in angstrom", 1.05],
        "boxsize":["Very Important one, estimated Box size for particle extraction:", 128],
        "mpi":["mpi number for parallization", 1],
        "ref":["2D stacks for particle picking", "ref.mrcs"],
        "ref_apix":["Pixel size of picking template", 2.1],
        "mind":["Minimum diameter of particles in anstrom", 80],
        "maxd":["Maximum diameter of particles in anstrom", 120],
        "time":["Sleeping time during jobs", 5],
        "session":["Session Name:", ""]}

    if args.do_motion_correction:
        preference.pop("micrographs")
    else:
        for k in ["eps", "exp_time", "movies", "frames", "gain", "motioncorr2"]:
            preference.pop(k)

    if args.new_sample:
        preference.pop("ref")
        preference.pop("ref_apix")
    else:
        preference.pop("mind")
        preference.pop("maxd")

    if args.skip_link:
        preference.pop("session")

    params = {}

    for ele in preference.keys():
        while True:
            info = "{:<50}\033[31m{:>60}\033[0m\nOr:    ".\
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
        params["dose"] = round(params["eps"] * params["exp_time"] \
            / params["apix"] / params["apix"] / params["frames"], 2)
        params["half_apix"] = float(float(params["apix"]) / 2)
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
    parser.add_argument("--skip_link", action = 'store_true', \
        help = "Optional: If specified, will skip linking files from EM-server")
    parser.add_argument("--run2d", action = 'store_true', \
        help = "Optional: If specified, will try to submit 2d classification to local slurm queue")
    args = parser.parse_args()
    return args

if __name__ == "__main__":
    args = ArgumentParse()
    comm = update_global_parameters(args)
    version = get_relion_version()
    if version == "3.1":
        from Template31 import *
    else:
        from Template30 import *

    if args.mode == "auto":
        create_relion_project(version)
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
