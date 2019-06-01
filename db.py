import psycopg2


def setup_db():
    dbconnection = psycopg2.connect("user='user' password='pass' host='localhost' dbname='db' port='5434'")
    db=dbconnection.cursor()
    db.execute("create extension if not exists cube;")
    db.execute("drop table if exists vectors")
    db.execute("create table vectors (id serial, file varchar, vec_low cube, vec_high cube);")
    db.execute("create index vectors_vec_idx on vectors (vec_low, vec_high);")
    dbconnection.commit()
setup_db()
