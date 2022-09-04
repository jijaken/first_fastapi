from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from loguru import logger
from typing import TypeVar
from datetime import date, timedelta
import psycopg2
from psycopg2.extras import RealDictCursor


app = FastAPI()


def check_errors(res):
    '''
    Проверяет результат селекта на наличие значений
    '''
    if res is None:
        raise HTTPException(404, detail='user not found')


class SimpleClass(BaseModel):
    '''
    Класс для волидации значений по пути /sum_date
    '''
    current_date : date
    offset: int

    class Config:
        orm_mode = True


class User(BaseModel):
    '''
    Класс для волидации значений по пути /user/validate
    '''
    name: str
    surname: str
    age: int
    registration_date: date

    class Config:
        orm_mode = True


class Postgresql_dump(BaseModel):
    '''
    Класс для проверки валидации данных таблички user
    '''
    gender: int
    age: int
    city: str

    class Config:
        orm_mode = True



@app.get('/sum_date', response_model=TypeVar(SimpleClass))
def sum_def(current_date : date,offset: int) -> date:
    '''
    Перевод даты на несколько дней
    '''
    logger.info(current_date)
    return  current_date+timedelta(days=offset)



@app.post('/user/validate')
def func(user: User):
    '''
    Проебразование json строки в строку с привествием
    '''
    return f'Will add user: {user.name} {user.surname} with age {user.age}'


def get_db():
    '''
    Соединение с базой данных для inject
    '''
    conn = psycopg2.connect('postgresql://login:pass@hostname:port/database',
                            cursor_factory=RealDictCursor)
    return conn

@app.get('/user/{id}',response_model=  Postgresql_dump)
def connect_postgresql(id: int, db = Depends(get_db)):
    '''
    Вытаскиваем информацию по id из postgresql из таблички user
    '''
    with db.cursor() as cursor:
        cursor.execute(f'''SELECT gender, age, city 
        FROM "user"
        WHERE id={id}
        ''')
        result = cursor.fetchone()
        logger.info(result)
        check_errors(result)
        return result



class PostResponse(BaseModel):
    '''
    Класс для проверки валидации данных таблички post
    '''
    id:int
    text:str
    topic:str
    class Config:
        orm_mode = True



@app.get('/post/{id}',response_model=PostResponse)
def func(id:int,db = Depends(get_db)) -> PostResponse:
    '''
    Вытаскиваем информацию по id из postgresql из таблички post
    '''
    with db.cursor() as cursor:
        cursor.execute(f'''SELECT id, text, topic
        FROM post
        WHERE id={id}
        ''')
        result = cursor.fetchone()
        check_errors(result)
        return result


