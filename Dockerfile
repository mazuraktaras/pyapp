FROM python:3.8

LABEL Author="Taras Mazurak"
LABEL E-mail="xperia.t.mazurak@gmail.com"
LABEL version="0.0.1b"

ENV PYTHONDONTWRITEBYTECODE 1
ENV FLASK_APP "uetag.py"
ENV FLASK_ENV "development"
ENV FLASK_DEBUG True

RUN mkdir /uenergo
WORKDIR /uenergo

# COPY . /uenergo

RUN pip install --upgrade pip

COPY ./requirements.txt /uenergo/requirements.txt
RUN pip install -r requirements.txt


ADD . /uenergo
EXPOSE 5000
# CMD /bin/bash
CMD flask run --host=0.0.0.0