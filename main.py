from flask import Flask, g, render_template, request, redirect
import flask_login
import operator
import os
import sqlite3

app = Flask(__name__)
app.secret_key = 'sneakerbuddiez4lyf'
project_dir = os.path.dirname(os.path.abspath(__file__))
DATABASE = 'db/sneakerbuddy.db'

db_file_path = "sqlite:///{}".format(os.path.join(project_dir, DATABASE))

app.config['SQLALCHEMY_DATABASE_URI'] = db_file_path

# login_manager = flask_login.LoginManager()
# login_manager.init_app(app)


# @login_manager.user_loader
# def user_loader(username):
#     users = query_db("select * from users WHERE username=?", [username])
#     user = next(iter(users), None)

#     if user is None:
#          return

#     user = User()
#     user.username = username
#     print(user)
#     return user

# @login_manager.request_loader
# def request_loader(request):
#     username = request.form.get('username')
#     users = query_db("select * from users WHERE username=?", [username])
#     user = next(iter(users), None)

#     if user is None:
#         return

#     new_user = User(user['username'], request.form.get('password'), user['salt'])

#     # DO NOT ever store passwords in plaintext and always compare password
#     # hashes using constant-time comparison!
#     new_user.is_authenticated = new_user.check_password(user['hashed_pw'])
#     print(new_user)
#     return new_user

# @app.route('/login', methods=['GET', 'POST'])
# def login(head="Sign in here"):
#     if request.method == 'GET':
#         return '''
#                <form action='login' method='POST'>
#                 <h2>{}</h2>
#                 <input type='text' name='username' id='username' placeholder='username'/>
#                 <br />
#                 <input type='password' name='password' id='password' placeholder='password'/>
#                 <br />
#                 <input type='submit' name='submit'/>
#                </form>
#                '''.format(head)
#     else:
#         username = request.form['username']
#         users = query_db('select * from users WHERE username=?', [username], False)
#         if len(users) == 0:
#             return 'User not found. <a href="/login">Login again</a>'
#         db_user = next(iter(users))
#         print(db_user)
#         ## if db hashed_pass == bcrypt.hashpw(input, db salt)
#         user = User(db_user['username'], request.form['password'], db_user['salt'])
#         if user.check_password(db_user['hashed_pw']):
#             flask_login.login_user(user)
#             return redirect(url_for('protected'))
#         else:
#             return 'Bad login. <a href="/login">Login again</a>'

# @app.route('/protected')
# @flask_login.login_required
# def protected():
#     print(flask_login.current_user)
#     return 'Logged in as: ' + flask_login.current_user.username

# @app.route('/register/<username>/<password>')
# def register(username, password):
#     u = User(username, password)
   
#     res = query_db("insert into users VALUES (null, ?, ?, ?)", [u.username, u.salt, u.hashed_pass], True)

#     return str(res)

@app.route('/recommendations/<user_type>')
def display_shoes(user_type):
    shoes = {}
    defaultShoeList = []
    ownedShoes = []

    for shoe in query_db('select * from sneakers'): 
        shoes[shoe['Model Name']] = shoe
        if len(defaultShoeList) < 10:
            defaultShoeList.append(shoe)

    for ownedShoe in query_db('select * from owned'):
        ownedShoes.append(ownedShoe['model'])

    if not ownedShoes:
        return render_template('recommendations.html', recs=defaultShoeList)

    recScore = generate_recommendations(shoes, ownedShoes, user_type)
    sellerRecScore = generate_seller_recommendations(shoes, ownedShoes)
    recommendations = []
    sellerRecommendations = []

    numShoes = min(10, len(sellerRecScore.items()))

    for i in range(0, 10):
        model = max(recScore.items(), key=operator.itemgetter(1))[0]
        recScore.pop(model, None)
        recommendations.append(shoes[model])

    if user_type == 'investor':
        for i in range(0, numShoes):
            model = max(sellerRecScore.items(), key=operator.itemgetter(1))[0]
            sellerRecScore.pop(model, None)
            sellerRecommendations.append(shoes[model])
        print(sellerRecommendations)
        return render_template('investor_recs.html', recs=recommendations, sellerRecs=sellerRecommendations)        
    return render_template('recommendations.html', recs=recommendations, sellerRecs=sellerRecommendations)

def generate_recommendations(shoes, owned, user_type='collector'):
    recScore = {}
    for shoe in shoes:
        if shoe not in owned:
            recScore[shoe] = 0
    # If collector, use colors n whatnot
    # else, it's an investor. use price prediction for seller first
    if user_type == 'collector':
        for shoe in recScore:
            for ownedShoe in owned:
                for color in shoes[shoe]['Color'].split(' '):
                    for otherColor in shoes[ownedShoe]['Color'].split(' '):
                        if color == otherColor:
                            recScore[shoe] += 5
                if shoes[shoe]['Brand'] == shoes[ownedShoe]['Brand']:
                    recScore[shoe] += 10
    else:
        for shoe in recScore:
            price_pred = query_db('select * from predictions where [Sneaker Name]=?', [shoe])
            sorted_preds_date = sorted(price_pred, key=lambda kv: (int(kv['date'].split('/')[0]), int(kv['date'].split('/')[1]), int(kv['date'].split('/')[2])), reverse=True)[0]
            sales = query_db('select * from sales where [Sneaker Name]=?', [shoe])
            sorted_sales_date = sorted(sales, key=lambda kv: (int(kv['Order Date'].split('/')[2]), int(kv['Order Date'].split('/')[0]), int(kv['Order Date'].split('/')[1])), reverse=True)[0]
            recScore[shoe] = sorted_preds_date['yhat'] / int(sorted_sales_date['Sale Price'][1:].replace(',', ''))
    return recScore

def generate_seller_recommendations(shoes, owned):
    recScore = {}
    for shoe in shoes:
        if shoe in owned:
            recScore[shoe] = 0
    # If collector, use colors n whatnot
    # else, it's an investor. use price prediction for seller first
    for shoe in recScore:
        price_pred = query_db('select * from predictions where [Sneaker Name]=?', [shoe])
        sorted_preds_date = sorted(price_pred, key=lambda kv: (int(kv['date'].split('/')[0]), int(kv['date'].split('/')[1]), int(kv['date'].split('/')[2])), reverse=True)[0]
        sales = query_db('select * from sales where [Sneaker Name]=?', [shoe])
        sorted_sales_date = sorted(sales, key=lambda kv: (int(kv['Order Date'].split('/')[2]), int(kv['Order Date'].split('/')[0]), int(kv['Order Date'].split('/')[1])), reverse=True)[0]
        recScore[shoe] = sorted_preds_date['yhat'] / int(sorted_sales_date['Sale Price'][1:].replace(',', ''))
    return recScore

@app.route('/')
def hello():
    return redirect('/portfolio', code=302)

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
    select = request.form.get('sneaker_select').replace(' ', '-')
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
        sales.append(sale)
    sales.sort(key = lambda sale: sale['Day After Release'])
    mostRecent = sales[len(sales)-5:len(sales)]
    mostRecent.reverse()

    predictions = []
    for prediction in query_db("select * from predictions where [Sneaker Name]=?", [sneaker_model]):
        predictions.append(prediction)

    return render_template('model_details.html', model=shoe, sales=sales, mostRecent=mostRecent, predictions=predictions)

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

def query_db(query, args=(), commit=False, one=False):
    cur = get_db().execute(query, args)
    if commit:
        get_db().commit()
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
