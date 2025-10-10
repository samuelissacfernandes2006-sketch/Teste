
from requests import request
from datetime import datetime,  timedelta, timezone 
from jose import jwt 

def test_GET():
  toencode = {"sub":"teste"}
  toencode.update({"exp": datetime.now(timezone.utc) + timedelta(minutes = 2)})
  tokencodificado = jwt.encode(toencode,"teste123",algorithm= "HS256")
  resultado = request("get","http://[::1]:3019/items/-1", headers={"api-head":tokencodificado},verify= False)
  assert resultado.json() == {'mensagem': 'ITEM NÃO ENCONTRADO HTTP_404'}
