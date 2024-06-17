import os
from typing import Union
from fastapi import FastAPI
from dotenv import load_dotenv
from pydantic import BaseModel
from transformers import pipeline, set_seed, GPT2Tokenizer


load_dotenv()


MODEL_PATH = os.getenv("MODEL_PATH")
if not MODEL_PATH:
    print("MODEL_PATH env variable is required")
    exit(1)


set_seed(42)
tokenizer = GPT2Tokenizer.from_pretrained(MODEL_PATH)
generator = pipeline("text-generation", model=MODEL_PATH)
app = FastAPI()


@app.get("/")
async def predict_get(text: str, length: int = 3, no_top: bool = False):
    num_predicted_tokens = length
    no_topp = no_top

    return serve_predict_request(text, num_predicted_tokens, no_topp)


class InferencePostRequest(BaseModel):
    text: str
    length: Union[str, None] = 3


@app.post("/")
async def predict_post(body: InferencePostRequest):
    text = body.text
    num_predicted_tokens = body.length

    return serve_predict_request(text, num_predicted_tokens)


def serve_predict_request(text: str, num_predicted_tokens: int, no_topp=False):
    tokens = tokenizer(text, return_length=True)
    num_tokens = tokens["length"]
    max_length = num_tokens + num_predicted_tokens

    kargs = {"do_sample": True, "top_k": max_length, "top_p": 0.92}

    if no_topp:
        kargs = {}

    # For info about the args: https://huggingface.co/blog/how-to-generate
    predictions = generator(
        text,
        max_length=max_length,
        num_return_sequences=5,
        output_scores=True,
        return_full_text=False,
        **kargs
    )

    result = [p["generated_text"] for p in predictions]

    print("Predictions:", result)

    return result
