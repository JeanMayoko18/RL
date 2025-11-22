# Copyright (c) 2022-2025, The Isaac Lab Project Developers (https://github.com/isaac-sim/IsaacLab/blob/main/CONTRIBUTORS.md).
# All rights reserved.
#
# SPDX-License-Identifier: BSD-3-Clause

"""Utilities for file I/O with yaml."""

import os
import yaml
#####################################################################
import pickle
from pathlib import Path
from omegaconf import OmegaConf
#####################################################################

from isaaclab.utils import class_to_dict


def load_yaml(filename: str) -> dict:
    """Loads an input PKL file safely.

    Args:
        filename: The path to pickled file.

    Raises:
        FileNotFoundError: When the specified file does not exist.

    Returns:
        The data read from the input file.
    """
    if not os.path.exists(filename):
        raise FileNotFoundError(f"File not found: {filename}")
    with open(filename) as f:
        data = yaml.full_load(f)
    return data


def dump_yaml(filename: str, data: dict | object, sort_keys: bool = False):
    """Saves data into a YAML file safely.

    Note:
        The function creates any missing directory along the file's path.

    Args:
        filename: The path to save the file at.
        data: The data to save either a dictionary or class object.
        sort_keys: Whether to sort the keys in the output file. Defaults to False.
    """
    # check ending
    if not filename.endswith("yaml"):
        filename += ".yaml"
    # create directory
    if not os.path.exists(os.path.dirname(filename)):
        os.makedirs(os.path.dirname(filename), exist_ok=True)
    # convert data into dictionary
    if not isinstance(data, dict):
        data = class_to_dict(data)
    # save data
    with open(filename, "w") as f:
        yaml.dump(data, f, default_flow_style=False, sort_keys=sort_keys)

def dump_pickle(file_path, obj):
    """
    Save an object to a pickle file.
    Supports the order: dump_pickle(file_path, obj)

    Args:
        file_path: Path to save the pickle file.
        obj: Object to save (dict, list, class, OmegaConf, etc.)
    """
    # Convert OmegaConf objects to plain dict
    if OmegaConf.is_config(obj):
        obj = OmegaConf.to_container(obj, resolve=True)

    # Convert custom classes to dict if needed
    elif not isinstance(obj, (dict, list, tuple, str, int, float, bool)):
        try:
            obj = class_to_dict(obj)
        except Exception:
            pass  # fallback if conversion fails

    # Ensure path exists
    file_path = Path(file_path)
    file_path.parent.mkdir(parents=True, exist_ok=True)

    # Save the object
    with open(file_path, "wb") as f:
        pickle.dump(obj, f, protocol=pickle.HIGHEST_PROTOCOL)


def load_pickle(file_path, as_omegaconf: bool = False):
    """
    Load an object from a pickle file.

    Args:
        file_path: Path to the pickle file.
        as_omegaconf: If True, load the object as an OmegaConf DictConfig.

    Returns:
        Loaded object (dict, list, etc., or DictConfig if requested).
    """
    with open(file_path, "rb") as f:
        obj = pickle.load(f)

    if as_omegaconf:
        obj = OmegaConf.create(obj)

    return obj