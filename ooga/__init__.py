# Copyright 2023 iiPython

# Modules
from blacksheep import Application

# Initialization
app = Application()

# Routes
from .routes import *  # noqa: E402, F403
