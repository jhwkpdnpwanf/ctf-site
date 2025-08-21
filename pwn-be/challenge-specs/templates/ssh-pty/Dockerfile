FROM alpine:3.20
RUN adduser -D ctf && apk add bash
USER ctf
WORKDIR /challenge
COPY entrypoint.sh /challenge/entrypoint.sh
ENTRYPOINT ["/bin/sh","-lc","exec /challenge/entrypoint.sh"]