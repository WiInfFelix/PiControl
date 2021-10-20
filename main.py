import logging
import os
import uvicorn

from fastapi import FastAPI, HTTPException, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="static")


class AuthInfo(BaseModel):
    password: str


class CommandBody(BaseModel):
    name: str
    description: str
    command: str


class Command:
    def __init__(self, name, description, command):
        self.name = name
        self.description = description
        self.command = command


@app.get("/")
def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request, "command_container": command_container})


@app.post("/command", status_code=200)
def exec_command(comm: CommandBody):
    if any(x.command == comm.command for x in command_container):
        if os.system(comm.command) != 0:
            logging.warning(f"Executing '{comm.command}' threw an error...")
            raise HTTPException(status_code=500, detail="Internal server error when running command")
    else:
        raise HTTPException(status_code=404, detail="Command not found")


@app.get("/auth")
def auth_user(password: str):
    with open("./config/pass.txt") as pass_file:
        p = pass_file.read()

    if p == password:
        pass

    return {""}


def setup_application():
    with open("./config/commands.txt") as command_file:
        commands = command_file.read()
        commands = commands.splitlines()

        commands = list(filter(None, commands))
        container = []

        for i in command_generator(commands, 3):
            new_com = Command(name=i[0], description=i[1], command=i[2])
            container.append(new_com)

    return container


def command_generator(commands, batch_size):
    for i in range(0, len(commands), batch_size):
        yield commands[i:i + batch_size]


logging.info("Setting up application")
command_container = setup_application()
logging.info(f'Read in {len(command_container)} commands')

if __name__ == '__main__':
    uvicorn.run(app, host="0.0.0.0", port=3333)
