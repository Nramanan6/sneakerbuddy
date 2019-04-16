import sqlite3
from flask import Flask, g, render_template, request

app = Flask(__name__)
DATABASE = 'db/sneakerbuddy.db'

@app.route('/recommendations')
def display_shoes():
    shoes = []

    for shoe in query_db('select * from sneakers ORDER BY hype_avg_score DESC limit 10'): 
        shoes.append(shoe)

    return render_template('recommendations.html', recs=shoes)

@app.route('/portfolio')
def display_owned():
    shoes = []
    owned = []
    for shoe in query_db('select * from sneakers'): 
        shoes.append(shoe)
    for shoe in query_db('select * from owned'):
    	owned.append(shoe)

    return render_template('portfolio.html', all_shoes=shoes, owned=owned)

@app.route('/add_owned_sneaker', methods=['POST'])
def submit_owned():
	select = request.form.get('sneaker_select')
	size = request.form.get('size_select')
	query_db('insert into owned(username, model, size) values(?,?,?)', ['testuser', select, size])
	shoes = []
	owned = []
	for shoe in query_db('select * from sneakers'): 
		shoes.append(shoe)
	for shoe in query_db('select * from owned'):
		owned.append(shoe)
	return render_template('portfolio.html', all_shoes=shoes, owned=owned)

@app.route('/remove_owned_sneaker', methods=['POST'])
def remove_owned():
	ownedId = request.form.get('owned_id')
	query_db('delete from owned where id=?', [ownedId])
	shoes = []
	owned = []
	for shoe in query_db('select * from sneakers'): 
		shoes.append(shoe)
	for shoe in query_db('select * from owned'):
		owned.append(shoe)
	return render_template('portfolio.html', all_shoes=shoes, owned=owned)

@app.route('/sneaker/<sneaker_model>')
def display_model_details(sneaker_model):
    shoes = []
    sneaker_model = sneaker_model.replace(' ', '-')
    for shoe in query_db("select * from sneakers WHERE [Model Name]=?", [sneaker_model]): 
        shoes.append(shoe)

    shoe = ''
    if len(shoes) != 0:
    	shoe = shoes[0]['Model Name']

    sales = []
    for sale in query_db("select * from sales where [Sneaker Name]=?", [sneaker_model]):
    	sale['splitDate'] = sale['Order Date'].split('/')
    	sales.append(sale)
    sales.sort(key = lambda sale: (int(sale['splitDate'][2]), int(sale['splitDate'][0]), int(sale['splitDate'][1])))
    mostRecent = sales[len(sales)-5:len(sales)]
    mostRecent.reverse()

    return render_template('model_details.html', model=shoe, sales=sales, mostRecent=mostRecent)

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
        db = g._database = sqlite3.connect(DATABASE, isolation_level=None)
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
