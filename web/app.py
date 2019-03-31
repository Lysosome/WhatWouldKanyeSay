from flask import Flask, render_template, request, url_for, redirect, flash
import wtforms
app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/result_page', methods = ['GET', 'POST'])
def result():
	select = request.form.get('personality')
	return(str(select))

if __name__ == '__main__':
   app.run(debug = True)