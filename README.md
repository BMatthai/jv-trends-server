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

Example of response:
{
    "top": 3,
    "begin": 30,
    "end": 0,
    "topics": [
        {
            "title": "Discrimination à l'embauche : Étude officielle",
            "link": "/forums/42-51-61786220-1-0-1-0-discrimination-a-l-embauche-etude-officielle.htm",
            "oldval": 135.0,
            "newval": 246.0,
            "delta": 111.0
        },
        {
            "title": "[STAR WARS] Qui est le Jedi ou Sith le plus puissant ?",
            "link": "/forums/42-51-61804537-1-0-1-0-star-wars-qui-est-le-jedi-ou-sith-le-plus-puissant.htm",
            "oldval": 63.0,
            "newval": 170.0,
            "delta": 107.0
        },
        {
            "title": "Est-ce normal de se sentir supérieur parce qu'on lit beaucoup ?",
            "link": "/forums/42-51-61849239-1-0-1-0-est-ce-normal-de-se-sentir-superieur-parce-qu-on-lit-beaucoup.htm",
            "oldval": 2.0,
            "newval": 107.0,
            "delta": 105.0
        }
    ]
}
