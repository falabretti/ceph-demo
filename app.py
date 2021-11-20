from flask import Flask, render_template, request, redirect, jsonify
from flask.helpers import url_for
import client

app = Flask(__name__)

app.config['ENV'] = 'development'
app.config['TEMPLATES_AUTO_RELOAD'] = True
app.config['DEBUG'] = True

@app.route('/', methods=['GET'])
def index():
    buckets = client.list_buckets()
    return render_template('index.html', buckets=buckets)

@app.route('/', methods=['POST'])
def create_bucket():
    bucket = request.form['name']
    return redirect(f'/{bucket}')

@app.route('/<bucket>', methods=['GET'])
def files(bucket):
    objects = client.list_objects(bucket)
    return render_template('objects.html', bucket=bucket, objects=objects)

@app.route('/<bucket>', methods=['POST'])
def upload_object(bucket):
    file = request.files['file']
    print(file)
    client.upload_object(file, bucket)
    return redirect(f'/{bucket}')

@app.route('/<bucket>/<key>', methods=['DELETE'])
def delete_object(bucket, key):
    client.delete_object(bucket, key)
    return jsonify(success=True)

app.run(port=80)
