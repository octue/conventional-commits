FROM python:3.10.7-slim

RUN pip3 install git+https://github.com/octue/conventional-commits.git@0.8.0

COPY entrypoint.sh /entrypoint.sh

RUN chmod +x entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]
