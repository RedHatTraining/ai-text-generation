import argparse
import torch
from train import predict
from model import Model
from dataset import Dataset


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--max-epochs", type=int, default=1)
    parser.add_argument("--batch-size", type=int, default=1000)
    parser.add_argument("--sequence-length", type=int, default=5)
    args = parser.parse_args()
    dataset = Dataset(args)
    model = Model(dataset)
    model.load_state_dict(torch.load("model.torch"))
    model.eval()

    print(predict(dataset, model, text="define tests by"))