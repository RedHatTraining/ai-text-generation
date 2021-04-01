import os
from pathlib import Path
import torch
import pandas as pd
from collections import Counter

try:
    train_df = pd.read_csv("dataset.csv")
except FileNotFoundError:
    lines = []

    # Find adoc files
    home = str(Path.home())
    coursedir = os.path.join(home, "Desarrollo")

    for dirpath, dnames, fnames in os.walk(coursedir):
        for f in fnames:
            if f.endswith("-content.adoc"):
                filepath = os.path.join(dirpath, f)
                print(filepath)
                with open(filepath) as f:
                    flines = [line.lower().replace("\n", "") for line in f.readlines()]
                    lines += [f for f in flines if f]

    train_df = pd.DataFrame(lines, columns=["Text"])
    train_df.to_csv("dataset.csv")

print("Dataset read")


class Dataset(torch.utils.data.Dataset):
    def __init__(
        self,
        args,
    ):
        self.args = args
        self.words = self.load_words()
        self.uniq_words = self.get_uniq_words()
        self.index_to_word = {index: word for index, word in enumerate(self.uniq_words)}
        self.word_to_index = {word: index for index, word in enumerate(self.uniq_words)}
        self.words_indexes = [self.word_to_index[w] for w in self.words]

    def load_words(self):
        text = train_df["Text"].str.cat(sep=" ")
        return text.split(" ")

    def get_uniq_words(self):
        word_counts = Counter(self.words)
        return sorted(word_counts, key=word_counts.get, reverse=True)

    def __len__(self):
        return len(self.words_indexes) - self.args.sequence_length

    def __getitem__(self, index):
        return (
            torch.tensor(self.words_indexes[index:index+self.args.sequence_length]),
            torch.tensor(self.words_indexes[index+1:index+self.args.sequence_length+1]),
        )
