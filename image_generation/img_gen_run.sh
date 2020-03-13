#!/bin/bash
# load run-utils
. "$PWD/../run-utils.sh"

# A function, which prints out the help screen
function print_help() {
    echo "Runs Unique CLEVR image generation"
    echo
    echo "Usage:"
    echo "  $(basename "$0") [-h | --help] [-o | --outputdir]"
    echo
    echo "Options:"
    echo "  --help        | -h     Shows this help screen."
    echo "  --outputdir   | -o     Specifies the output directory."
    echo "  --numimages   | -n     Specifies the total number of images to render. Defaults to 10"
    echo "  --gpu         | -g     Boolean flag to use GPU rendering. 0: disabled 1: enabled. Defaults to 0."
    echo "  --split       | -s     Split name. Default: unique."

    exit 0
}

# Checks if getopt is installed and supports long options                                                                                                                                                                                                                                                                                                                                   
if ! command_exists getopt; then                                                                                                                                                                                                                                                                                                                                                            
    log error "getopt is not installed, exiting..."                                                                                                                                                                                                                                                                                                                                         
fi                                                                                                                                                                                                                                                                                                                                                                                          
getopt --test > /dev/null                                                                                                                                                                                                                                                                                                                                                                   
if [[ $? -ne 4 ]]; then                                                                                                                                                                                                                                                                                                                                                                     
    log error "getopt does not support long options, exiting..."                                                                                                                                                                                                                                                                                                                            
fi                                                                                                                                                                                                                                                                                                                                                                                          
                                                                                                                                                                                                                                                                                                                                                                                            
# Uses getopt to parse the command line arguments                                                                                                                                                                                                                                                                                                                                           
# Initialize variables
declare -a EXTRA_ARGS
declare -a POSITIONAL
DISCARD_OPTS_AFTER_DOUBLEDASH=1 # 1=Discard, 0=Save opts after -- to ${EXTRA_ARGS}


# An option followed by a single colon ':' means that it *needs* an argument.
# An option followed by double colons '::' means that its argument is optional.
# See `man getopt'.
SHORT=-ho:n:g:s:                            # List all the short options
LONG=help,outputdir:,numimages:,gpu:,split: # List all the long options

# - Temporarily store output to be able to check for errors.
# - Activate advanced mode getopt quoting e.g. via "--options".
# - Pass arguments only via   -- "$@"   to separate them correctly.
# - getopt auto-adds "--" at the end of ${PARSED}, which is then later set to
#   "$@" using the set command.
PARSED=$(getopt --options ${SHORT} \
                --longoptions ${LONG} \
                --name "$0" \
                -- "$@")         #Pass all the args to this script to getopt
if [[ $? -ne 0 ]]; then
    # e.g. $? == 1
    #  then getopt has complained about wrong arguments to stdout
    log error "The command line arguments could not be parsed, exiting..."                                                                                                                                                                                                                                                                                                              
fi
# Use eval with "$PARSED" to properly handle the quoting
# The set command sets the list of arguments equal to ${PARSED}.
eval set -- "${PARSED}"

OUTPUTDIR=""
NUMIMAGES=10
USEGPU=0
SPLITNAME="unique"

dashes=0 #flag to track if we've parsed '--'
while [[ $# -gt 0 ]]; do
    case "$1" in
        -h|--help) print_help;;
        -o|--outputdir) shift
                     OUTPUTDIR="$1";;
        -n|--numimages) shift
                     NUMIMAGES=$1;;
	-g|--gpu) shift
                     USEGPU=$1;;
	-s|--split) shift
                     SPLITNAME=$1;;
        --) dashes=1
            if [[ ${DISCARD_OPTS_AFTER_DOUBLEDASH} -eq 1 ]]; then break; fi
            ;;
        *)  #store positional arguments until we reach the dashes, then store as extra
            if [[ $dashes -eq 0 ]]; then POSITIONAL+=("$1");
            else EXTRA_ARGS+=("$1"); fi
                ;;
    esac
    shift  # Expose the next argument
done
set -- "${POSITIONAL[@]}"

if [ -z "$OUTPUTDIR" ]
then
	log error "No output directory specified. Use $(basename "$0") -h to see help, exiting..."
fi

if [ ! -d "$OUTPUTDIR" ]; then
  log warning "${OUTPUTDIR} does not exist, creating it..."
  mkdir -p $OUTPUTDIR
fi

log info "Running image generation in clevr-blender singularity container..."

singularity run --nv -B $OUTPUTDIR:/data  \
	blender-clevr.sif --use_gpu $USEGPU --num_images $NUMIMAGES \
        --output_image_dir /data/images/ --output_scene_dir /data/scenes \
	--output_scene_file /data/CLEVR_scenes.json --output_blend_dir /data/blendfiles \
	--output_mask_dir /data/masks \
	--split $SPLITNAME \
	--width=480 --height=320
