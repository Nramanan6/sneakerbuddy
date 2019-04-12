import sqlite3
from flask import Flask, g, render_template

app = Flask(__name__)
DATABASE = 'db/sneakerbuddy.db'

@app.route('/recommendations')
def display_shoes():
    shoes = []

    for shoe in query_db('select * from sneakers ORDER BY hype_avg_score DESC'): 
        shoes.append(shoe)

    return render_template('recommendations.html', owned=shoes)

@app.route('/sneaker/<sneaker_model>')
def display_model_details(sneaker_model):
    shoes = []
    sneaker_model = sneaker_model.replace(' ', '-')
    for shoe in query_db("select * from sneakers WHERE [Model Name]=?", [sneaker_model]): 
        shoes.append(shoe)

    shoe = ''
    if len(shoes) != 0:
    	shoe = shoes[0]['Model Name']

    return render_template('model_details.html', model=shoe)

@app.template_filter('format_model_name')
def remove_dashes(text):
    return text.replace('-', ' ')

@app.template_filter('format_price')
def format_price(text):
    return '${:,}'.format(int(text))

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
