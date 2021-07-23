import os, shutil, time
from pathlib import Path
from typing import Any, Dict, Iterable, Optional

from datetime import date
import fastapi as fast
from fastapi.middleware.wsgi import WSGIMiddleware
from fastapi_utils.tasks import repeat_every
import environs
import aiofiles
import starlette as star
import fastapi_users as fastusr
import databases
import json
from flask import Flask
from flask_autoindex import AutoIndex
import logging 
import app.db.base as base
import app.models as mdl
import app.config as cfg

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
RESULTS_DIR = Path('/'.join((ROOT_DIR, 'results')))
env = environs.Env()
env.read_env(recurse=False)
POSTGRES_PORT = f":{env('POSTGRES_PORT')}" if len(env('POSTGRES_PORT')) else ''
DATABASE_URL = f"postgres://postgres:{env('POSTGRES_PASSWORD')}@{env('POSTGRES_SERVER')}{POSTGRES_PORT}/postgres"
SECRET = env('DATA_SERVER_SECRET')
HOST = env('DATA_SERVER_PUBLIC_HOST')
PORT = env('DATA_SERVER_PORT') 
VALID_EXTENSIONS = (
    '.csv', '.doc', '.docx',
    '.jpeg', '.jpg', '.json',
    '.log', '.markdown',  
    '.png', '.pdf', 
    '.tar', '.gz', '.xz', '.bz2',  '.txt', 
    '.xml', '.yml', '.yaml',
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

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def validate_extension(filename):
    suffixes = Path(filename).suffixes
    bad_suffixes = list(filter(lambda ext: ext not in VALID_EXTENSIONS, suffixes))

    if suffixes and not bad_suffixes:
        # happy path has at least 1 suffix, and 0 bad suffixes
        return
    elif not suffixes:
        detail = 'Uploaded file is invalid because it does not have an extension.'
    elif len(bad_suffixes) == 1:
        detail = f'{bad_suffixes} is an invalid extension.'
    elif len(bad_suffixes) > 1:
        detail = f'{bad_suffixes} are invalid extensions.'
    
    raise fast.HTTPException(
        status_code = 400,
        detail = detail
    )
 

def remove_folder(path,tdate):
    if not shutil.rmtree(path):
        logger.info(f"---{tdate}---{path} folder is removed successfully")
    else:
        logger.info(f"---{tdate}---Unable to delete the {path}")


def remove_file(path,tdate):
    if not os.remove(path):         
        logger.info(f"---{tdate}---{path} file is removed successfully")
    else:           
        logger.info(f"---{tdate}---Unable to delete the {path}")


def get_file_or_folder_age(path):
    # getting modified time of the file/folder in seconds
    return os.stat(path).st_mtime
        
@app.on_event("startup")
async def startup():
    await database.connect()

@app.on_event("startup")
@repeat_every(seconds= 24 * 60 * 60) 
async def remove_old_files():

    if(env('ENABLE_PRUNER')=='true'):
        today = date.today()
        logger.info(f"---------------------------------------Pruner logs for {today}-------------------------------")

        Cfg: Config=cfg.get_config()
        
        for Conf in Cfg.prune_configs:

            logger.info(Conf)
            folder = Conf.path
            days = Conf.days_to_live

            path = os.path.join(RESULTS_DIR, folder)
                        
            # time.time() returns current time in seconds
            seconds = time.time() - (days * 24 * 60 * 60)

            # checking whether the file is present in path or not
            if os.path.exists(path):
                # iterating over each and every folder and file in the path
                for root_folder, folders, files in os.walk(path):
                        # checking folder from the root_folder
                        for folder in folders:
                                folder_path = os.path.join(root_folder, folder)

                                if seconds >= get_file_or_folder_age(folder_path):
                                        remove_folder(folder_path,today)

                        # checking the current directory files
                        for file in files:
                                file_path = os.path.join(root_folder, file)

                                if seconds >= get_file_or_folder_age(file_path):
                                        remove_file(file_path,today)


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
    filename: str,
    user: mdl.User = fast.Depends(api_users.get_current_active_user),
    filedir: str = ''
):
    validate_extension(filename)

    dest = RESULTS_DIR.joinpath(filedir, filename)
    dest.parent.mkdir(parents=True, exist_ok=True)        

    async with aiofiles.open(dest, 'wb') as buffer:       
           async for chunk in request.stream():
                    await buffer.write(chunk)

    return {
           'loc': f'http://{HOST}:{PORT}/index/{dest.parent.name}/'
        }    


app.include_router(
    api_users.get_auth_router(jwt_authentication),
    prefix = '/auth/jwt',
    tags = ['auth']
)
