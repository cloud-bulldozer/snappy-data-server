import os, pathlib

import fastapi as fast
from fastapi.middleware.wsgi import WSGIMiddleware
import environs
import aiofiles
import starlette as star
import fastapi_users as fastusr
import databases
from flask import Flask
from flask_autoindex import AutoIndex

import app.db.base as base
import app.models as mdl


ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
RESULTS_DIR = pathlib.Path('/'.join((ROOT_DIR, 'results')))
env = environs.Env()
env.read_env(recurse=False)
POSTGRES_PORT = f":{env('POSTGRES_PORT')}" if len(env('POSTGRES_PORT')) else ''
DATABASE_URL = f"postgres://postgres:{env('POSTGRES_PASSWORD')}@{env('POSTGRES_SERVER')}{POSTGRES_PORT}/postgres"
SECRET = env('DATA_SERVER_SECRET')
HOST = env('DATA_SERVER_PUBLIC_HOST')
PORT = env('DATA_SERVER_PORT') 
VALID_EXTENSIONS = (
    '.png', '.jpeg', '.jpg',
    '.tar.gz', '.tar.xz', '.tar.bz2', '.csv', '.txt', '.json', '.markdown', '.doc', '.docx', '.pdf', '.log', '.xml', '.yml', '.yaml'
)


app = fast.FastAPI()
database = databases.Database(DATABASE_URL)
user_db = fastusr.db.SQLAlchemyUserDatabase(
        user_db_model = mdl.UserDB, 
        database = database, 
        users = base.UserTable.__table__)
jwt_authentication = fastusr.authentication.JWTAuthentication(
    secret=SECRET, lifetime_seconds=28800,
    tokenUrl='/auth/jwt/login')
api_users = fastusr.FastAPIUsers(
    db = user_db,
    auth_backends = [jwt_authentication],
    user_model = mdl.User,
    user_create_model = mdl.UserCreate,
    user_update_model = mdl.UserUpdate,
    user_db_model = mdl.UserDB)


# Flask AutoIndex module for exploring directories
flask_app = Flask(__name__)
AutoIndex(flask_app, browse_root = RESULTS_DIR)
app.mount('/index', WSGIMiddleware(flask_app))


@app.on_event("startup")
async def startup():
    await database.connect()


@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()


@app.get('/')
async def root(): 
    return star.responses.RedirectResponse(url = '/docs')


@app.get('/results/{filepath:path}')
async def results(filepath: str):
    p = RESULTS_DIR.joinpath(filepath)
    if not p.is_file():
        raise fast.HTTPException(
            status_code = 404,
            detail = f"{filepath} was not found in results.")
    return fast.responses.FileResponse(path = p)   


@app.post('/api')
async def upload(
    request: fast.Request, 
    file: fast.UploadFile = fast.File(...),
    user: mdl.User = fast.Depends(api_users.get_current_active_user),
    filedir: str = ''):

    if not file.filename.endswith(VALID_EXTENSIONS):
        raise fast.HTTPException(
            status_code = 400,
            detail = 'File extension not allowed.')
    
    dest = RESULTS_DIR.joinpath(filedir, file.filename)
    dest.parent.mkdir(parents=True, exist_ok=True)

    async with aiofiles.open(dest, 'wb') as buffer:
        await file.seek(0)
        contents = await file.read()
        await buffer.write(contents)

    return f'{HOST}:{PORT}/results/{dest.parent.name}/{dest.name}'


app.include_router(
    api_users.get_auth_router(jwt_authentication),
    prefix = '/auth/jwt',
    tags = ['auth']
)
