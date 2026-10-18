FROM python:3.13-alpine

WORKDIR /app
COPY main.py run.sh ./
COPY syslogger ./syslogger
COPY static ./static

# run.sh may arrive with Windows line endings if the folder was copied from a PC
RUN sed -i 's/\r$//' run.sh && chmod +x run.sh

CMD ["/app/run.sh"]
