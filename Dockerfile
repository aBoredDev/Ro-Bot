FROM python:3.10
COPY . /
RUN pip install -r requirements.txt
WORKDIR /
VOLUME persist:/persistent
CMD ["echo", "The bot is about to start!"]
ENTRYPOINT ["python3"]
CMD ["./main.py"]
