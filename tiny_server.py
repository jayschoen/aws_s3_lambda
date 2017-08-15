from flask import Flask, render_template, request

import boto3

app = Flask(__name__)

@app.route('/test')
def test():
  return 'test'

@app.route('/', methods=['GET', 'POST'])
def index():
  
  message = '' 

  # check if a submission happened
  if request.method == 'POST':
    
    # connect to amazon s3
    s3 = boto3.resource('s3')

    # loop over submitted files list
    data_files = request.files.getlist('file[]')
    for data_file in data_files:

      file_contents = data_file.read()

      # upload file to bucket->folder
      #s3.Bucket('nusa-dev-testing').put_object(Key='jschoen/' + data_file.filename, Body=file_contents)

      #upload file to bucket
      s3.Bucket('nusa-jschoen-resizeimage-origin').put_object(Key=data_file.filename, Body=file_contents)

    message = 'submitted!'

  # render_template() looks in the templates directory
  return render_template('upload_page.html', message = message)
