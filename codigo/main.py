from pydantic import BaseModel
from fastapi import FastAPI, Depends,Header
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import jwt
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo
from passlib.context import CryptContext
from typing import Generator, Optional
import psycopg2
from prometheus_client import make_asgi_app

metrics_app = make_asgi_app()
app.mount("/metrics", metrics_app)
#secrets
SECRET_KEY = "teste123"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 2

pwd_context = CryptContext(schemes=["des_crypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token") #rota "token" para obter token

on_off = {"status": False}
def criar_conexão() -> Generator[Optional[object], None, None]:
    if on_off["status"] == False:
        yield None
        return 
    
    conexão = None
    cursorDB = None
    try:
        conexão  = psycopg2.connect(
            host="postgres-api",
            port="5432",
            user="postgres",
            password="Sam123", 
            database="postgres"
        )
        conexão.set_session(autocommit=True)
        cursorDB = conexão.cursor()
        
        yield cursorDB
        
    except:
        yield None
        
    finally:
        if conexão is not None:
                conexão.close() 
def criar_tabelas():
    conexao_gerador = criar_conexão()
    cursorDB = next(conexao_gerador)
    
    try:
        if cursorDB is None:
            return
        

        cursorDB.execute('''
            CREATE TABLE IF NOT EXISTS cliente (
                id_cliente SERIAL PRIMARY KEY,
                nome VARCHAR(255) NOT NULL,
                cpf VARCHAR(12) NOT NULL UNIQUE,
                data_de_nascimento DATE NOT NULL,
                esta_ativo BOOLEAN NOT NULL DEFAULT TRUE,
                CONSTRAINT chk_cpf_formato CHECK ( cpf ~ '^\d{11}$' )
            );
        ''')
        
        cursorDB.execute('''
            CREATE TABLE IF NOT EXISTS produto (
                id_produto SERIAL PRIMARY KEY,
                nome_produto VARCHAR(255) NOT NULL UNIQUE,
                categoria VARCHAR(255) NOT NULL,
                valor float NOT NULL,
                esta_ativo BOOLEAN NOT NULL DEFAULT TRUE
            );
        ''')
        
        cursorDB.execute('''
            CREATE TABLE IF NOT EXISTS vendas (
                id_venda SERIAL PRIMARY KEY,
                id_cliente INT REFERENCES cliente(id_cliente),
                id_produto INT REFERENCES produto(id_produto),
                quantidade INT NOT NULL,
                valor FLOAT NOT NULL,
                data_compra TIMESTAMPTZ NOT NULL,
                data_confirmacao_compra TIMESTAMPTZ
            );
        ''')

    except Exception as e:
        None
        
    finally:
        try:
            next(conexao_gerador) 
        except StopIteration:
            pass
        except Exception as e:
            None

app = FastAPI()
metrics_app = make_asgi_app()
app.mount("/metrics", metrics_app)


class Prod(BaseModel):
    nome_produto: str
    categoria: str
    valor: float
    
    class Config:
         from_attributes = True

class ProdUPDATE(BaseModel):
    nome_produto: str
    categoria: str
    valor: float
    esta_ativo: bool

class Token(BaseModel):
    access_token: str
    token_type: str

class ClienteCREATE(BaseModel):
    nome: str
    cpf: str
    nascimento_yyyy_mm_dd: str 

class ClienteUPDATE(BaseModel):
    nome: str
    cpf: str
    nascimento_yyyy_mm_dd: str 
    esta_ativo: bool

@app.get("/")
def ler_raiz():
    return{"TESTE":"API(localhost:3019/docs)"}
    
@app.put("/on_off/status")
def criar_conexao8(select_on_off:str):
    if select_on_off == "on":
        on_off["status"] = "True"
        criar_tabelas()
        return {"menssagem":"conexão ligada"}
    if select_on_off == "off":
        on_off["status"] = False
        return {"menssagem":"conexão desligada"}
        
        
    
    
@app.post("/cliente")
def criar_cliente(cliente:ClienteCREATE, cursorDB: object = Depends(criar_conexão)):
    try:
        cursorDB.execute('''SELECT * FROM cliente WHERE cpf = %s''',(cliente.cpf,))

    except psycopg2.errors.UndefinedFunction:
        return {"mensagem":"CPF OU DATA INVALIDOS"}
    else:

        try:
            cursorDB.execute('''INSERT INTO cliente (nome, cpf, data_de_nascimento) VALUES (%s, %s, %s)''',(cliente.nome, cliente.cpf, cliente.nascimento_yyyy_mm_dd,))
        except psycopg2.errors.CheckViolation:
            return {"mensagem": "CPF INVALIDO"}
        except psycopg2.errors.UniqueViolation:
            return {"mensagem":"CLIENTE JA EXISTENTES"}
        except psycopg2.errors.StringDataRightTruncation:
            return {"mensagem":"DADOS SOBRECARREGADOS"}
        

        return {"mensagem":f"cliente criado{cliente}"}

@app.put("/cliente/{cpf_cliente}")
def atualizar_cliente(cpf_cliente: int, cliente:ClienteUPDATE ,cursorDB: object = Depends(criar_conexão)):
    cursorDB.execute('''SELECT * FROM cliente WHERE cpf = %s''',(cliente.cpf,))
    resultado = []
    linhas = cursorDB.fetchall()
    for linha in linhas:
        resultado+=linha    
    if resultado == []:
        return {"mensagem":"cliente não encontrado"}
    
    cursorDB.execute('''UPDATE cliente SET nome= %s WHERE cpf = %s''',(cliente.nome,cliente.cpf,))

    cursorDB.execute('''UPDATE cliente SET data_de_nascimento = %s WHERE cpf = %s''',(cliente.nascimento_yyyy_mm_dd, cliente.cpf,))

    cursorDB.execute('''UPDATE cliente SET esta_ativo = %s WHERE cpf = %s''',(cliente.cpf, cliente.cpf,))

    cursorDB.execute('''UPDATE cliente SET cpf = %s WHERE cpf = %s''',(cliente.cpf, cliente.cpf,))


    return {"mensagem":f"cliente atualizado com sucesso: {cliente}"}

@app.delete("/cliente/{cpf_cliente}")
def deletar_cliente(cpf_cliente: int, cursorDB: object = Depends(criar_conexão)):
    cursorDB.execute('''SELECT * FROM cliente where cpf = %s''',(cpf_cliente,))
    linhas = cursorDB.fetchall()

    resultado = []
    for linha in linhas:
        resultado+=linha
    if resultado== []:
        return{"mensagem":"CLIENTE NÃO ENCONTRADO"}
    
    cursorDB.execute('''DELETE FROM cliente WHERE cpf = %s''',(cpf_cliente,))

    return {"mensagem":"cliente deletado"}


@app.get("/produto/{nome_do_produto}")
def ler_item(nome_do_produto = str,cursorDB: object = Depends(criar_conexão)):
    cursorDB.execute('''SELECT * FROM produto WHERE nome_produto = %s''',(nome_do_produto,))
    linhas = cursorDB.fetchall() 
    produto = []
    for linha in linhas:
        produto+= linha
    if produto == []:
        return {"mensagem":"ITEM NÃO ENCONTRADO HTTP_404"}
    return {"resultado":produto}

@app.put("/produto/{nome_do_produto}")
def atualizar_item(nome_do_produto: str, prod:ProdUPDATE,cursorDB: object = Depends(criar_conexão)):
    cursorDB.execute('''SELECT * FROM produto WHERE nome_produto = %s''',(nome_do_produto,))
    resultado = []
    linhas = cursorDB.fetchall()
    for linha in linhas:
        resultado+=linha    
    if resultado == []:
        return {"mensagem":"item não encontrado"}
    
    cursorDB.execute('''UPDATE produto SET categoria = %s WHERE nome_produto = %s''',(prod.categoria,prod.nome_produto,))

    cursorDB.execute('''UPDATE produto SET valor = %s WHERE nome_produto = %s''',(prod.valor,prod.nome_produto,))

    cursorDB.execute('''UPDATE produto SET esta_ativo = %s WHERE nome_produto = %s''',(prod.esta_ativo,nome_do_produto,))

    cursorDB.execute('''UPDATE produto SET nome_produto = %s WHERE nome_produto = %s''',(prod.nome_produto, prod.nome_produto,))


    return {"mensagem":f"produto criado com sucesso: {prod}"}
@app.post("/produto")
async def criar_item(produto: Prod,cursorDB: object = Depends(criar_conexão)):
    nomedoproduto = produto.nome_produto
    cursorDB.execute('''SELECT * FROM produto where nome_produto = %s''',(nomedoproduto,))
    resultado = cursorDB.fetchall()

    resul = []
    for i in resultado:
        resul+=i
    if resul !=[]:
        return{"mensagem":"item já existente"}
    cursorDB.execute('''INSERT INTO produto (nome_produto, categoria, valor) VALUES (%s,%s,%s)''',(produto.nome_produto, produto.categoria,produto.valor,))

    return{"mensagem":f"produto inserido na db {produto}"}
    
@app.delete("/produto/{nome_do_produto}")
def desativar_item(nome_do_produto: str,cursorDB: object = Depends(criar_conexão)):
    cursorDB.execute('''SELECT * FROM produto where nome_produto = %s''',(nome_do_produto,))
    linhas = cursorDB.fetchall()

    resultado = []
    for linha in linhas:
        resultado+=linha
    if resultado== []:
        return{"mensagem":"PRODUTO NÃO ENCONTRADO"}
    
    cursorDB.execute('''UPDATE produto SET esta_ativo = FALSE WHERE nome_produto = %s''',(nome_do_produto,))

    return {"mensagem":f"produto {nome_do_produto} desativado"}

@app.post("/vendas")
def comprar_prod(CPF_do_cliente:str, nome_do_produto: str, quantidade: int , cursorDB: object = Depends(criar_conexão)):
    try:
        cursorDB.execute('''SELECT * FROM cliente where cpf = %s''',(CPF_do_cliente,))
    except psycopg2.errors.UndefinedFunction:
        return{"mensagem":"CPF INVALIDO"}
    else:
        cursorDB.execute('''SELECT * FROM cliente where cpf = %s''',(CPF_do_cliente,))
        linhas_C = cursorDB.fetchall()

        resultado_cliente = []
        for linha in linhas_C:
            resultado_cliente+=linha
        if resultado_cliente== []:
            return{"mensagem":"CLIENTE NÃO ENCONTRADO"}
        
        try:
            cursorDB.execute('''SELECT * FROM produto where nome_produto = %s''',(nome_do_produto,))
        except psycopg2.errors.UndefinedFunction:
            return {"mensagem":"NOME DO PRODUTO INVALIDO"} 
        else:

            linhas_P = cursorDB.fetchall()

            resultado_produto = []
            for linha in linhas_P:
                resultado_produto+=linha
            if resultado_produto== []:
                return{"mensagem":"PRODUTO NÃO ENCONTRADO"}
            data_atual = datetime.now(ZoneInfo("America/Sao_Paulo"))
            data_formatada = data_atual.strftime('%Y-%m-%d %H:%M:%S')
            valorunit = resultado_produto[3]
            valortotal = valorunit * quantidade

            
            
            cursorDB.execute('''INSERT INTO vendas (id_cliente, id_produto, nome_produto, quantidade, valor,data_compra, data_confirmacao_compra) VALUES (%s, %s, %s, %s, %s, %s, %s)''',(resultado_cliente[0],resultado_produto[0], resultado_produto[1], quantidade, valortotal, str(data_formatada), None,))

            cursorDB.execute('''SELECT id_venda FROM vendas WHERE id_cliente = %s ORDER BY data_compra DESC LIMIT 1''',(resultado_cliente[0],))
            linhas_id_vd = cursorDB.fetchall()
            resultado_id_vd = []
            for linha in linhas_id_vd:
                resultado_id_vd += linha

            return {"mensagem":f"id venda({resultado_id_vd}), Produto comprado {nome_do_produto}*{quantidade} VALOR({valortotal})"}

@app.put("/vendas/{id_venda}")
def confirmar_venda(id_venda:int,cursorDB: object = Depends(criar_conexão)):
    cursorDB.execute('''SELECT * FROM vendas WHERE id_venda = %s''',(id_venda,))
    linhas_V = cursorDB.fetchall()

    resultado_venda = []
    for linha in linhas_V:
        resultado_venda+=linha
    if resultado_venda== []:
        return{"mensagem":"VENDA NÃO ENCONTRADA"}
    data_atual = datetime.now(ZoneInfo("America/Sao_Paulo"))
    data_formatada = data_atual.strftime('%Y-%m-%d %H:%M:%S')

    if resultado_venda[7] != None:
        return {"mensagem":"VENDA JA HAVIA SIDO CONFIRMADA"}
    
    cursorDB.execute('''UPDATE vendas SET data_confirmacao_compra = %s WHERE id_venda = %s''',(data_formatada, id_venda,))

    return{"mensagem":f"venda ({id_venda}) CONFIRMADA"}
