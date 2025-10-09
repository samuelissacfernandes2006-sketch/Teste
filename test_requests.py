import APP
from requests import request
from datetime import datetime,  timedelta, timezone 
from jose import jwt 

'''def test_get():
  toencode = {"sub":"teste"}
  toencode.update({"exp": datetime.now(timezone.utc) + timedelta(minutes = 2})
  tokencodificado = jwt.encode(toencode,"teste123",algorithm= "HS256")
  resultado = APP.ler_item(item_id: 1, db: Session = Depends(get_db),api_head: tokencodificado = Header(default=None))
  assert resultado == {"mensagem":"ITEM NÃO ENCONTRADO HTTP_404"}'''
def test_teste():
  num = 1
  assert num == 1
