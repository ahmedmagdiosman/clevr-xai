# Generating Images

Images are rendered in the same fashion as the original dataset with one difference. We add a unique mask for every object to be able to measure the overlap with explanation methods. 

To generate the images, you need to run the singularity blender container. There's a prebuilt image in the releases page for convenience. 

## Singularity Image

### Pre-built


After downloading the image, either copy the image or create a symlink to `image_generation/blender-clevr.sif`:
```bash
cd image_generation
cp $SINGULARITY_IMAGE_LOCATION/blender-clevr.sif blender-clevr.sif
######
# OR #
######
cd image_generation
ln -s $SINGULARITY_IMAGE_LOCATION/blender-clevr.sif blender-clevr.sif
```

### Build

You can build the image using the following commands:
```bash
cd image_generation
singularity build --fakeroot --force blender-clevr.sif clevr-blender.def
```
`--fakeroot` removes the requirement to build as root and `--force` overwrites the singularity image save file name if it already exists.

## Run
Run the script `image_generation/img_gen_run.sh` to render the images. Show help with `-h`. Enable GPU rendering with `--gpu 1`.
```bash
cd image_generation
./img_gen_run.sh --outputdir $OUTPUT_DIR --numimages 10000 --gpu 0
```

### Description of the Output

* The images will be saved in `$OUTPUT_DIR/images`, the segmented object masks will be saved in `OUTPUT_DIR/masks`. Scene
* Scene structure information will be saved individiually per scene in `OUTPUT_DIR/scenes`, and aggregated in `$OUTPUT_DIR/CLEVR_scenes.json`
* A unique mask color is assigned per scene to every object called `mask_color`.

