"""Calculate the contrast of a tomogram."""

import os
import argparse
import numpy as np
import mrcfile  # type: ignore


def _open_tomo(tomo_path: str) -> np.ndarray:
    """
    Opens a tomogram from the specified path.

    Parameters
    ----------
    tomo_path : str
        The file path to the tomogram.

    Returns
    -------
    numpy.ndarray
        The loaded tomogram.
    """
    with mrcfile.open(tomo_path, mode="r") as mrc:
        tomo = mrc.data
    return tomo  # type: ignore


def _rms_contrast(tomo: np.ndarray) -> float:
    "Calculates the root mean square (RMS) contrast of an image."
    mean_intensity = np.mean(tomo)
    return np.sqrt(np.mean((tomo - mean_intensity) ** 2))


def _michelson_contrast(tomo: np.ndarray) -> float:
    "Calculates the Michelson contrast of an image."
    min_i = np.min(tomo)
    max_i = np.max(tomo)
    return (max_i - min_i) / (max_i + min_i)


def calculate_contrast(tomo_path: str) -> dict:
    "Calculate and print the contrast of a tomogram."
    tomo = _open_tomo(tomo_path)
    tomo_name = os.path.basename(tomo_path)
    rms_contrast = _rms_contrast(tomo)
    michelson_contrast = _michelson_contrast(tomo)
    print(f"RMS Contrast: {rms_contrast:.3f}")
    print(f"Michelson Contrast: {michelson_contrast:.3f}")
    return {tomo_name: (rms_contrast, michelson_contrast)}


def cli():
    """
    Command line interface entrance point for the script.

    Accepts tomogram path from command line arguments.

    """
    parser = argparse.ArgumentParser(
        description="Calculate RMS and Michelson contrast of a tomogram."
    )
    parser.add_argument("tomo_path", help="Tomogram path")
    args = parser.parse_args()
    calculate_contrast(args.tomo_path)


if __name__ == "__main__":
    cli()
