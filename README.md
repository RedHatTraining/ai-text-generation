# Text Generator

AI writing assistant (prototype).

## Usage

2. Run the container:

    podman run --rm -ti -p 8482:8482 quay.io/redhattraining/ai-text-generator

3. Install the extension in VSCode

    code --install-extension extension/rht-text-generator/rht-text-generator-0.0.2.vsix

## Retrain the model

1. Build the dataset from courses:

    COURSE_DIR=... python build_dataset.py

2. Train:

    ./train

## Rebuild the model server image

    podman build . -t quay.io/redhattraining/ai-text-generator

## Publish the image

    podman push quay.io/redhattraining/ai-text-generator
