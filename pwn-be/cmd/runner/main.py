import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import docker
import uvicorn

import os
from dotenv import load_dotenv

def _load_env_flex():
    p = os.getenv("ENV_FILE")
    if p and os.path.exists(p):
        load_dotenv(p)
        return
    if os.path.exists(".env.local"):
        load_dotenv(".env.local")
        return
    if os.path.exists(".env"):
        load_dotenv(".env")

_load_env_flex()

app = FastAPI(title='runner')
client = docker.from_env()

class StartIn(BaseModel):
  image: str
  mode: str
  port: int | None = None

@app.post('/start')
def start(payload: StartIn):
  try:
    host_config = client.api.create_host_config(
      network_mode='none' if payload.mode != 'tcp' else 'bridge',
      mem_limit='256m',
      nano_cpus=500_000_000,
      pids_limit=128,
      read_only=True,
      cap_drop=['ALL'],
      security_opt=['no-new-privileges=true'],
    )
    cmd = ['/bin/sh', '-lc', 'exec /challenge/entrypoint.sh'] if payload.mode != 'tcp' else None
    ports = None if payload.mode != 'tcp' else {f'{payload.port}/tcp': None}
    container = client.api.create_container(
      image=payload.image,
      command=cmd,
      tty=True,
      stdin_open=True,
      host_config=host_config,
      ports=list(ports.keys()) if ports else None,
    )
    client.api.start(container=container.get('Id'))
    info = client.api.inspect_container(container.get('Id'))
    return {'container_id': info['Id'], 'ports': info.get('NetworkSettings', {}).get('Ports', {})}
  except docker.errors.DockerException as e:
    raise HTTPException(500, str(e))

class StopIn(BaseModel):
  container_id: str

@app.post('/stop')
def stop(payload: StopIn):
  try:
    client.api.stop(payload.container_id)
    client.api.remove_container(payload.container_id, force=True)
    return {'ok': True}
  except docker.errors.DockerException as e:
    raise HTTPException(500, str(e))

if __name__ == '__main__':
  uvicorn.run(app, host=os.getenv('API_HOST', '0.0.0.0'), port=int(os.getenv('API_PORT', '8081')))