"""A script to rename subframes in mdocs according to the frame filenames.

This script may be helpful if subframe names in .mdoc files contain
precise tilt angles (e.g. "Position_37_001[-0.04]_fractions.mrc") and the
corresponding .mrc files contain unrefined tilt angles (e.g.
"Position_37_001[0.00]_fractions.mrc"). It will use the frame ID ("001" in
the names above) to match names.

"""

import os
import glob

PATH_TO_FRAMES = "frames/"
PATH_TO_MDOCS = "rawdata/"


def get_frame_name(frame_prefix):
    "Get file name from frames that starts with the frame_id."
    matches = [frame for frame in frames if frame.startswith(frame_prefix)]
    if (n_matches := len(matches)) != 1:
        msg = (
            f"Expected 1 match for frame ID '{frame_prefix}', but found {n_matches}:\n"
            f"{matches}"
        )
        raise ValueError(msg)
    return matches[0]


frames = os.listdir(PATH_TO_FRAMES)
paths = glob.glob(PATH_TO_MDOCS + "/*.mdoc")
for path in paths:
    if path.endswith("_renamed.mdoc"):
        print("Warning! You already renamed this file:", path)
        paths.remove(path)
    with open(path, "r", encoding="utf-8") as old_mdoc:
        new_file_contents = ""
        for line in old_mdoc:
            if line.startswith("SubFramePath = "):
                subframepath = line.split("=")[1].strip()
                subframename = subframepath.split("\\")[-1]
                subframeprefix = subframename.split("[")[0]
                line = (
                    line[: line.index(subframename)]
                    + get_frame_name(subframeprefix)
                    + "\n"
                )
            new_file_contents += line
    old_path, ext = os.path.splitext(path)
    new_path = old_path + "_renamed" + ext
    with open(new_path, "w", encoding="utf-8") as new_mdoc:
        new_mdoc.write(new_file_contents)
    print("Renamed SubFrames and saved:", new_path)

for path in paths:
    old_path, ext = os.path.splitext(path)
    new_path = old_path + "_renamed" + ext
    with open(path, "r", encoding="utf-8") as file_bef:
        lines_bef = file_bef.readlines()
    with open(new_path, "r", encoding="utf-8") as file_aft:
        lines_aft = file_aft.readlines()
    for i, (line_bef, line_aft) in enumerate(zip(lines_bef, lines_aft)):
        if line_bef != line_aft:
            assert "SubFramePath = " in line_bef and "SubFramePath = " in line_aft, (
                f"Unexpected difference between {path} line {i}:"
                f"{line_bef} and {new_path} line: {line_aft}"
            )
print("Renaming complete.")
