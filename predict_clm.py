from transformers import pipeline, set_seed

TEXT = "=== Identifying the Need"
wordcount = len(TEXT.split())

# generator = pipeline('text-generation', model='gpt2')
generator = pipeline('text-generation', model='.output/')
set_seed(42)
predictions = generator("Correct any reported",
                        max_length=wordcount + 3, num_return_sequences=5)

for p in predictions:
    print()
    print("-" * 100)
    print(p["generated_text"])
    print("-" * 100)
    print()
