import os
import re
import random
import statistics
import numpy as np
from pathlib import Path
import matplotlib.pyplot as plt
from transformers import GPT2Tokenizer


TRAIN_PATH = "data/train/"
VALIDATION_PATH = "data/validation/"

# Find adoc files
home = str(Path.home())
coursedir = os.environ.get(
    "COURSE_DIR",
    os.path.join(home, "Desarrollo", "courses"))


lecture_pattern = re.compile(r"== \w+")
lab_pattern = re.compile(r"(^\d\) \w+)|(^== Outcomes)")


def parse_sections(filehandler, pattern):
    section = ""
    sections = []
    ignore_lines = True

    for line in filehandler:
        if (line.startswith("//")
            or line.startswith("ifndef")
                or line.startswith(":experiment")):
            continue

        if pattern.match(line):
            ignore_lines = False
            if section:
                sections.append(section)
            section = ""

        if not ignore_lines:
            section += line.rstrip(" ")

    return sections


def get_block_sizes(sections):
    tokenizer = GPT2Tokenizer.from_pretrained("gpt2")
    total = 0
    return [tokenizer(section, return_length=True)["length"]
            for section in sections]


if __name__ == "__main__":

    sections = []
    for dirpath, dnames, fnames in os.walk(coursedir):
        for f in fnames:
            if (f.endswith("content.adoc") and
                "guides" in dirpath and
                    "en-US" in dirpath):
                filepath = os.path.join(dirpath, f)

                if "zzz" in filepath:
                    continue

                print(filepath)

                with open(filepath, "r") as f:

                    if "lab-content" in filepath or "ge-content" in filepath:
                        print(filepath)
                        sections += parse_sections(f, lab_pattern)
                    else:
                        sections += parse_sections(f, lecture_pattern)

    sizes = get_block_sizes(sections)
    print("Mean block size:", statistics.mean(sizes))
    print("Median block size:", statistics.median(sizes))

    def pdf(x):
        mean = np.mean(x)
        std = np.std(x)
        y_out = 1/(std * np.sqrt(2 * np.pi)) * np.exp( - (x - mean)**2 / (2 * std**2))
        return y_out

    plt.style.use('seaborn')
    y = pdf(sizes)
    plt.figure(figsize=(6, 6))
    # plt.plot(sizes, y, color='black',
    #          linestyle='dashed')

    plt.scatter(sizes, y, marker='o', s=25, color='red')
    plt.show()

    random.Random(42).shuffle(sections)
    num_sections = len(sections)
    train_size = int(num_sections * 0.8)
    train_sections = sections[:train_size]
    validation_sections = sections[train_size:]

    import pandas as pd
    train_df = pd.DataFrame(train_sections)
    train_df.to_csv(TRAIN_PATH + "train.csv", index=False)
    valid_df = pd.DataFrame(validation_sections)
    valid_df.to_csv(VALIDATION_PATH + "validation.csv", index=False)

    for key, section in enumerate(train_sections):
        with open(TRAIN_PATH + f"section_{key}.txt", "w") as f:
            f.write(section)

    for key, section in enumerate(validation_sections):
        with open(VALIDATION_PATH + f"section_{key}.txt", "w") as f:
            f.write(section)
