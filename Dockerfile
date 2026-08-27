#Made-with-VGX-SHIT-THINGS

FROM python:3.9-slim-buster
RUN apt-get update \
    && apt-get install -y --no-install-recommends python3-pip git \
    && rm -rf /var/lib/apt/lists/*
RUN pip3 install --upgrade pip
WORKDIR /my_project_vgx
RUN chmod 777 /my_project_vgx
RUN apt update && apt upgrade -y && apt install ffmpeg python3 python3-pip -y
COPY requirements.txt .
RUN pip3 install -r requirements.txt
COPY . .
CMD ["bash", "start.sh"] #CMD ["python3", "-m", "vgx"]
