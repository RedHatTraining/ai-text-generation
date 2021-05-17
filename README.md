# RHT Text Generator

Tool to assist developers when writing courses.

## Usage

1. Build the model server image:

    podman build . -t rht-text-generator

2. Run the container:

    podman run --rm -ti -p 8482:8000 rht-text-generator

3. Install the extension:




## Retrain the model

1. Build the dataset from courses:

    COURSE_DIR=... python build_dataset.py

2. Train:

    ./train