# syntax=docker/dockerfile:1
FROM python:3.10

ENV LANG="C.UTF-8" \
    LC_LANG="C.UTF-8" \
    PYTHONDONTWRITEBYTECODE="1" \
    PYTHONUNBUFFERED="1" \
    PIP_DISABLE_PIP_VERSION_CHECK="1"

WORKDIR /code

COPY requirements.txt /code/

RUN pip install --upgrade pip

RUN pip install -r requirements.txt

RUN pip install --upgrade websockets

COPY . /code/

CMD ["uvicorn", "app.main:application", "--reload", "--host", "0:0:0:0", "--port", "8000"]
