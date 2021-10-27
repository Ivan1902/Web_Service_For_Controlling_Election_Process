FROM python:3

RUN mkdir -p /opt/src/electionOfficial
WORKDIR /opt/src/electionOfficial

COPY applications/electionOfficial/application.py ./application.py
COPY applications/electionOfficial/electionOfficialDecorator.py ./electionOfficialDecorator.py
COPY applications/electionOfficial/configuration.py ./configuration.py
COPY applications/electionOfficial/models.py ./models.py
COPY applications/electionOfficial/requirements.txt ./requirements.txt

RUN pip install -r ./requirements.txt


ENV PYTHONPATH="/opt/src/electionOfficial"

# ENTRYPOINT ["echo", "hello world"]
# ENTRYPOINT ["sleep", "1200"]
ENTRYPOINT ["python", "./application.py"]