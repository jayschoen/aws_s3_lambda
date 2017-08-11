from flask import Flask

app = Flask(__name__)

@app.route('/test')
def test():
  return 'test'

@app.route('/upload-image')
def upload_image():
  return 'uploading image... TEST'
