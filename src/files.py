# This file.py is for the moving of original files.



import shutil
from pathlib import Path

def move_file(path, status, base="data"):
    """Move a CSV out of the inbox into processed/ or rejected/."""
    folder = "processed" if status == "success" else "rejected"
    dest_dir = Path(base) / folder
    dest_dir.mkdir(parents=True, exist_ok=True)

    dest = dest_dir / Path(path).name
    shutil.move(str(path), str(dest))
    return dest

# status decides the destination folder: "success" goes to processed, anything else goes to rejected.
# mkdir(..., exist_ok=True) creates the folder if it’s missing, 
# so the function never fails because a folder doesn’t exist.
# shutil.move really moves the file, which is what the pipeline needs. 
# The inbox ends up empty, so nothing is picked up twice.