#!/bin/bash
# Based on https://vigitlab.fe.hhi.de/git/lrp-demo-website/blob/master/build.sh 
# load run-utils
. "$PWD/../run-utils.sh"

# A function, which prints out the help screen
function print_help() {
    echo "Evaluates saliency/relevance maps on Unique CLEVR"
    echo
    echo "Usage:"
    echo "  $(basename "$0") [-h | --help] [-d | --datadir] [-c | --config] [-s | --sif]"
    echo
    echo "Options:"
    echo "  --help        | -h     Shows this help screen."
    echo "  --datadir     | -d     Specifies the data directory containing all required data: CLEVR_questions.json, heatmaps dir, masks dir, predictions dir, and CLEVR_scenes.json "
    echo "  --config      | -c     Specifies the config file path"
    echo "  --sif         | -s     OPTIONAL: Specifies the singularity sif file. By default, it's assumed to be in the current directory with name eval-unique-clevr.sif"
    echo "  --no-evaluate | -n     OPTIONAL: Only generates the ground truths and saves them to disk"

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
SHORT=-hd:c:s:n                     # List all the short options
LONG=help,datadir:,config:,sif:,no-evaluate # List all the long options

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

DATADIR=""
CONFIG=""
CONTAINER=$PWD/eval-unique-clevr.sif
NOEVALUATE=""

dashes=0 #flag to track if we've parsed '--'
while [[ $# -gt 0 ]]; do
    case "$1" in
        -h|--help) print_help;;
        -s|--sif) shift
                     CONTAINER="$1";;
        -d|--datadir) shift
		   DATADIR="$1";;
        -c|--config) shift
                   CONFIG="$1";;
        -n|--no-evaluate) shift
                   NOEVALUATE="True";;
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

if [ -z "$CONFIG" ]
then
      log error "No config file specified. Use -h to see help, exiting..."
fi

if [ -z "$DATADIR" ]
then
      log error "No data directory specified. Use -h to see help, exiting..."
fi

if [ -z "$NOEVALUATE" ]
then
	log info "Running evaluation code in singularity container..."
	singularity run -B $DATADIR:/data -B $CONFIG:/config.yaml \
		$CONTAINER --config /config.yaml
else 
	log info "Running evaluation code in singularity container..."
	singularity run -B $DATADIR:/data -B $CONFIG:/config.yaml \
		$CONTAINER --config /config.yaml --no-evaluate
fi
