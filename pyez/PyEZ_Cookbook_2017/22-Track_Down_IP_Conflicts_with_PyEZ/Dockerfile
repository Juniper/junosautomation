FROM python:3.6.2

# Update and install required utilities
RUN apt-get update -y && \
    apt-get install -y \
    nano \
    vim && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt /fdip/requirements.txt
RUN pip install -r /fdip/requirements.txt

WORKDIR /fdip
COPY *.py /fdip/
COPY conf /fdip/conf/
COPY data /fdip/data/
COPY pkgs /fdip/pkgs/

ENTRYPOINT ["python","main.py"]
