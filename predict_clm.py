from transformers import pipeline, set_seed
from transformers import logging as transformers_logging

# Suppress warning messages
transformers_logging.set_verbosity_error()

prompt = "OpenShift AI is"
max_input_chars = 1000
wordcount = len(prompt.split())


# generator = pipeline('text-generation', model='gpt2')
generator = pipeline("text-generation", model=".model/")
set_seed(42)


def generate(text: str):
    predictions = generator(text, max_new_tokens=10, num_return_sequences=1)
    return predictions[0]["generated_text"]


print(prompt, end=None)

while True:
    input = prompt[-max_input_chars:]
    generated = generate(input)

    print(generated.replace(input, "").strip(), end=" ", flush=True)
    prompt = generated
