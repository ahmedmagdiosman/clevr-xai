#!/bin/bash
singularity exec --nv  \
	  -B $PWD:/code -B img-gen-mount:/data  \
	  --pwd /code/image_generation	\
	  blender-clevr.sif bash 
