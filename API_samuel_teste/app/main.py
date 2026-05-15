from pydantic import BaseModel
from fastapi import FastAPI, Depends, Header, Response, Request
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import jwt
from jwt import InvalidSignatureError, ExpiredSignatureError
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from passlib.context import CryptContext
from time import time
import psycopg2
from prometheus_client import Counter, generate_latest, CONTENT_TYPE_LATEST, Histogram
from typing import Generator, Optional
from os import getenv
#secrets\/

#secrets/\

class ClienteUPDATE(BaseModel):
    nome: str
    cpf: str
    nascimento_yyyy_mm_dd: str 
    esta_ativo: bool

@app.middleware("http")
async def add_metrics_middleware(request: Request, call_next):
    start = time()
    response: Response = await call_next(request)
    end_time = time()
    latency = end_time - start

    path = request.url.path
    method = request.method
    status_code = str(response.status_code) 

    REQUEST_COUNTER.labels(method=method, path=path, status_code=status_code).inc()
    REQUEST_LATENCY.labels(method=method, path=path).observe(latency)
    return response

@app.get("/")
def ler_raiz():
    return{"TESTE":"API(localhost:3019/docs)"}

@app.get("/metrics")
async def ler_raiz():
    metrics_data = generate_latest()

    return Response(content=metrics_data, media_type= CONTENT_TYPE_LATEST)





    