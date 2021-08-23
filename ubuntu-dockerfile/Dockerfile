FROM python:3

RUN python3 -m pip install --upgrade pip 
RUN wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add -
RUN sh -c 'echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google.list'
RUN apt-get -y update
RUN apt-get install -y google-chrome-stable

RUN apt-get install -yqq unzip
RUN wget -O /tmp/chromedriver.zip http://chromedriver.storage.googleapis.com/`curl -sS chromedriver.storage.googleapis.com/LATEST_RELEASE`/chromedriver_linux64.zip
RUN unzip /tmp/chromedriver.zip chromedriver -d /usr/local/bin/

RUN apt-get install -y cron
ENV DISPLAY=:99
ENV PYTHONBUFFERED 1
ENV DJANGO_SETTINGS_MODULE=search_project.settings.prod

WORKDIR /project3
ADD secrets.json /
ADD django-bootstrap-modal-forms-2.2.0 /
ADD CustomS3Boto3Storage.py /
ADD requirements.txt /
COPY . / 
RUN python /django-bootstrap-modal-forms-2.2.0/setup.py install
RUN pip3 install -r /requirements.txt

CMD ["gunicorn", "search_project.wsgi:application", "--bind", "0.0.0.0:8000"]
# CMD ["python", "manage.py", "runserver"]
EXPOSE 8000


