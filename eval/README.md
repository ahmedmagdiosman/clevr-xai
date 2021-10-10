# Ground Truth Generation and Evaluation

To generate the ground truth masks and evaluate your explanation method, you can run the eval container. There is also a pre-built image in the releases section for convenience. 

Currently the heatmap evaluation code is packaged separately from this directory as a Github [gist](https://gist.github.com/ArrasL/0bc02ef98e369f861aec40145a58e356) (in the future we plan to integrate the evaluation process in the present directory).

**Alternatively, you can run the ground truth generation and evaluation code without a container. We supply the [requirements.txt](https://github.com/ahmedmagdiosman/simply-clevr-dataset/blob/master/eval/requirements.txt) so you can build a virtualenv with it. Make sure to adjust the paths in `eval/config.yaml` respectively.**


## 1. Singularity Image

### Pre-built


After downloading the image, either copy the image or create a symlink to `eval/eval-unique-clevr.sif`:

```bash
cd eval/
cp $SINGULARITY_IMAGE_LOCATION/eval-unique-clevr.sif eval-unique-clevr.sif
######
# OR #
######
cd eval/
ln -s $SINGULARITY_IMAGE_LOCATION/eval-unique-clevr.sif eval-unique-clevr.sif
```


### Build

You can build the image using the following commands:
```bash
cd eval/
singularity build --fakeroot --force eval-unique-clevr.sif eval-unique-clevr.def
```
`--fakeroot` removes the requirement to build as root and `--force` overwrites the singularity image if it already exists.


## 2. Ground Truth Masks Generation

After obtaining a singularity image, you can generate the ground truth masks without any prediction data, you can do so by adding the `--no-evaluate` flag:

```bash
cd eval/
./eval_unique_clevr.sh --datadir $DATADIR --config $CONFIG --sif eval-unique-clevr.sif --no-evaluate
```

`$DATADIR` specifies the data directory containing all required data: 
* Masks directory: The object segmentation`masks` generated from Step 1: Generating Images.
* CLEVR_scenes.json: The scene structure information generated from Step 1: Generating Images.
* CLEVR_questions.json: The questions JSON file generated from Step 2: Generating Questions.

`$CONFIG` specifies a config file to supply the evaluation code with needed arguments. The default config file can be found [here](config.yaml).
**The paths are related to the singularity container not your host machine!**

The `--sif` parameter is optional. It points the script to the location of the singularity sif file. By default, it is expected to be in `eval/eval-unique-clevr.sif`.

### Description of the Output

* The ground truth masks will be saved as numpy arrays in `$DATADIR/ground_truth`. Please check the [config.yaml](config.yaml) to save the ground truth masks either in separate files or concatenated in one single file.


### Generating the all-objects ground truth

In the `config.yaml`, change `target_all` to true and re-run the above script to generate the all-objects ground truths.
Otherwise per default the one-object ground truth masks will be generated.

### Generating a different sized ground truth
The ground truths masks we provide in our *simply*-CLEVR dataset map the Relation Network model's input image dimensions (i.e. the masks are resized to 128x128).
If the model/heatmaps you are evaluating have a different size, you can generate the appropriate ground truth by changing the `heatmap_shape` option in `config.yaml` and re-run the ground truth generation script above.


## 3. Heatmap Evaluation


**Currently the heatmap evaluation code is packaged separately from this repo as a Github [gist](https://gist.github.com/ArrasL/0bc02ef98e369f861aec40145a58e356). Do not follow the steps below. (We will automatize the evaluation process and integrate it here in the future)**

Once you have some heatmaps and model predictions you'd like to evaluate, run the script `eval/eval_unique_clevr.sh`. Show help with `-h`.

```bash
cd eval
./eval_unique_clevr.sh --datadir $DATADIR --config $CONFIG --sif eval-unique-clevr.sif
```

`$DATADIR` specifies the data directory containing all required data: 
* Masks directory: The object segmentation`masks` generated from Step 1: Generating Images.
* CLEVR_scenes.json: The scene structure information generated from Step 1: Generating Images.
* CLEVR_questions.json: The questions JSON file generated from Step 2: Generating Questions.
* Heatmaps directory: `heatmaps` directory containing the numpy arrays generated from your interpretability method. Files should be saved with `name == question id`. Files are expected to be pure numpy 2D arrays with the same x,y dimensions as the input images.
* Predictions directory: `predictions` directory containing the predictions made by your models. Each model's prediction should be saved in a single file as a list of dicts.
    - Example: `[{"answer":1, "question_index": 0},{"answer": "cylinder", "question_index": 1}]`

`$CONFIG` specifies a config file to supply the evaluation code with needed arguments. The default config file can be found [here](https://github.com/ahmedmagdiosman/simply-clevr-dataset/blob/master/eval/config.yaml). **The paths are related to the singularity container not your host machine!**

The `--sif` parameter is optional. It points the script to the location of the singularity sif file. By default, it is expected to be in `eval/eval-unique-clevr.sif`.

## 4. Extra

Calculate ground truth size in pixels.

```bash
python3 eval.py --config $CONFIG --gt-stats
```
