from flask import Flask, render_template, request

app = Flask(__name__)

@app.route('/test')
def test():
  return 'test'

@app.route('/', methods=['GET', 'POST'])
def index():
  
  message = '' 

  # check if a submission happened
  if request.method == 'POST':
    message = 'submit test'

  # render_template() looks in the templates directory
  return render_template('upload_page.html', message = message)
