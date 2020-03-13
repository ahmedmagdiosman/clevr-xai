# Ground Truth Generation and Evaluation

To generate the ground truths and evaluate your method, you can run the eval container. There's a prebuilt image in the releases page for convenience. 
Currently the evaluation code used is packaged seperately from this directory and is included with the RN-network code.

**Alternatively, you can run the ground truth generation and evaluation code without a container. We supply the [requirements.txt](eval/requirements.txt) so you can build a virtualenv with it. Make sure to adjust the paths in `eval/config.yaml` respectively.**


## Singularity Image

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
`--fakeroot` removes the requirement to build as root and `--force` overwrites the singularity image save file name if it already exists.


## Ground Truth Generation

After obtaining a singularity image, you can generate the ground truths without any prediction data, you can do so by adding the `--no-evaluate` flag:

```bash
cd eval/
./eval_unique_clevr.sh --datadir $DATADIR --config $CONFIG --sif eval-unique-clevr.sif --no-evaluate
```

`$DATADIR` specifies the data directory containing all required data: 
* Masks directory: The `masks` directory generated from: Generating Images.  
* CLEVR_scenes.json: The scene structure information generated from: Generating Images.
* CLEVR_questions.json: Ground truth JSON file from: Generating Questions.

`$CONFIG` specifies a config file to supply the evaluation code with needed arguments. The default config file can be found [here](config.yaml).
**The paths are related to the singularity container not your host machine!**

The `--sif` parameter is optional. It points the script to the location of the singularity sif file. By default, it is expected to be in `eval/eval-unique-clevr.sif`.

### Description of the Output

* The ground truths will be saved as numpy arrays in `DATADIR/ground_truth`. Please check the [config.yaml](config.yaml) to save the ground truths in seperate files or in one single file.

### Different ground truths

#### Generating the all-object ground truth

* In the `config.yaml`, change `target_all` to true and re-run the above script. 

#### Generating a different sized ground truth
The ground truths provided in our dataset map the RN network's image input dimensions (128x128). If the model/heatmap you're evaluating has a different size, you can generate the appropriate ground truth by changing the `heatmap_shape` option in `config.yaml` and re-run the ground truth generation script above.


## Evaluation


**Currently the evaluation code used is packaged seperately from this repo. TODO: Add link to other repo. Do not follow the steps below.**

Once you have some heatmaps and predictions you'd like to evaluate, run the script `eval/eval_unique_clevr.sh`. Show help with `-h`.

```bash
cd eval
./eval_unique_clevr.sh --datadir $DATADIR --config $CONFIG --sif eval-unique-clevr.sif
```

`$DATADIR` specifies the data directory containing all required data: 
* Masks directory: The `masks` directory generated from step 1 (Generating Images).  
* CLEVR_scenes.json: The scene structure information generated from step 1 (Generating Images).
* CLEVR_questions.json: Ground truth JSON file from step 2 (Generating Questions).
* Heatmaps directory: `heatmaps` directory containing the numpy arrays generated from your interpretability method. Files should be saved with `name == question id`. Files are expected to be pure numpy 2D arrays with the same x,y dimensions of the input image.
* Predictions directory: `predictions` directory containing the predictions made by your models. Each model's prediction should be saved in a single file as a list of dicts.
    - Example: `[{"answer":1, "question_index": 0},{"answer": "cylinder", "question_index": 1}]`

`$CONFIG` specifies a config file to supply the evaluation code with needed arguments. The default config file can be found [here](eval/config.yaml). **The paths are related to the singularity container not your host machine!**

The `--sif` parameter is optional. It points the script to the location of the singularity sif file. By default, it is expected to be in `eval/eval-unique-clevr.sif`.

