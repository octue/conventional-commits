FROM python:3.10.7-alpine

RUN apk update && apk add --no-cache curl git gcc libc-dev libffi-dev

RUN curl -L https://github.com/idc101/git-mkver/releases/download/v1.2.1/git-mkver-linux-amd64-1.2.1.tar.gz \
    | tar xvz \
    && mv git-mkver /usr/local/bin

RUN pip install git+https://github.com/octue/conventional-commits

COPY entrypoint.sh /entrypoint.sh

RUN chmod +x entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]
