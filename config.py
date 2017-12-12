import pymysql

DEBUG = True
SECRET_KEY = "mysecret"
# SQLALCHEMY_DATABASE_URI = 'postgres://foqoathejkauyl:5d1e146269753b67cc836fdf89afa29c65d52ac69c9add560dda7cfb1fd8586f@ec2-54-235-219-113.compute-1.amazonaws.com:5432/dd3n2pe57rc68c'
SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:mysql@localhost/plusone'
SQLALCHEMY_TRACK_MODIFICATIONS = False
