from transformers import AutoTokenizer

model_name = "HuggingFaceTB/SmolLM-135M"
tokenizer = AutoTokenizer.from_pretrained(model_name)

# Add FIM special tokens
special_tokens = {"additional_special_tokens": ["<|fim_prefix|>", "<|fim_middle|>", "<|fim_suffix|>", "<|endoftext|>"]}
tokenizer.add_special_tokens(special_tokens)

# Save tokenizer
tokenizer.save_pretrained("./fim_smol_tokenizer")
