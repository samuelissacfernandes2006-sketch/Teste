from typing import Annotated, Union
from pydantic import BaseModel
from fastapi import FastAPI, Depends, HTTPException, status, Header
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy import create_engine, Column, Integer, String, Boolean
from sqlalchemy.orm import sessionmaker, declarative_base, Session 
from jose import jwt, JWTError
from jwt import InvalidSignatureError, ExpiredSignatureError
from datetime import datetime, timedelta, timezone
from passlib.context import CryptContext

SECRET_KEY = "teste123"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 2

pwd_context = CryptContext(schemes=["des_crypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token") #rota "token" para obter token

#teste de login por usuario e senha
login_atual= {"usuario":None,"senha": None, "token": None}



app = FastAPI()

Base = declarative_base()

class UserDB(Base):
    __tablename__ = "usuarios"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)

class ItemDB(Base): 
    __tablename__ = "itens"
    id = Column("item_id", Integer, primary_key=True, index=True) 
    name = Column(String, index=True)
    price = Column(Integer)
    
SQLALCHEMY_DATABASE_URL = "sqlite:///Minhabasededados.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
Base.metadata.create_all(engine)  
Sessionlocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = Sessionlocal()
    try:
        yield db
    finally:
        db.close()

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def validacao_de_token(token: str):
    try:
        tokendeco = jwt.decode(token, SECRET_KEY, algorithms=ALGORITHM)
    except ExpiredSignatureError:
        return {"mensagem":"TOKEN EXPIRADO"}
    except InvalidSignatureError:
        return {"mensagem":"ERRO DE ASSINATURA"}





#verificar usuario na Userdb
def get_user_by_username(db: Session, username: str):
    return db.query(UserDB).filter(UserDB.username == username).first()
 
# Dependência para obter o usuário logado !!teste!////
async def get_current_user(db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Não foi possível validar as credenciais",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        # Decodifica o token
        payload = jwt.decode(login_atual["token"], SECRET_KEY, algorithms=[ALGORITHM])
        username: str = login_atual["usuario"]
        if username is None:
            raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Faça o login",
        headers={"WWW-Authenticate": "Bearer"},
    )
    except JWTError:
        raise credentials_exception 
    #procura o usuario na db e verifica a existencia
    user = get_user_by_username(db, username=username)
    if user is None:
        raise credentials_exception
    return user
    #\teste!!!

class Item(BaseModel):
    item_name:str
    item_price:float
    class Config:
         from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class UserCreate(BaseModel):
    usuario: str
    senha: str
@app.post("/")
def login(user:OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    db_user = get_user_by_username(db,username = user.username)
    if not db_user or not verify_password(user.password,db_user.hashed_password): 
        return {"mensagem":"usuario ou senha errados"}
    login_atual["usuario"]=user.username
    senha_codificada = get_password_hash(password=user.password)
    login_atual["senha"]=senha_codificada
    return {"mensagem":f"login {login_atual}"} 

@app.post("/users/", response_model=UserCreate)
def criar_usuario(user: UserCreate, db: Session = Depends(get_db)):
    db_user = get_user_by_username(db, username=user.usuario)
    if db_user:
        raise HTTPException(status_code=400, detail="Usuário já registrado")
    
    hashed_password = get_password_hash(user.senha)
    db_user = UserDB(username=user.usuario, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return user
'''@app.post("/users/", response_model=UserCreate)
def criar_usuario_aberto(user: UserCreate, db: Session = Depends(get_db)):
    db_user = get_user_by_username(db, username=user.username)
    if db_user:
        raise HTTPException(status_code=400, detail="Usuário já registrado")
    
    hashed_password = get_password_hash(user.password)
    db_user = UserDB(username=user.username, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return user '''
#criação de token :
@app.post("/token")
async def login_e_criar_token(data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = get_user_by_username(db, username=data.username)
    
    if not user or not verify_password(data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="NOME DE USUARIO OU SENHA INCORRETOS",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if login_atual["token"]:
        login_atual["token"]= None
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode = {"sub": login_atual["usuario"]}
    if access_token_expires:
        expire = datetime.now(timezone.utc) + access_token_expires
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp":expire})
    encoded_token = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    login_atual["token"] = encoded_token
    return {"access_token": encoded_token, "token_type": "bearer"}


@app.get("/items/{item_id}")
def ler_item(item_id: int, db: Session = Depends(get_db),api_head: str = Header(default=None)):
            #if login_atual["token"] is None:
            #    return {"message":"CRIE UM TOKEN"}
            VT_resultado = validacao_de_token(token = api_head)
            if VT_resultado:
                return {"mensagem":VT_resultado}

            item = db.query(ItemDB).filter(ItemDB.id == item_id).first()
            if item is None:
                return {"mensagem":"ITEM NÃO ENCONTRADO HTTP_404"}
            return item
mensagemdelogin ="Faça Login"
@app.put("/items/{item_id}")
def atualizar_item(item_id: int, item: Item, db:Session = Depends(get_db)):
    verificação_de_usuario = db.query(UserDB).filter(UserDB.username == login_atual["usuario"])
    if verificação_de_usuario is None:
        return{"HTTP401":mensagemdelogin}
    else:
        testedeexistencia = db.query(ItemDB).filter(ItemDB.id == item_id).first()
        if testedeexistencia is None:
            return {"mensagem":"ITEM NÃO ENCONTRADO HTTP_404"}
        else:
            testedeexistencia.name = item.item_name
            testedeexistencia.price = item.item_price
            db.commit()
            db.close()
            return {"mensagem": "ITEM ATUALIZADO"}
@app.post("/items/")
async def criar_item(item: Item, db: Session = Depends(get_db)):
    verificação_de_usuario = db.query(UserDB).filter(UserDB.username == login_atual["usuario"])
    if verificação_de_usuario is None:
        return{"HTTP401":mensagemdelogin}
    else:
        db_item = ItemDB(name=item.item_name, price=item.item_price)    
        db.add(db_item)
        db.commit()
        db.refresh(db_item)
        return db_item

@app.delete("/items/{item_id}")
def deletar_item(item_id: int, db: Session = Depends(get_db)):
    verificação_de_usuario = db.query(UserDB).filter(UserDB.username == login_atual["usuario"])
    if verificação_de_usuario is None:
        return{"HTTP401":mensagemdelogin}
    else:
        item = db.query(ItemDB).filter(ItemDB.id == item_id).first()
        if item is None:
            return {"mensagem":"ITEM NÃO ENCONSTRADO 404"}
        else:
            db.delete(item)
            db.commit()
        return {"mensagem":f"id={item_id}, ITEM DELETADO"}
