# *simply*-CLEVR Dataset

The simply-CLEVR dataset aims to provide a VQA dataset that can be use for transparent quantitative evaluation of explanation methods. The dataset consists of 10,000 images and approximately 40,000 question/answer pairs. 

You can find the dataset in the [releases](https://github.com/ahmedmagdiosman/simply-clevr-dataset/releases) section.


|Question/*Answer*   | Image   | One Object Mask  | All Objects Mask  |
|:-:|:-:|:-:|:-:|
| **What is the small yellow sphere made of?** <br> *metal*  | <img src="images/2891_original-1.png" width="256px">        |   <img src="images/2891_MASK-1.png" width="256px">  |   <img src="images/2891_MASK_ALL-1.png" width="256px">  |
| **Method**  | **LRP**  | **Integrated Gradient**  | **Gradient × Input**  | 
| *Heatmap*  |  <img src="images/2891_LRP-1.png" width="256px">   |  <img src="images/2891_IG-1.png" width="256px">   |  <img src="images/2891_GI-1.png" width="256px">   |   



## Dataset Generation

This code generates a CLEVR dataset aimed to quantitavely evaluate explanation methods. It is based on the original [CLEVR dataset](https://github.com/facebookresearch/clevr-dataset-gen/).
### Prerequisites

To minimize the amount of prerquisites, all tasks run inside containers using [Singularity](https://sylabs.io/singularity/). So this is the only requirement to run the code.
 Here's the [quick start guide](https://sylabs.io/guides/3.3/user-guide/quick_start.html).


### Step 1: Generating Images

Please refer to the README in the `image_generation` directory.

### Step 2: Generating Questions

Please refer to the README in the `question_generation` directory.

### Step 3: Generating Ground Truth and Evaluation

Please refer to the README in the `eval` directory.
