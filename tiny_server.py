from flask import Flask, render_template, request, abort, jsonify

import boto3
from botocore.errorfactory import ClientError
### AWS credentials are stored in the ".aws" directory which gets put in the user's home directory during installation of BOTO

import hashlib

import redis

app = Flask(__name__)

# set max upload size to 20MB ... (1024 bytes = 1 kb | 1024 bytes * 1024 = 1 mb -- 20 * 1024 * 1024 = ~20 mb)
# app.config['MAX_CONTENT_LENGTH'] = 20 * 1024 * 1024

@app.route('/test')
def test():
  return 'test'

@app.route('/', methods=['GET', 'POST'])
def index():
  
  message = '' 
  filename = ''

  # check if a submission happened
  if request.method == 'POST':
    
    # connect to amazon s3
    s3 = boto3.resource('s3')

    # loop over submitted files list
    data_files = request.files.getlist('file')
    for data_file in data_files:

      content_length = request.content_length
      if content_length is not None and content_length > 20 * 1024 * 1024:
          abort(413)

      # if there is no file, don't upload it!
      if data_file.filename != '':

        file_contents = data_file.read()

        # hash the file contents
        hashed_file = hashlib.sha256(file_contents)

        # split on the first occurence of the '.' character, return the second position of the dict, lowercase it for consistency
        file_extension = data_file.filename.split('.', 1)[1].lower()
        file_name = hashed_file.hexdigest() + '.' + file_extension

        # upload file to bucket
        s3.Bucket('nusa-jschoen-resizeimage-origin').put_object(Key=file_name, Body=file_contents)

        message = 'submitted!'
        
        # return file_name as post body
        return file_name

      else:
        message = 'no file uploaded'

  # render_template() looks in the templates directory
  return render_template('upload_page.html', message = message)




@app.route('/status', methods=['GET'])
def status():

  file_name = request.args['filename']

  # get users ip
  ip = request.remote_addr

  # connect to redis
  r = _connect_redis()

  # check redis to see if we're waiting on the file to be processed
  if r.get(file_name) == None:
    print 'Redis: key not found.'

    # check if file has been processed yet
    if not check_file_exists(file_name):
      print 'S3: target not found.'

      # if key doesn't exist in redis, add it
      if r.get(file_name) == None:
        print 'Redis: adding key.'

        # set the key to expire 30 seconds from now
        r.setex(file_name, 4, ip)
      
      data = { "status": "file_processing" }

    # file exists
    else:
      print 'S3: target found.'

      # generate a signed url... ie, it can be used once
      s3 = boto3.client('s3')
      presigned_url = s3.generate_presigned_url(
        'get_object',
        Params = {
          'Bucket': 'nusa-jschoen-resizeimage-target', 
          'Key': file_name
        }
      )

      data = { "status": "file_ready", "url": presigned_url }

  else:
    print 'Redis: key found.'
    data = { "status": "file_processing" }

  return jsonify(data)




def check_file_exists(file_name):
  # connect to s3
  s3 = boto3.client('s3')

  # check target bucket for our file
  try:
    print s3.head_object(Bucket='nusa-jschoen-resizeimage-target', Key=file_name)
    return True
  except ClientError as e:
    # Not Found
    print e
    return False




def _connect_redis():
  return redis.StrictRedis(host='localhost', port='6379', db=0)




