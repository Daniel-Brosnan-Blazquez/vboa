# Script to start the web server in development mode
source scl_source enable rh-ruby25; flask run --host=0.0.0.0 -p 4000
nginx
