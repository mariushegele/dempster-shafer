FROM python:3.7

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
COPY data/ .

ENV PYTHON python
ENV PIP pip

CMD make
