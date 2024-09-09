# Script to start the web server in development mode
nohup npm --prefix /vboa/src/vboa/static run test &> /log/npm.log &

# Start flask server on port 5000 for testing purposes
export VBOA_DEBUG=FALSE; export VBOA_TEST=TRUE; nohup flask run --host=0.0.0.0 -p 5000 &> /log/flask_5000.log &

# Start flask server on port 5001 for SSL connection
# Create certificates if they are not available
if [ ! -f /resources_path/boa_certificate.pem ] || [ ! -f /resources_path/boa_key.pem ];
then
    openssl req -x509 -newkey rsa:4096 -nodes -out /resources_path/boa_certificate.pem -keyout /resources_path/boa_key.pem -subj "/emailAddress=daniel.brosnan@elecnor.es/C=SP/ST=Madrid/L=Tres Cantos/O=Elecnor Deimos/OU=Ground Segment/CN=BOA"
fi
export VBOA_DEBUG=TRUE; export VBOA_TEST=TRUE; nohup flask run --cert=/resources_path/boa_certificate.pem --key=/resources_path/boa_key.pem  --host=0.0.0.0 -p 5001 &> /log/flask_5001.log &

sleep infinity
