FROM python:3

RUN mkdir -p /opt/src/daemon
WORKDIR /opt/src/daemon

COPY applications/daemon/application.py ./application.py
COPY applications/daemon/configuration.py ./configuration.py
COPY applications/daemon/models.py ./models.py
COPY applications/daemon/requirements.txt ./requirements.txt

RUN pip install -r ./requirements.txt


ENV PYTHONPATH="/opt/src/electionOfficial"

# ENTRYPOINT ["echo", "hello world"]
# ENTRYPOINT ["sleep", "1200"]
ENTRYPOINT ["python", "./application.py"]