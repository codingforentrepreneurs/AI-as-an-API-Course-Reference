import os
import pathlib
from typing import Optional
from fastapi import FastAPI

from cassandra.cqlengine.management import sync_table

from . import (
    config,
    db, 
    models,
    ml
)

app = FastAPI()
settings = config.get_settings()

BASE_DIR = pathlib.Path(__file__).resolve().parent

MODEL_DIR = BASE_DIR.parent / "models"
SMS_SPAM_MODEL_DIR = MODEL_DIR / "spam-sms"
MODEL_PATH = SMS_SPAM_MODEL_DIR / "spam-model.h5"
TOKENIZER_PATH = SMS_SPAM_MODEL_DIR / "spam-classifer-tokenizer.json"
METADATA_PATH = SMS_SPAM_MODEL_DIR / "spam-classifer-metadata.json"

AI_MODEL = None
DB_SESSION = None
SMSInference = models.SMSInference

@app.on_event("startup")
def on_startup():
    global AI_MODEL, DB_SESSION
    AI_MODEL = ml.AIModel(
        model_path= MODEL_PATH,
        tokenizer_path = TOKENIZER_PATH,
        metadata_path = METADATA_PATH
    )
    DB_SESSION = db.get_session()
    sync_table(SMSInference)
    

@app.get("/") # /?q=this is awesome
def read_index(q:Optional[str] = None):
    global AI_MODEL
    query = q or "hello world" # 280
    preds_dict = AI_MODEL.predict_text(query)
    # NoSQL -> cassandra -> DataStax AstraDB
    return {"query": query, "results": preds_dict}