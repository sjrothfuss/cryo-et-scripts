"""Estimate thickness of all tomos in a dir using slabify models."""

import os
import glob
import mrcfile
import numpy as np
from slabify import slabify
from plotly.subplots import make_subplots
import plotly.graph_objects as go

INPUT_DIR = r"..\..\datasets\membrain-seg-rat-synapse\raw_tomos"

results = {}

tomo_paths = glob.glob(os.path.join(INPUT_DIR, "*.rec")) + glob.glob(
    os.path.join(INPUT_DIR, "*.mrc")
)

for tomo_path in tomo_paths:
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
    flattened_values = z_projection.flatten()

    results[tomo_name] = {
        "tomo name": tomo_name,
        "bmask": bmask,
        "thickness map": z_projection,
        "flattened values": flattened_values,
        "shape": z_projection.shape,
        "min": np.min(z_projection),
        "max": np.max(z_projection),
        "mean": round(np.mean(z_projection), 2),
        "std": round(np.std(z_projection), 2),
    }

fig = make_subplots(
    rows=len(results),
    cols=2,
    subplot_titles=("Z-Projection", "Value Distribution"),
    horizontal_spacing=0.2,
)

for i, (tomo_name, metrics) in enumerate(results.items(), start=1):

    fig.add_trace(
        go.Heatmap(
            z=metrics["thickness map"],
            zmin=0,
            zmax=450,
            colorscale="viridis",
            colorbar=dict(
                x=0.45,  # Position colorbar between the two subplots
                len=0.9,  # Length of colorbar
                thickness=10,  # Thickness of colorbar
            ),
        ),
        row=i,
        col=1,
    )
    fig.update_xaxes(title_text="X", row=i, col=1)
    fig.update_yaxes(title_text="Y", row=i, col=1)

    fig.add_trace(
        go.Violin(
            y=metrics["flattened values"],
            name=tomo_name,
            box_visible=True,
        ),
        row=i,
        col=2,
    )
    fig.update_xaxes(title_text="", row=i, col=2)
    fig.update_yaxes(title_text="Thickness (nm)", range=[100, 400], row=i, col=2)

    fig.update_layout(
        title="Tomo Thickness Analysis", height=300 * len(results), showlegend=False
    )

print(results)
fig.show()
