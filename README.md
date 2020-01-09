# jv-trends-server

## What is it ?

This repository contains a web application created using Python 3 and Flask framework.
Its purpose is to track the most active topics of any forums of the website jeuxvideo.com.

I also created a simple mobile app to watch datas. It is available [here](https://github.com/BMatthai/jv-trends-client-mobile/blob/master/README.md).

## Usage

You can deploy the web server by calling shell script "script.sh" or simply by running this command: 
*FLASK_APP=./jv-trends.py flask run --port 5000 --host=0.0.0.0*.
Ensure each dependencies listed in requirements.txt file is properly installed.

Program is runned once the first http request has been sent.
For example you can access: http://your-ip-address:5000/trends?top=10&begin=30&end=0.

This query will returns a JSON formatted response containing the 10 most actives topics of the period between 30 minutes (begin=30) and now (end=0).

## Preview
Here is a preview of what this script can returns using the query right above:

<img src="https://github.com/BMatthai/jv-trends-server/blob/master/resources/jv-trends-server-preview-1.png?raw=true" height="480" />
