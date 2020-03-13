"""
util.py

util.py contains utility functions used for Unique CLEVR  dataset evaluation.
"""

# Add support for types within collections
# Python doesn't enforce types anyway but I think they help readability of function headers
from typing import List, Union, Tuple
import json
from PIL import Image
import numpy as np


def is_numpy_file(filepath: str) -> bool:
    """
    Helper function to check if the file extension is for npy

    Parameters
    ---
    filepath (str)
        File path

    Result
    ---
    bool
        Returns True if file path ends with the npy extension.
    """
    return filepath.endswith(".npy")


def srgb2lin(img_arr: np.ndarray) -> np.ndarray:
    """
    Convert from sRGB to Linear RGB.
    Method from reddit of all places
    https://www.reddit.com/r/blender/comments/8moqk6/rgb_node_difference_between_rgb_values/
    Another reference: https://entropymine.com/imageworsener/srgbformula/

    Parameters
    ---
    img_arr (ndarray)
        Input numpy array
    Result
    ---
    np.ndarray
        Converted array

    """

    # convert to [0,1]
    assert img_arr.all() >= 0
    img_arr = img_arr / 255

    cutoff = 0.0404482362771082
    linear_img = np.where(img_arr >= cutoff, ((img_arr + 0.055) / 1.055)**2.4,
                          img_arr / 12.92)

    return linear_img


def load_image_as_arr(filepath: str) -> np.ndarray:
    """
    Load an image as a numpy array. Also removes alpha channel
    Note: Colors saved from blender are in sRGB space.

    Parameters
    ---
    filepath (str)
        Image file path

    Result
    ---
    np.ndarray
    """

    img = Image.open(filepath)
    # Convert from PIL to numpy.
    img = np.array(img)
    # assert shape is 3D and either RGB or RGBA
    assert len(img.shape) == 3
    assert img.shape[2] == 3 or img.shape[2] == 4

    # remove alpha channel
    if img.shape[2] == 4:
        img = img[:, :, :3]

    return img


def load_json(filepath: str):
    """
    Load JSON file

    Parameters
    ---
    filepath (str)
        File path for JSON
    """
    try:
        with open(filepath) as file:
            return json.load(file)
    except FileNotFoundError:
        print("Warning: File %s was not found..." % filepath)
        return None


def get_mask_colors(scene: dict) -> List[List[float]]:
    """
    Loads the unique mask colors from the scene dictionary

    Parameters
    ---
    scene (dict)
        Scene dictionary containing info about the scene

    Result
    ---
    List[List[float]]
    """
    masks = []
    for obj in scene["objects"]:
        masks.append(obj["mask_color"])
    return masks


def preprocess_mask_img(img: np.ndarray, mask_colors: np.ndarray,
                        bg_color: np.ndarray) -> Union[np.ndarray, np.ndarray]:
    """
    Prepocessing step for a mask image to map the mask colors in the scene file to the
    actual pixel values in the mask image.

    1. Get unique colors
    2. Convert colors from sRGB to RGB
    3. Load mask colors from scene file
    4. Map the mask colors to the unique pixel values in the mask image

    Parameters
    ---
    img (np.ndarray)
        2D mask image
    mask_colors (np.ndarray)
        mask_colors for all scene objects. shape == #objects x RGB
    bg_color (np.ndarray)
        Background color RGB value. Example (64,64,64)

    Result
    ---
    Union[np.ndarray, np.ndarray]
        return 2 arrays: unique_colors, mapping
    """

    def find_nearest_index(array: np.ndarray, value: np.ndarray) -> int:
        """
        Returns index of nearest RGB value in an array compared to the given RGB value.
        We are dealing with a 2d array (num_unique x RGB) and the value
        is a 1d array (RGB values).
        Comparison done with euclidean distance.

        Parameters
        ---
        array (np.ndarray)
            2D array containing multiple unique colors (#num_unique x RGB)
        value (np.ndarray)
            1D array containg RGB values

        Result
        ---
        int
            Index of the closest value
        """

        distances = np.sqrt(np.sum((array - value)**2, axis=1))
        smallest_idx = np.where(distances == np.amin(distances))[0][0]
        return smallest_idx

    # get unique values
    unique_colors = np.unique(img.reshape(-1, img.shape[2]), axis=0)

    # remove background color
    bg_index = np.all(unique_colors == bg_color, axis=-1)
    # assert that there's only one row equivalent to the background
    assert np.count_nonzero(bg_index) == 1
    bg_index = bg_index.nonzero()[0][0]
    # remove from array
    unique_colors = np.delete(unique_colors, bg_index, axis=0)

    # convert from sRGB to linear RGB
    # The colors in the rendered images are in the sRGB space, thus when we load
    # and compare it with the mask_colors from the scenes files they would not match
    # So we need to convert the results to linear space

    unique_colors_rgb = srgb2lin(unique_colors)

    # Get mapping
    mapping = np.empty(len(mask_colors), dtype=np.uint64)
    for i, mask_color in enumerate(mask_colors):
        mapping[i] = find_nearest_index(unique_colors_rgb,
                                        np.asarray(mask_color))

    # Assert that each mapping is unique
    assert len(np.unique(mapping)) == len(mapping)

    return unique_colors, mapping


def get_target_objects(objects: List[dict],
                       program: List[dict]) -> Union[List[dict], List[int]]:
    """
    Get target objects by iterating the functional program.
    Currently we get the target objects by getting the last "filter_" program.
    This works for the current dataset but must be reviewed if we add more templates.

    Parameters
    ---
    objects (List[dict])
        Object list
    program (List[dict])
        Functional program

    Result
    ---
    Union[List[dict], List[int]]
    """
    target_objects = []
    target_objects_indices = []
    # find the last filter_* function which has output==index of target objects
    for func in reversed(program):
        if func["type"].startswith("filter_"):
            target_objects_indices = func["_output"]
            target_objects = [objects[i] for i in target_objects_indices]
            break

    return target_objects, target_objects_indices


def load_heatmap(filename: str) -> np.ndarray:
    """
    Loads heatmap from disk. Currently just loads a numpy array.

    Parameters
    ---
    filename (str)
        Heatmap File path

    Result
    ---
    np.ndarray
        Heatmap
    """
    return np.load(filename)


def resize_ground_truth(ground_truth: np.ndarray,
                        np_shape: Tuple[int, int]) -> np.ndarray:
    """
    Resize the ground truth to match the heatmap size. This is necessary because the
    heatmap shape is dependent on the the model's input preprocessing.

    Parameters
    ---
    ground_truth (np.ndarray)
        Ground truth boolean array with shape == mask_img.shape
    np_shape (Tuple[int,int])
        The target shape using numpy dimension ordering (Height x Width)

    Result
    ---
    np.ndarray
        Boolean ground truth with shape == np_shape
    """

    # No resizing needed
    if ground_truth.shape == np_shape:
        return ground_truth
    # heatmap.shape is reversed because PIL uses WxH while numpy uses HxW
    ground_truth_resized = np.array(
        Image.fromarray(ground_truth.astype(np.float64)).resize(
            reversed(np_shape), resample=Image.BILINEAR))
    # We casted the ground truth from bool to float so any interpolation values could be calculated.
    # Now we assume any value larger than 0 (interpolated) should be part of the ground truth.
    # So we set all values greater than 0 to 1 (True)
    ground_truth_resized = ground_truth_resized > 0

    return ground_truth_resized


def calc_overlap(ground_truth: np.ndarray, heatmap: np.ndarray) -> float:
    """
    Calculate overlap between the heatmap and the object masks in the mask image.

    Parameters
    ---
    ground_truth (np.ndarray)
        Ground truth boolean mask
    heatmap (np.ndarray)
        Relevance heatmap

    Result
    ---
    float
        overlap ratio
    """

    assert ground_truth.shape == heatmap.shape

    # Calculate correct relevance of heatmap where GT(x,y)==True
    correct_relevance = np.abs(heatmap[ground_truth]).sum()

    total_relevance = np.abs(heatmap).sum()

    # Return overlap of correct relevance over total relevance
    overlap = correct_relevance / total_relevance
    return overlap
