FROM python:3.12-slim-bullseye
LABEL description="Anonim Chat Bot"

ENV PATH="/app/:$PATH"
RUN pip install --upgrade pip
WORKDIR /app
COPY requirements.txt /app/
RUN pip install -r requirements.txt
COPY . /app/

CMD ["/bin/bash", "-c", "python main.py"]
