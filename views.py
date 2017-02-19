from flask import Flask, render_template, request, url_for
app = Flask(__name__)

@app.route('/')
def index():
    return render_template('home.html')
@app.route('/intro1')
def intro1():
    return render_template('intro1.html')

@app.route('/intro2')
def intro2():
    return render_template('intro2.html')

@app.route('/encouragement')
def encouragement():
    return render_template('encouragement.html')

@app.route('/finish')
def finish():
    return render_template('finish.html')

@app.route('/graphs')
def intro1():
    return render_template('graphs.html')