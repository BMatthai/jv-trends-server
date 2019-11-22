from flask import Flask, request

app = Flask(__name__)

@app.route("/trends", methods = ['GET'])
def trends():
	f = open("topic_file.txt", "r")		
	return f.read(), 200


