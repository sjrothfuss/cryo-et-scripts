"""Estimate thickness of all tomos in a dir using slabify models."""

import os
import glob
import mrcfile
import numpy as np
import pandas as pd
from slabify import slabify
from plotly.subplots import make_subplots
import plotly.graph_objects as go
from calculate_contrast import run_contrast_calculations

INPUT_DIR = r"..\..\datasets\membrain-seg-rat-synapse\raw_tomos"
OUTPUT_DIR = r""
SHOW_INDIVIDUAL_PLOTS = True
MAX_THICKNESS_IN_PLOTS_NM = 500
SAVE_JSON_RESULTS = True

tomo_paths = glob.glob(os.path.join(INPUT_DIR, "*.rec")) + glob.glob(
    os.path.join(INPUT_DIR, "*.mrc")
)

n_subplot_rows = len(tomo_paths) + 1 if SHOW_INDIVIDUAL_PLOTS else 1
fig = make_subplots(
    rows=n_subplot_rows,
    cols=2,
    horizontal_spacing=0.2,
    specs=[[{"colspan": 2}, None]] + [[{}, {}]] * (n_subplot_rows - 1),
    subplot_titles=["Thickness Summary"]
    + ["Thickness Map", "Thickness Distribution"] * (n_subplot_rows - 1),
)

results = pd.DataFrame(
    index=range(len(tomo_paths)),
    columns=[
        "tomo_name",
        "min",
        "max",
        "median",
        "mean",
        "std",
        "rms_contrast",
        "michelson_contrast",
        "thickness_map",
        "flattened_values",
    ],
)

for i, tomo_path in enumerate(tomo_paths):
    tomo_name = os.path.splitext(os.path.basename(tomo_path))[0]

    with mrcfile.open(tomo_path, permissive=True) as inmrc:
        tomo = np.array(inmrc.data)
        angpix = inmrc.voxel_size.x

    bmask = slabify(
        tomo=tomo,
        points=None,  # type: ignore
        border=0,
        offset=0,
        n_samples=50000,
        boxsize=32,
        z_min=1,
        z_max=None,  # type: ignore
        iterations=5,
        simple=False,
        thickness=None,  # type: ignore
        percentile=95,
        seed=4056,
    )
    z_projection = np.sum(bmask, axis=0) * angpix / 10
    rms_contrast, michelson_contrast = run_contrast_calculations(tomo, tomo_name)

    tomo_statistics = {
        "tomo_name": tomo_name,
        "thickness_map": z_projection,
        "flattened_values": z_projection.flatten(),
        "rms_contrast": rms_contrast,
        "michelson_contrast": michelson_contrast,
        "min": z_projection.min(),
        "max": z_projection.max(),
        "mean": z_projection.mean(),
        "median": np.median(z_projection),
        "std": z_projection.std(),
    }

    for col, value in tomo_statistics.items():
        results.loc[i, col] = value

    if not SHOW_INDIVIDUAL_PLOTS:
        continue
    subplot_row = i + 2  # start on row 2
    fig.add_trace(
        go.Heatmap(
            z=tomo_statistics["thickness_map"],
            zmin=0,
            zmax=MAX_THICKNESS_IN_PLOTS_NM,
            colorscale="viridis",
            colorbar={
                "x": 0.45,  # Position colorbar between the two subplots
                "y": 0.5,  # XXX
                "len": 0.9 / n_subplot_rows,  # Length of colorbar
                "thickness": 10,
            },
        ),
        row=subplot_row,
        col=1,
    )
    fig.update_xaxes(title_text="X", row=subplot_row, col=1)
    fig.update_yaxes(title_text="Y", row=subplot_row, col=1)

    fig.add_trace(
        go.Violin(
            y=tomo_statistics["thickness_map"][0].flatten(),
            name=tomo_name,
            box_visible=True,
            showlegend=False,
        ),
        row=subplot_row,
        col=2,
    )
    fig.update_xaxes(title_text="", row=subplot_row, col=2)
    fig.update_yaxes(
        title_text="Thickness (nm)",
        range=[100, MAX_THICKNESS_IN_PLOTS_NM],
        row=subplot_row,
        col=2,
    )

if SAVE_JSON_RESULTS:
    results.to_json(os.path.join(OUTPUT_DIR, "tomo_thickness.json"), indent=2)

# Summary plot on row 1
fig.add_trace(
    go.Bar(
        x=results["tomo_name"],
        y=results["mean"].values,
        error_y={"type": "data", "array": results["std"].values},
        showlegend=False,
    ),
    row=1,
    col=1,
)
fig.update_xaxes(title_text="", row=1, col=2)
fig.update_yaxes(title_text="Mean Thickness (nm)", row=1, col=2)

fig.update_layout(
    title="Tomo Thickness Analysis",
    height=300 * n_subplot_rows,
    width=1000,
)

fig.show()
