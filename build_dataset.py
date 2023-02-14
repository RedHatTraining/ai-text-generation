import os
import re
import random
from pathlib import Path


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
coursedir = os.environ.get(
    "COURSE_DIR",
    os.path.join(home, "courses"))


for dirpath, dnames, fnames in os.walk(coursedir):
    for f in fnames:

        is_adoc = f.endswith(".adoc")
        in_content_dir = "content" in dirpath and "translations" not in dirpath
        in_guides_dir = "guides" in dirpath and "en-US" in dirpath
        in_tmp = "guides/tmp" in dirpath
        in_cache = ".cache" in dirpath

        if is_adoc and (in_content_dir or in_guides_dir) and not in_tmp and not in_cache:
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
