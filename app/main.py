import os, pathlib, shutil
import sys
import fastapi as fast
import environs
import aiofiles
from fastapi.middleware.wsgi import WSGIMiddleware
from flask import Flask
from flask_autoindex import AutoIndex


ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
RESULTS_DIR = '/'.join((ROOT_DIR, 'results'))
print(RESULTS_DIR)
env = environs.Env()
env.read_env(recurse=False)
HOST = env('DATA_SERVER_PUBLIC_HOST')
PORT = env('DATA_SERVER_PORT')
VALID_EXTENSIONS = (
    '.png', '.jpeg', '.jpg',
    '.tar.gz', '.tar.xz', '.tar.bz2'
)


app = fast.FastAPI()


# Flask AutoIndex module for exploring directories
flask_app = Flask(__name__)
AutoIndex(flask_app, browse_root = RESULTS_DIR)
app.mount('/results', WSGIMiddleware(flask_app))


@app.get('/')
async def root(): return {'api': 'api/'}


@app.get('/results/{filename}')
async def results(filename):
    if not pathlib.Path('/'.join((ROOT_DIR, 'results', filename))).exists():
        raise fast.HTTPException(
            status_code = 404,
            detail = f"{filename} was not found in results."
        )
    return fast.responses.FileResponse(
        path = '/'.join((
            'results',
            filename
        ))
    )   


@app.post('/api')
async def upload(
    request: fast.Request, 
    file: fast.UploadFile = fast.File(...)):

    print(request.client.host)

    if not file.filename.endswith(VALID_EXTENSIONS):
        raise fast.HTTPException(
            status_code = 400,
            detail = 'File extension not allowed.')

    dest = pathlib.Path('/'.join((
        ROOT_DIR, 
        'results',
        file.filename
    )))
    dest.parent.mkdir(parents=True, exist_ok=True)
    print(dest)

    async with aiofiles.open(dest, 'wb') as buffer:
        await file.seek(0)
        contents = await file.read()
        await buffer.write(contents)

    return f'{HOST}:{PORT}/results/{file.filename}'
