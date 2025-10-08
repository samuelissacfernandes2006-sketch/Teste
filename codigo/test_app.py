import APP

def test_login():
  resultado = APP.login(user:OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db))
  assert resultado == {"mensagem":f"login {login_atual}"}
