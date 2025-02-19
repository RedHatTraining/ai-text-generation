"""
Build the dataset in fill-in-the-middle (FIM) format.

According to https://arxiv.org/pdf/2402.19173 section 5
"""

import os
import pathlib
import re
import random
from pathlib import Path


TRAIN_PATH = "data/dataset_train.txt"
VALIDATION_PATH = "data/dataset_validation.txt"


def parse_sections(f):
    sections = []
    for line in f:
        line = line.rstrip()

        if (
            line.startswith("//")
            or line.startswith("ifndef")
            or line.startswith(":experiment")
        ):
            continue

        if re.match(r"^=+ \w+", line):
            sections.append(line)
        else:
            try:
                sections[-1] += "\n" + line
            except IndexError:
                pass

    return sections


LINE_LENGTH = 20


class CurriculumSourceFile:
    repository: str
    filepath: str

    def __init__(self, filepath: str):
        self.filepath = filepath

    @property
    def short_filepath(self):
        absolute = pathlib.Path(filepath)
        return absolute.parent.name + "/" + absolute.name

    def read_lines(self):
        with open(self.filepath) as f:
            return [line.rstrip() for line in f]


def to_starcoder_format(f: CurriculumSourceFile):
    """
    Format a source file in StarCoder format
    """

    blocks = divide_blocks(f)

    processed_blocks = []
    for block in blocks:
        l = int(len(block) / 3)
        prefix = block[0:l]
        middle = block[l : 2 * l]
        suffix = block[2 * l :]

        if random.random() > 0:
            prefix = f"// {f.short_filepath}\n{prefix}"

        if random.random() > 0:
            processed = f"<fim_prefix>{prefix}<fim_suffix>{suffix}<fim_middle>{middle}"
        else:
            processed = f"{prefix}{middle}{suffix}"
        processed_blocks.append(processed)

    return processed_blocks


def divide_blocks(f: CurriculumSourceFile, lines_per_block=20):
    lines = f.read_lines()
    blocks = []
    for i in range(0, len(lines), lines_per_block):
        block = "\n".join(lines[i : i + lines_per_block])
        blocks.append(block)

    return blocks


sections = []

# Find adoc files
home = str(Path.home())
coursedir = os.environ.get("COURSE_DIR", os.path.join(home, "courses"))


for dirpath, dnames, fnames in os.walk(coursedir):
    for f in fnames:
        is_adoc = f.endswith(".adoc")
        in_content_dir = "AI264" in dirpath and "content" in dirpath and "translations" not in dirpath
        in_guides_dir = "guides" in dirpath and "en-US" in dirpath
        in_tmp = "guides/tmp" in dirpath
        in_cache = ".cache" in dirpath

        if is_adoc and in_content_dir and not in_tmp and not in_cache:
            filepath = os.path.join(dirpath, f)
            f = CurriculumSourceFile(filepath)
            sections += to_starcoder_format(f)

random.Random(42).shuffle(sections)
num_sections = len(sections)
train_size = int(num_sections * 0.8)

with open(TRAIN_PATH, "w") as f:
    f.write("\n<|endoftext|>\n".join(sections[:train_size]))

with open(VALIDATION_PATH, "w") as f:
    f.write("\n<|endoftext|>\n".join(sections[train_size:]))
