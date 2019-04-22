#############################################################
#############################################################
DESCRIPTION: 

Sneakerbuddy is an assistant web application 
for StockX, a resale marketplace for limited edition
sneakers and apparel. We created this to aid in the 
decision-making process for all sneakerheads -- by devising
two main interfaces, one for sneaker collectors and one for
investors (looking to buy or sell), we can pinpoint what
data analysis or recommendations that user type would be 
interested in. 

This application provides personalized recommendations by
leveraging statistical models for price prediction in
conjunction with various sneaker metadata based on the user's
intention to buy, keep, or resell. Each user type receives
recommendations based on unique scoring algorithms comparing
owned and prospective shoes to each other -- this is critical
in providing the most accurate information for each user's
situation.

This application was created mostly in the Flask framework
for lightweight Python backends. Server-side rendering
uses the Jinja2 templating engine, as well as D3 to serve 
various graphical components. Data was stored in-file, using
sqlite.



#############################################################
#############################################################
INSTALLATION: 

It is recommended to use Python virtual environments in some
capacity. Once an isolated environment with Python3 is up,
simply cd into the main directory and run either:

`pip install -r requirements.txt`

or 

`pip3 install -r requirements.txt`.


If this approach does not work for you, or you think you do
not need virtual environments, simply open the 
requirements.txt file and manually add dependencies. Using
pip to first install Flask and flask_login would be good to
check if working. This is not recommended, but should work.



#############################################################
#############################################################
EXECUTION:

Once the dependencies are installed, simply run the following
command:

`python main.py`

or

`python3 main.py`.

This will serve up a Flask server, initiating the web app
for service at:

`localhost:5000`.

Use the back button to go through various windows, such as
portfolio add/drop and recommendations.