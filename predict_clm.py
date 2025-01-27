import random
from transformers import pipeline, set_seed
from transformers import logging as transformers_logging

# Suppress warning messages
transformers_logging.set_verbosity_error()

prompt = "To list all the pods in an OpenShift project"
max_input_chars = 500
wordcount = len(prompt.split())


# generator = pipeline('text-generation', model='gpt2')
generator = pipeline(
    "text-generation", model=".model/", do_sample=True, temperature=0.8
)
set_seed(42)


def generate(text: str):
    predictions = generator(text, max_new_tokens=3, num_return_sequences=3)
    return predictions[random.choice([0, 1, 2])]["generated_text"]


print(prompt, end=None)

while True:
    input = prompt[-max_input_chars:]
    generated = generate(input)
    print(generated.replace(input, ""), end="", flush=True)
    # print(generated)
    # print("--" * 50)
    prompt = generated
