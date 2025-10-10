
from requests import request
from datetime import datetime,  timedelta, timezone 
from jose import jwt 

def test_GET():
  toencode = {"sub":"teste"}
  toencode.update({"exp": datetime.now(timezone.utc) + timedelta(minutes = 2)})
  tokencodificado = jwt.encode(toencode,"teste123",algorithm= "HS256")
  resultado = request("get","https://myfin-financial-management.bubbleapps.io/api/1.1/obj/category/", headers={"Authotization":"Bearer " +tokencodificado})
  assert resultado.json() is not None
