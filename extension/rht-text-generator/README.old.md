# RHT Text generator


1. Build the model server image:

    podman build ../.. -t rht-text-generator

2. Run the container:

    podman run --rm -ti -p 8482:8000 rht-text-generator

3. Install the extension:

    code --install-extension rht-text-generator-0.0.1.vsix