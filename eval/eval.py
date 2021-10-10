"""
eval.py

eval.py runs the evaluation code for the Unique CLEVR dataset.
"""

import os
import glob
import argparse
import yaml
from tqdm import tqdm
import numpy as np
import util
from typing import Tuple


class UniqueCLEVREvaluator():
    """
    A class to evaluate performant of saliency and relevance methods on Unique CLEVR.
    Usage:
        1. Instantiate the class
        2. Call evaluate()
        3. Call get_overall_accuracy()
    """

    def __init__(self, args: dict):
        """
        Initialize an instance of the Unique CLEVR Evaluator class.

        Parameters
        ---
        args (dict)
            Args with required information to evaluate the relevance performance on Uniqe CLEVR.
        """
        self.args = args
        self.predictions = util.load_json(self.args["pred_file"])
        self.questions = util.load_json(self.args["question_file"])["questions"]
        self.accuracy = None
        self.ground_truth = {}
        self.ground_truth_stats = {}
        self.ground_truth_precomputed = self._try_load_ground_truth()
        self.target_all = self.args["target_all"]
        self.filters = self.args["filters"]

    def _try_load_ground_truth(self) -> bool:
        """
        Tries to load the ground truth from disk. If found returns true and loads
        it to self.ground_truth. Otherwise returns false.

        Result
        ---
        bool
        """
        gt_path = self.args["ground_truth_path"]
        single = util.is_numpy_file(gt_path)

        if single:
            try:
                self.ground_truth = np.load(gt_path, allow_pickle=True)[()]
            except FileNotFoundError:
                return False
        else:
            files = glob.glob(os.path.join(gt_path, "*.npy"))
            if not files:
                return False
            for file in files:
                idx = os.path.splitext(os.path.basename(file))[0]
                self.ground_truth[int(idx)] = np.load(file)

        return True

    def _calc_ground_truth_stats(self) -> None:
        """
        Calculates ground truth statistics. Currently only computes the size of the
        ground truth object. Only compatible with simple-questions!
        """
        stats = {}


        print("Calculating stats...")
        for ques in tqdm(self.questions, total=len(self.questions)):
            ques_id = ques["question_index"]
            program = ques["program"]
            scene = util.load_json(self.args["scenes_path"] + ques["image"] +
                               ".json")
            objects = scene["objects"]

            # get target object
            target_objects = []
            target_objects_indices = []
            # find the last filter_* function which has output==index of target objects
            for func in reversed(program):
                if func["type"].startswith("filter_"):
                    target_objects_indices = func["_output"]
                    target_objects = [objects[i] for i in target_objects_indices]
                    break

            if len(target_objects) == 0:
                print(
                "No target objects found, skipping this question (qid:%d)..." %
                (ques_id))
            elif len(target_objects) > 1:
                print(
                "More than 1 target object found, check this question (qid:%d)..." %
                (ques_id))



            stats[ques_id] = target_objects[0]["size"]


        gt_path = self.args["ground_truth_path"]
        stats_file_path = os.path.join(gt_path,"gt_stats.json")
        util.save_json(stats, stats_file_path)


    def save_ground_truth(self, save_stats: bool = True) -> None:
        """
        Saves the ground truths to disk. If the ground truth path has a npy extension,
        all ground truths are saved in a single file. Otherwise, it's saved in a directory
        with file corresponding to a single question with name == question_index.npy


        Parameters
        ---
        save_stats (bool)
            Saves ground truth statistics to disk (JSON).

        Result
        ---
        None
        """
        gt_path = self.args["ground_truth_path"]

        single = util.is_numpy_file(gt_path)

        if single:
            # save as single file
            np.save(gt_path, self.ground_truth)
        else:
            # save as multiple individual files
            if not os.path.exists(gt_path):
                os.makedirs(gt_path)
            for key in self.ground_truth.keys():
                file_path = os.path.join(gt_path, str(key) + ".npy")
                np.save(file_path, self.ground_truth[key])

        if save_stats:
            stats_file_path = os.path.join(
                gt_path,
                util.strip_special_chars(str(self.filters)) + "_stats.json")
            util.save_json(self.ground_truth_stats, stats_file_path)

    def calculate_ground_truth(self, question: dict) -> Tuple[np.ndarray, dict]:
        """
        Calculatest he ground truth map for a single question.

        Parameters
        ---
        question (dict)
            The question dict containing info about the question.
        
        Result
        ---
        np.ndarray
            Ground truth boolean array of shape HxW
        dict
            Ground truth statistics. Currently only return number
            of target objects and total number of objects in the scene.
        """
        scene = util.load_json(self.args["scenes_path"] + question["image"] +
                               ".json")
        if self.target_all:
            target_objects, target_objects_indices = scene["objects"], [
                i for i in range(len(scene["objects"]))
            ]
        else:
            target_objects, target_objects_indices = util.get_target_objects(
                scene["objects"], question["program"], filters=self.filters)
        # Skip questions where there's no target object, ie for exist and count
        # questions with answer False or 0
        if len(target_objects) == 0:
            print(
                "No target objects found, skipping this question (qid:%d)..." %
                (question["question_index"]))
            return None, None

        # load ground truth mask
        mask_img_path = self.args["masks_path"] + question["image"] + ".png"
        mask_img = util.load_image_as_arr(mask_img_path)
        # get mask colors
        mask_colors = util.get_mask_colors(scene)
        # background color
        bg_color = np.asarray(self.args["background_color"])

        unique_colors, mapping = util.preprocess_mask_img(
            mask_img, mask_colors, bg_color)

        target_colors = [
            unique_colors[mapping[i]] for i in target_objects_indices
        ]

        # Calculate ground truth as bool array
        # Ignore alpha channel
        ground_truth_shape = mask_img.shape[0:2]
        ground_truth = np.full(ground_truth_shape, False, dtype=bool)
        for target_color in target_colors:
            # Compare target color RGB val against mask img RGB vals
            target_mask = np.all(mask_img == target_color, axis=-1)
            # Add to current ground truth
            ground_truth = np.logical_or(ground_truth, target_mask)

        ground_truth_stats = {
            "target_objects": len(target_objects),
            "total_objects": len(scene["objects"])
        }
        return ground_truth, ground_truth_stats

    def calculate_all_ground_truths(self) -> None:
        """
        Calculates the ground truths for all questions in the dataset.

        Result
        ---
        None
        """
        if self.ground_truth_precomputed:
            exit("Existing ground truth found at %s, exiting..." %
                 self.args["ground_truth_path"])

        print("Calculating all ground truths...")
        for ques in tqdm(self.questions, total=len(self.questions)):
            ques_id = ques["question_index"]
            ground_truth, ground_truth_stats = self.calculate_ground_truth(ques)
            if ground_truth is None:
                continue
            if "heatmap_shape" in self.args:
                resize_shape = self.args["heatmap_shape"]
                ground_truth = util.resize_ground_truth(ground_truth,
                                                        resize_shape)

            self.ground_truth[ques_id] = ground_truth
            self.ground_truth_stats[ques_id] = ground_truth_stats

    def eval_single(self, prediction: dict, question: dict) -> float:
        """
        Evaluates performance on a single heatmap-answer pair.


        Parameters
        ---
        prediction (dict)
            Prediction dictionary containing the question index which is used to load the
            heatmap for this question.
        question (dict)
            Question dictionary item from that is generated from the CLEVR generated questions.
            (Ground truth)

        Result
        ---
        float
            Accuracy [0,1]. Ratio of the relevance values overlapping with the ground truth
            over all relevance.
        """

        heatmap = util.load_heatmap(self.args["heatmap_path"] +
                                    str(prediction["question_index"]) + ".npy")
        # Get ground truth if it's already computed.
        if question["question_index"] in self.ground_truth:
            ground_truth = self.ground_truth[question["question_index"]]
        else:
            ground_truth, _ = self.calculate_ground_truth(question)
            if not ground_truth:
                return -1
            if "heatmap_shape" in self.args:
                resize_shape = self.args["heatmap_shape"]
            else:
                resize_shape = heatmap.shape
            ground_truth = util.resize_ground_truth(ground_truth, resize_shape)
            self.ground_truth[question["question_index"]] = ground_truth

        acc = util.calc_overlap(ground_truth, heatmap)

        return acc

    def evaluate(self) -> None:
        """
        Evaluate relevance on Unique CLEVR.

        Algorithm:
         1. Loop over each question heatmap
         2. If answer is correct, continue
         3. Get object color mapping since blender saves colors in sRGB. (sRGB -> RGB)
         4. Filter out irrelevant object mask colors.
         5. Get ground truth bool array where (x,y)==True if pixel lies in relevant object
         6. Count how many pixels from heatmap overlap with true ground truth
         7. Sum values at those pixels -> rel_true
         8. Calculate metric -> acc = rel_true/total_rel


        Result
        ---
        None
        """

        if not self.predictions:
            exit("Predictions were not loaded. Can not evaluate. Exiting...")
        self.accuracy = []
        print("Evaluating...")
        for pred in tqdm(self.predictions, total=len(self.predictions)):
            ques_id = pred["question_index"]
            question = [
                q for q in self.questions if q["question_index"] == ques_id
            ][0]
            if pred["answer"] == question["answer"]:
                acc = self.eval_single(pred, question)
                if acc >= 0:
                    self.accuracy.append(acc)

    def get_overall_accuracy(self) -> np.float64:
        """
        Returns the mean accuracy over the whole dataset.

        Result
        ---
        np.float64
            Mean accuracy.
        """
        try:
            mean_acc = np.mean(self.accuracy)
        except TypeError:
            print(
                "Accuracy not computed yet. Call evaluate() to compute accuracy."
            )
            return None
        return mean_acc


def _debug_draw_ground_truth(filepath: str):
    """
    Draw ground truth npy bool array. DEBUG function

    Parameters
    ---
    filepath (str)
        ground truth file path
    """

    import matplotlib.pyplot as plt

    ground_truth = np.load(filepath)
    plt.subplot(111)
    plt.imshow(ground_truth, cmap='hot', interpolation='nearest')

    plt.savefig("gt.png")


def run():
    """
    Main function call.
    """
    parser = argparse.ArgumentParser(
        description=
        "Evaluate accuracy of saliency/relevance maps on Unique CLEVR.")
    parser.add_argument("--config",
                        type=str,
                        default=None,
                        required=True,
                        help="config yaml file")
    parser.add_argument(
        "--no-evaluate",
        default=False,
        required=False,
        action="store_true",
        help="Doesn't evaluate heatmaps and only computes ground truths.")

    parser.add_argument(
        "--gt-stats",
        default=False,
        required=False,
        action="store_true",
        help="Only compute GT statistics")
    cmd_args = parser.parse_args()

    config_file = cmd_args.config
    try:
        with open(config_file) as file:
            args = yaml.safe_load(file)
    except FileNotFoundError:
        exit("Config file not found! Please provide a valid config file path.")

    unique_clevr_evaluator = UniqueCLEVREvaluator(args)

    if cmd_args.no_evaluate:
        unique_clevr_evaluator.calculate_all_ground_truths()
    elif cmd_args.gt_stats:
        unique_clevr_evaluator._calc_ground_truth_stats()
    else:
        unique_clevr_evaluator.evaluate()
        print("Overall accuracy: ",
              unique_clevr_evaluator.get_overall_accuracy())

    if not unique_clevr_evaluator.ground_truth_precomputed:
        unique_clevr_evaluator.save_ground_truth(save_stats=True)


if __name__ == "__main__":
    run()
