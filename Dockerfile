FROM registry.access.redhat.com/ubi8/python-38

COPY requirements.prod.txt .
RUN pip install --upgrade pip && \
    pip install -r requirements.prod.txt && \
    pip install torch==1.8.1+cpu -f https://download.pytorch.org/whl/torch_stable.html

COPY .model .model
COPY serve.py .

EXPOSE 8000

CMD ["python", "serve.py"]
