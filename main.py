from flask import *
import flask_login
from models import User
import os
import sqlite3

app = Flask(__name__)
app.secret_key = 'sneakerbuddiez4lyf'
project_dir = os.path.dirname(os.path.abspath(__file__))
DATABASE = 'db/sneakerbuddy.db'

db_file_path = "sqlite:///{}".format(os.path.join(project_dir, DATABASE))

app.config['SQLALCHEMY_DATABASE_URI'] = db_file_path

login_manager = flask_login.LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def user_loader(username):
    users = query_db("select * from users WHERE username=?", [username])
    user = next(iter(users), None)

    if user is None:
         return

    user = User()
    user.username = username
    print(user)
    return user

@login_manager.request_loader
def request_loader(request):
    username = request.form.get('username')
    users = query_db("select * from users WHERE username=?", [username])
    user = next(iter(users), None)

    if user is None:
        return

    new_user = User(user['username'], request.form.get('password'), user['salt'])

    # DO NOT ever store passwords in plaintext and always compare password
    # hashes using constant-time comparison!
    new_user.is_authenticated = new_user.check_password(user['hashed_pw'])
    print(new_user)
    return new_user

@app.route('/login', methods=['GET', 'POST'])
def login(head="Sign in here"):
    if request.method == 'GET':
        return '''
               <form action='login' method='POST'>
                <h2>{}</h2>
                <input type='text' name='username' id='username' placeholder='username'/>
                <br />
                <input type='password' name='password' id='password' placeholder='password'/>
                <br />
                <input type='submit' name='submit'/>
               </form>
               '''.format(head)
    else:
        username = request.form['username']
        users = query_db('select * from users WHERE username=?', [username], False)
        if len(users) == 0:
            return 'User not found. <a href="/login">Login again</a>'
        db_user = next(iter(users))
        print(db_user)
        ## if db hashed_pass == bcrypt.hashpw(input, db salt)
        user = User(db_user['username'], request.form['password'], db_user['salt'])
        if user.check_password(db_user['hashed_pw']):
            flask_login.login_user(user)
            return redirect(url_for('protected'))
        else:
            return 'Bad login. <a href="/login">Login again</a>'

@app.route('/protected')
@flask_login.login_required
def protected():
    print(flask_login.current_user)
    return 'Logged in as: ' + flask_login.current_user.username

@app.route('/register/<username>/<password>')
def register(username, password):
    u = User(username, password)
   
    res = query_db("insert into users VALUES (null, ?, ?, ?)", [u.username, u.salt, u.hashed_pass], True)

    return str(res)

@app.route('/recommendations')
def display_shoes():
    shoes = []

    for shoe in query_db('select * from sneakers ORDER BY hype_avg_score DESC limit 10'): 
        shoes.append(shoe)

    return render_template('recommendations.html', recs=shoes)

@app.route('/portfolio')
def display_owned():
    shoes = []

    for shoe in query_db('select * from sneakers'): 
        shoes.append(shoe)

    return render_template('portfolio.html', all_shoes=shoes, owned=shoes)

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
        db = g._database = sqlite3.connect(DATABASE)
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
