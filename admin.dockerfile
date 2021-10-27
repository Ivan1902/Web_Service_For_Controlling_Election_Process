FROM python:3

RUN mkdir -p /opt/src/admin
WORKDIR /opt/src/admin

COPY applications/admin/application.py ./application.py
COPY applications/admin/adminDecorator.py ./adminDecorator.py
COPY applications/admin/configuration.py ./configuration.py
COPY applications/admin/models.py ./models.py
COPY applications/admin/requirements.txt ./requirements.txt

RUN pip install -r ./requirements.txt


ENV PYTHONPATH="/opt/src/applications/admin"

# ENTRYPOINT ["echo", "hello world"]
# ENTRYPOINT ["sleep", "1200"]
ENTRYPOINT ["python", "./application.py"]