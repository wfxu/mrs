from flask import Flask, render_template


app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/movie/', methods=['GET', 'POST'])
def movie():
    return render_template('movie.html')


@app.route('/user/', methods=['GET', 'POST'])
def user():
    return render_template('user.html')


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=80)
