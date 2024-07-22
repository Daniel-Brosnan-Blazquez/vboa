# VBOA: Visualization for Business Operation Analysis #

This component is the visulization tool for the Business Operation Analysis.
It offers all needed for visualizing data coming from [EBOA](https://github.com/danielbrosnan/eboa).

## Back-end ##
The back-end is entirely written in [Python](https://www.python.org/) and based on EBOA for retrieving the data requested. It uses [flask](http://flask.pocoo.org/) for offering a REST API for requests.

## Front-end ##
The front-end is written using [Jinja](https://en.wikipedia.org/wiki/Jinja_(template_engine)), [HTML](https://en.wikipedia.org/wiki/HTML), [CSS](https://en.wikipedia.org/wiki/Cascading_Style_Sheets) and [javascript](https://en.wikipedia.org/wiki/JavaScript) all combined with [webpack](https://webpack.js.org/) and [npm](https://www.npmjs.com/) for the process of packaging the needed libraries.
The production web server is based on [gunicorn](https://gunicorn.org/).
