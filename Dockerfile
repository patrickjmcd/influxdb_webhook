FROM python:3
COPY src /opt/app

# prepare the application
RUN pip install --no-cache-dir flask influxdb
ENV FLASK_APP=/opt/app/api.py

EXPOSE 5000

CMD ["python", "-m", "flask", "run", "--host=0.0.0.0"]