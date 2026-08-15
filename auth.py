from jose import jwt
from datetime import datetime,timedelta
from fastapi.security import OAuth2PasswordBearer
from config import SECRET,ALGORITHM
from fastapi import HTTPException,Depends

oauth=OAuth2PasswordBearer(tokenUrl='reglog')

def create_token(username:str):
    payload={
        'sub':username,
        'exp':datetime.utcnow()+timedelta(hours=1)
    }
    return jwt.encode(payload,SECRET,ALGORITHM)

def get_user(token=Depends(oauth)):
    try:
        data=jwt.decode(token,SECRET,ALGORITHM)
        return data['sub']
    except:
        raise HTTPException(401, 'Ошибка с токеном')

def get_by_token(token):
    try:
        data=jwt.decode(token,SECRET,ALGORITHM)
        return data['sub']
    except:
        raise HTTPException(401, 'Ошибка с токеном')
