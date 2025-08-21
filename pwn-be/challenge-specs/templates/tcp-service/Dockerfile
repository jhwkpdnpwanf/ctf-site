FROM alpine:3.20
RUN adduser -D ctf && apk add socat
USER ctf
WORKDIR /challenge
COPY entrypoint.sh /challenge/entrypoint.sh
EXPOSE 31337
ENTRYPOINT ["/bin/sh","-lc","exec /challenge/entrypoint.sh"]