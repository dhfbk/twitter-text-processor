# import argparse
# import warnings
# warnings.simplefilter(action='ignore', category=FutureWarning)

import logging
logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.DEBUG)
logger = logging.getLogger()

import configparser
config = configparser.ConfigParser()
logger.info("Reading default configuration")
config.read('default-config.ini')

# TODO: use argparse to read a custom config file?

uvicorn_host = config['server'].get('host', "0.0.0.0")
uvicorn_port = config['server'].getint('port', 8000)

if not config['general']['langs']:
    logger.error("No languages set in config file")
    exit(1)

langs = [x.strip() for x in config['general']['langs'].split(',')]
logger.info("Languages: " + str(langs))

# Fill langs with default values
for l in langs:
    if l not in config:
        config.add_section(l)
        for k in config.defaults():
            config.set(l, k, config.defaults()[k])

import language

lang_objs = dict()
for l in langs:
    logger.info("Loading language: " + l)
    lang_obj = language.Language(l, config[l])
    lang_obj.loadModels()
    lang_objs[l] = lang_obj

from typing import Union
from fastapi import FastAPI
from pydantic import BaseModel
import uvicorn

class Item(BaseModel):
    text: str
    lang: Union[str, None] = config['general']['default_lang']

app = FastAPI()

@app.post("/")
async def root(item: Item):
    lang = item.lang
    if item.lang not in langs:
        lang = config['general']['fallback_lang']
    logger.info(f"Text ({lang}): {item.text}")
    return lang_objs[lang].parseText(item.text)

# https://stackoverflow.com/questions/7173033/duplicate-log-output-when-using-python-logging-module
if (logger.hasHandlers()):
    logger.handlers.clear()
logger = logging.getLogger("uvicorn.error")
uvicorn.run(app, host=uvicorn_host, port=uvicorn_port)
