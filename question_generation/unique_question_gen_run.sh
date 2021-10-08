#!/bin/bash
# Based on https://vigitlab.fe.hhi.de/git/lrp-demo-website/blob/master/build.sh 
# load run-utils
. "$PWD/../run-utils.sh"

# A function, which prints out the help screen
function print_help() {
    echo "Runs Unique CLEVR question generation"
    echo
    echo "Usage:"
    echo "  $(basename "$0") [-h | --help] [-i | --input] [-o | --output] [-t | --templatedir]"
    echo
    echo "Options:"
    echo "  --help        | -h     Shows this help screen."
    echo "  --input       | -i     Specifies the input scene file path."
    echo "  --output      | -o     Specifies the file to save the generated questions."
    echo "  --templatedir | -t     Specifies the template directory used to generate questions. Defaults to ./CLEVR_unique_templates"

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
SHORT=-hi:o:t:                     # List all the short options
LONG=help,input:,output:,templatedir: # List all the long options

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

INPUT=""
OUTPUT=""
TEMPLATEDIR=$PWD/CLEVR_unique_templates/

dashes=0 #flag to track if we've parsed '--'
while [[ $# -gt 0 ]]; do
    case "$1" in
        -h|--help) print_help;;
        -t|--templatedir) shift
                     TEMPLATEDIR="$1";;
        -i|--input) shift
		   INPUT="$1";;
        -o|--output) shift
                   OUTPUT="$1";;
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

if [ -z "$INPUT" ]
then
      log error "No input scene file specified. Use -h to see help, exiting..."
fi

if [ -z "$OUTPUT" ]
then
      log error "No output file path specified. Use -h to see help, exiting..."
fi

if [ ! -d "$OUTPUT" ]; then
  log warning "${OUTPUT} does not exist, creating it..."
  touch $OUTPUT
fi



log info "Running question generation in python singularity container..."
singularity exec -B $INPUT:/input.json -B $OUTPUT:/output.json -B $TEMPLATEDIR:/templatedir	\
	-B $PWD:/code --pwd /code docker://python:3.6 python generate_questions.py --input_scene_file /input.json \
	--output_questions_file /output.json --template_dir /templatedir  && exit

