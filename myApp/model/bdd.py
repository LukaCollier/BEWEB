from . import bddGen
import inspect
import hashlib

def func_name():
    return inspect.currentframe().f_back.f_code.co_name

def verifLogin(login):
    sql = 'SELECT * FROM utilisateur WHERE login=%s'
    param = (login,)
    return bddGen.selectOneData(func_name(), sql, param, None)

def verifAuthData(login, mdp):
    mdp = hashlib.sha256(mdp.encode())
    mdpC = mdp.hexdigest()
    sql = 'SELECT * FROM utilisateur WHERE login=%s AND mdp=%s'
    param = (login, mdpC)
    return bddGen.selectOneData(func_name(), sql, param, None)