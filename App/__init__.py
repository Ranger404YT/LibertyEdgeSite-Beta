from flask import Flask
import os

app = Flask("__main__",template_folder='Template',static_folder='Static')
app.config['SECRET_KEY'] = 'ZOHU6-H109I-0LVI8-TKUKR'

from .db import DB

db = DB('app.db')

from . import route