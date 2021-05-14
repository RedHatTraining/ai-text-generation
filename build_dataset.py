import os
import re
from pathlib import Path
import pandas as pd
import random

from sklearn.utils import validation


TRAIN_PATH = "data/dataset_train.txt"
VALIDATION_PATH = "data/dataset_validation.txt"


def parse_sections(f):
    sections = []
    for line in f:
        line = line.rstrip()

        if (line.startswith("//")
            or line.startswith("ifndef")
                or line.startswith(":experiment")):
            continue

        if re.match(r"^=+ \w+", line):
            sections.append(line)
        else:
            try:
                sections[-1] += "\n" + line
            except IndexError:
                pass

    return sections


sections = []

# Find adoc files
home = str(Path.home())
coursedir = os.path.join(home, "Desarrollo")

for dirpath, dnames, fnames in os.walk(coursedir):
    for f in fnames:
        if (f.endswith(".adoc") and
            "guides" in dirpath and
                "en-US" in dirpath):
            filepath = os.path.join(dirpath, f)
            print(filepath)
            with open(filepath, "r") as f:
                sections += parse_sections(f)

random.Random(42).shuffle(sections)
num_sections = len(sections)
train_size = int(num_sections * 0.8)

with open(TRAIN_PATH, "w") as f:
    f.write("\n".join(sections[:train_size]))

with open(VALIDATION_PATH, "w") as f:
    f.write("\n".join(sections[train_size:]))
