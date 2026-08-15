from fastapi import APIRouter,Depends,Request,Body, HTTPException,Query,Cookie
from fastapi.responses import FileResponse, RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from models import * 
from database import get_db
import bcrypt
from auth import *
from fastapi.responses import Response
import asyncio
from asyncio import create_task
import httpx
from database import SessionLocal

router=APIRouter()

@router.get('/')
def root():
    return FileResponse('templates/reglog.html')

@router.post('/reglog')
async def reglog(db:AsyncSession=Depends(get_db), data=Body()):
    ex=select(User).filter(User.name==data['name'])
    result=await (db.execute(ex))
    user=result.first()
    if not(user):
        user=User(name=data['name'], password=bcrypt.hashpw(data['password'].encode('utf-8'), bcrypt.gensalt()).decode('utf-8'))
        db.add(user)
        await db.commit()
        await db.refresh(user)
        token=create_token(str(user.name)) #type:ignore
    elif not(bcrypt.checkpw(data['password'].encode(), user[0].password.encode())):
        raise HTTPException(401, 'Неправильный логин или пароль')
    else:
        token=create_token(str(user[0].name)) #type:ignore
    return {'status':'ok', 'redirect_url':f'/mainpageRED?token={token}'}

@router.get('/mainpageRED')
def RED(token=Query()):
    response=RedirectResponse('/mainpage',headers={'Authorization':f'Bearer {token}'})
    response.set_cookie(key='token',value=token,max_age=3600,path='/')
    return response

@router.get('/mainpage')
def mainpage(request:Request, token=Cookie()):
    get_by_token(token)
    return FileResponse('templates/mainpage.html')

async def fetch(time, url,id):
    while True:
        try:
            async with httpx.AsyncClient() as client:
                response=await client.get(url)
                if response.status_code//100==5 or response.status_code//100==4:
                    resp=False
                elif response.status_code//100==3:
                    resp=True
                elif response.status_code//100==2:
                    resp=True
                async with SessionLocal() as db: #type:ignore
                    ex=select(Site).filter(Site.user_id==id, Site.url==url)
                    result=await (db.execute(ex))
                    site=result.first()[0]
                    target=Check(code=response.status_code, response=resp, user_id=id, site_id=site.id)
                    db.add(target)
                    await db.commit()
        except Exception as e:
            pass
        await asyncio.sleep(time)

async def monitor(id):
        async with SessionLocal() as db: #type:ignore
            ex=select(Site).filter(Site.user_id==id)
            result=await (db.execute(ex))
            sites=result.all()
        for i in sites:
            for j in i:
                create_task(fetch(j.interval*60, j.url,id))

@router.get('/upgrade')
async def start(token=Cookie(), db:AsyncSession=Depends(get_db)):
    if token:
        ex=select(User).filter(User.name==get_by_token(token))
        result=await (db.execute(ex))
        user=result.first()
        asyncio.create_task(monitor(user[0].id)) #type:ignore


@router.get('/showsites')
async def show(request:Request,db:AsyncSession=Depends(get_db), token=Cookie()):
    ex=select(User).filter(User.name==get_by_token(token))
    result=await (db.execute(ex))
    res=result.first()
    if not(res):
        raise HTTPException(404, 'У вас нету сайтов. Давайте заведем!')
    user=res[0]          #type:ignore
    ex1=select(Site).filter(Site.user_id==user.id)
    result1=await (db.execute(ex1))
    sites=result1.all()
    text=''
    for i in sites:
            j=i[0]
            ex2=select(Check).filter(Check.site_id==j.id, Check.user_id==user.id).order_by(Check.created_at)
            result=await (db.execute(ex2))
            res=result.first()
            if res:
                check=res[0] #type:ignore
                text+=f'''
                <h3>Название: {j.name}\tСсылка: {j.url}\tИнтервал: {j.interval}<h3>
                <button onclick="deleteSite({j.id})">Удалить</button>
                <hr>
                <h3>{f'🟢 Успешно:{check.code}' if check.code//100==2 else f'🔴 Ошибка: {check.code}'}<h3>
                <p></p>
                '''
    return {'text':text}


@router.post('/sites')
async def append(token=Cookie(), db:AsyncSession=Depends(get_db), data=Body()):
    name=get_by_token(token)
    ex=select(User).filter(User.name==name)
    result=await (db.execute(ex))
    user=result.first()
    ex1=select(Site).filter(Site.url==data['url'])
    res1=await db.execute(ex1)
    res=res1.first()
    if res:
        raise HTTPException(400,'Такая ссылка уже есть')
    target=Site(url=data['url'], name=data['name'], interval=data['interval'], user_id=user[0].id) #type:ignore
    db.add(target)
    await db.commit()
    return {'sites':'success'}

@router.delete('/sites/{id}')
async def delete(id=Body(), db:AsyncSession=Depends(get_db), token=Cookie()):
    name=get_by_token(token)
    ex=select(User).filter(User.name==name)
    res=await (db.execute(ex))
    user=res.first()
    if not(user):
        raise HTTPException(404, 'Такого пользователя нет!')
    us=user[0]

    ex1=select(Site).filter(Site.id==id['id'])
    res=await (db.execute(ex1))
    s=res.first()
    if not(s):
        raise HTTPException(404, 'Такого пользователя нет!')
    site=s[0]
    if not(us.id==site.user_id):
        raise HTTPException(401, 'Парсер пренадлежит не вам!')
    await db.delete(site)
    await db.commit()




