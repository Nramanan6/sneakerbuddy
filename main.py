from flask import Flask, render_template
app = Flask(__name__)


@app.route("/")
def template_test():
    return render_template('recommendations.html', owned=["Off-White", "Raf", "Yeezy"])


if __name__ == '__main__':
    app.run(debug=True)