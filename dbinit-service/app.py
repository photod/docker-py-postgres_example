import os
from flask import Flask
from flask import g
import pg8000.native
import random

app = Flask(__name__)

db_host = os.getenv("POSTGRES_HOST")
db_user = os.getenv("POSTGRES_USER")
db_pass = os.getenv("POSTGRES_PASSWORD")
db_name = os.getenv("POSTGRES_DB")

def get_db():
    if not hasattr(g, 'postgres_db'):
        try:
            g.postgres_db = pg8000.native.Connection(db_user, db_host, db_name, password=db_pass)
        except (pg8000.exceptions.InterfaceError, pg8000.exceptions.DatabaseError):
            return None        
    
    if ping_db(g.postgres_db):
        return g.postgres_db
    else:
        g.postgres_db = None

def ping_db(db=None):
    if db:
        conn = db
    else:
        conn = get_db()
    if conn:    
        db_ver_info = g.postgres_db.run("select version();")
        if db_ver_info:
            return True
    return False

@app.teardown_appcontext
def close_db(error):    
    if hasattr(g, 'postgres_db'):
        g.postgres_db.close()


def make_sure_schema_is_in_place():
    conn = get_db()
    if not conn:
        return False    
    conn.run("CREATE TABLE IF NOT EXISTS log(id SERIAL PRIMARY KEY, text TEXT NOT NULL, addedon timestamp default current_timestamp);")    
    return True

def insert_some_noise_to_db():
    conn = get_db()
    subj = ["stranger", "guest", "user", "glasshole", "robot", "hacker", "investigator"]
    verb = ["hacked", "crashed", "started", "restarted", "stopped", "reloaded", "ruined", "restored"]
    obj  = ["server", "database", "application", "cluster", "service"]
    msg  = "A {} {} the {}".format(random.choice(subj), random.choice(verb), random.choice(obj))    
    sql_query = f"INSERT INTO log (text) VALUES ('{msg}')"    
    if conn:
        conn.run(sql_query)

def get_top10_log_entries():
    conn = get_db()
    if conn:
        data = ["postgres log db is not available"]
        if conn:
            data = conn.run("SELECT * FROM log ORDER BY addedon DESC LIMIT 10")    
        return " ".join([ out := "<li>{}: {}</li>".format(item[0], item[1]) for item in data])
    else:
        return "No connection to the DB, Sorry", 500
    

@app.route("/")
def get_root():
    make_sure_schema_is_in_place()
    insert_some_noise_to_db()
    return(get_top10_log_entries())

@app.route("/healthcheck")
def check_health():
    if ping_db():
        return("healthy")
    else:
        return("faulty")

if __name__ == "__main__":
    app.run(host ='0.0.0.0', port = 8000, debug = False)