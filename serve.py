from sanic import Sanic
from sanic.response import json
from transformers import pipeline, set_seed, AutoTokenizer


set_seed(42)
tokenizer = AutoTokenizer.from_pretrained('.model')
generator = pipeline('text-generation', model='.model')


app = Sanic("PTL-writing-assistant")


@app.route("/")
async def test(request):
    text = request.args.get("text", "")
    num_predicted_tokens = int(request.args.get("length", 3))
    no_topp = request.args.get("no_top", False)

    tokens = tokenizer(text, return_length=True)
    num_tokens = tokens["length"][0]
    max_length = num_tokens + num_predicted_tokens

    kargs = {
        "do_sample": True,
        "top_k": max_length,
        "top_p": 0.92
    }

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

    return json(result)

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8482)
