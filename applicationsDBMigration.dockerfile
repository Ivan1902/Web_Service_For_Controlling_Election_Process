FROM python:3

RUN mkdir -p /opt/src/applications
WORKDIR /opt/src/applications

COPY applications/migrate.py ./migrate.py
COPY applications/configuration.py ./configuration.py
COPY applications/models.py ./models.py
COPY applications/requirements.txt ./requirements.txt

RUN pip install -r ./requirements.txt

# ENTRYPOINT ["echo", "hello world"]
# ENTRYPOINT ["sleep", "1200"]
ENTRYPOINT ["python", "./migrate.py"]