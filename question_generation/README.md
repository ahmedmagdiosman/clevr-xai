
# Generating Questions

To generate questions, run the script `question_generation/unique_question_gen_run.sh`. Show help with `-h`.

### Simple Questions

```bash
cd question_generation
./unique_question_gen_run.sh --input $INPUT_SCENE_FILE \
  --output $OUTPUT_FILE_FULL_PATH \
  --templatedir ./CLEVR_unique_templates
```

### Complex Questions

```bash
cd question_generation
./unique_question_gen_run.sh --input $INPUT_SCENE_FILE \
  --output $OUTPUT_FILE_FULL_PATH \
  --templatedir ./CLEVR_1.0_templates
```

This script runs a python 3.6 container at run-time since there is no need to build a separate container to generate the questions. 

You can run this script without singularity like this (untested): 


```bash
cd question_generation
python generate_questions.py --input_scene_file $INPUT_SCENE_FILE \ 
  --output_questions_file $OUTPUT_FILE_FULL_PATH \
  --template_dir CLEVR_unique_templates/
```

* `$INPUT_SCENE_FILE` is the `CLEVR_scenes.json` file generated from the image generation step.
* `$OUTPUT_FILE_FULL_PATH` is the json file where the questions will be saved.
## Description of the Output

* The questions will be generated based on the templates in `CLEVR_unique_templates` for simple questions (resp. `CLEVR_1.0_templates` for complex questions) and saved in `$OUTPUT_FILE_FULL_PATH` in JSON format.

