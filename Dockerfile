#echo $CR_PAT | docker login ghcr.io -u jariperttunen --password-stdin
#docker build . --tag ghcr.io/jariperttunen/lukeghg:latest
#docker push ghcr.io/jariperttunen/lukeghg:latest     
FROM python:3.9

WORKDIR /lukeghg
ENV VIRTUAL_ENV=/venv
RUN python3 -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"
RUN python3 -m pip install --upgrade pip
RUN python3 -m pip install --upgrade setuptools wheel

COPY . /lukeghg/

RUN cd  /lukeghg/lukeghg && python3 setup.py bdist_wheel
RUN cd  /lukeghg/lukeghg && python3 -m pip install --upgrade dist/lukeghg-1.0-py3-none-any.whl
LABEL org.opencontainers.image.source="https://github.com/jariperttunen/docker-lukeghg"
ENTRYPOINT ["/bin/bash","-l","-c"]
CMD ["ls"]

