import APP

def test_de_secretkey:
  valordachave = APP.SECRET_KEY
  assert valordachave == "teste123"
def test_de_algorithm:
  valordachave = APP.ALGORITHM
  assert valordachave == "HS256"
def test_de_expire:
  valordachave = APP.ACCESS_TOKEN_EXPIRE_MINUTES
  assert valordachave == 2
