# Copyright 2023 iiPython

# Modules
import random
import string
import shelve
from pathlib import Path
from dataclasses import dataclass

from blacksheep import (
    Application, FromJSON, Response,
    json
)
from blacksheep.server.responses import not_found, redirect
from blacksheep.server.templating import use_templates
from jinja2 import FileSystemLoader

from . import app

# Initialization
view = use_templates(
    app,
    loader = FileSystemLoader(Path(__file__).parent / "templates"),
    enable_async = True
)
charset = string.ascii_letters + string.digits

# Database init
database = shelve.open("db/main.db", writeback = True)
if "urls" not in database:
    database["urls"] = {}

# Class structure
@dataclass
class ShortenInput:
    url: str

# Handle saving db
@app.on_stop
async def save_db(app: Application) -> None:
    database.close()

# Handle routes
@app.route("/", methods = ["GET"])
async def index_page() -> Response:
    return await view("index", {})

@app.route("/{short_id}", methods = ["GET"])
async def handle_link(short_id: str) -> Response:
    if short_id not in database["urls"]:
        return not_found("Link not found.")

    return redirect(database["urls"][short_id])

@app.route("/api/shorten", methods = ["POST"])
async def shorten_link(data: FromJSON[ShortenInput]) -> Response:
    data = data.value
    if (data.url[:4] != "http") or "://" not in data.url:
        return json({"error": "URL must contain a protocol (http at minimum)."})

    # Generate short ID
    short_id, length, ticker = "", 1, 0
    while ticker <= 10:
        if ticker == 10:
            ticker, length = 0, length + 1
            continue

        short_id = "".join([random.choice(charset) for i in range(length)])
        if short_id not in database["urls"]:
            break

        ticker += 1

    # Save to database and return
    database["urls"][short_id] = data.url
    return json({"id": short_id})
