import sqlite3
from flask import Flask, g, render_template

app = Flask(__name__)
DATABASE = 'db/sneakerbuddy.db'

@app.route("/")
def template_test():
    return render_template('recommendations.html', owned=["Off-White", "Raf", "Yeezy"])

@app.route('/shoes')
def display_shoes():
    shoes = []

    for shoe in query_db('select * from sneakers ORDER BY hype_avg_score DESC'): 
        shoes.append(shoe)

    return render_template('shoes.html', shoes=shoes)

### DB CONFIG METHODS

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    db.row_factory = make_dicts
    return db

def query_db(query, args=(), one=False):
    cur = get_db().execute(query, args)
    rv = cur.fetchall()
    cur.close()
    return (rv[0] if rv else None) if one else rv

def make_dicts(cursor, row):
    return dict((cursor.description[idx][0], value)
                for idx, value in enumerate(row))

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

if __name__ == '__main__':
    app.run(debug=True)