FROM python:3.12-alpine
WORKDIR /usr/src/app
RUN pip install --upgrade pip
COPY ./requirements.txt /usr/src/app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY ./entrypoint.sh /usr/src/app/entrypoint.sh

COPY . /usr/src/app/

ENTRYPOINT ["/usr/src/app/entrypoint.sh"]