FROM ubuntu:16.04

RUN apt-get update && \
    apt-get install -y python3-pip && \
    pip3 install keras tensorflow

COPY mnist.py .

CMD ["python3", "mnist.py"]