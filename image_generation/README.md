# Step 1: Image Generation

Images are rendered in the same fashion as in the original CLEVR dataset with one difference. We additionally create a segmentation mask for every object in the scene (for the segmentation mask each object gets assigned a unique color). These segmentation masks will be later useful to create ground truth masks and evaluate explanation methods. 

To generate the images, you need to run the singularity blender container. There is also a pre-built singularity image in the [releases](https://github.com/ahmedmagdiosman/simply-clevr-dataset/releases) of this repository for convenience. 

## 1. Singularity Image

### Pre-built


After downloading the pre-built image, either copy the image or create a symlink to `image_generation/blender-clevr.sif`:
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

You can build the image yourself using the following commands:
```bash
cd image_generation
singularity build --fakeroot --force blender-clevr.sif clevr-blender.def
```
`--fakeroot` removes the requirement to build as root and `--force` overwrites the singularity image if it already exists.

## 2. Run
Run the script `image_generation/img_gen_run.sh` to render the images. Show help with `-h`. Enable GPU rendering with `--gpu 1`.
```bash
cd image_generation
./img_gen_run.sh --outputdir $OUTPUT_DIR --numimages 10000 --gpu 0
```

### Description of the Output

* The images will be saved in `$OUTPUT_DIR/images`.
* The segmented object masks will be saved in `$OUTPUT_DIR/masks`.
* The scene structure information will be saved individually per scene in `$OUTPUT_DIR/scenes`, and aggregated in `$OUTPUT_DIR/CLEVR_scenes.json`.
* A unique mask color is assigned per scene to every object called `mask_color`.

