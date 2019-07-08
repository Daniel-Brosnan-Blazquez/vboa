#################################################################
#
# Init docker environment of the vboa
#
# Written by DEIMOS Space S.L. (dibb)
#
# module vboa
#################################################################

USAGE="Usage: `basename $0` -e path_to_eboa_src -p path_to_vboa_src"
PATH_TO_EBOA_SRC=""
PATH_TO_VBOA_SRC=""

while getopts p:e: option
do
    case "${option}"
        in
        e) PATH_TO_EBOA_SRC=${OPTARG};;
        p) PATH_TO_VBOA_SRC=${OPTARG};;
        ?) echo -e $USAGE
            exit -1
    esac
done

# Check that option -e has been specified
if [ "$PATH_TO_EBOA_SRC" == "" ];
then
    echo "ERROR: The option -e has to be provided"
    echo $USAGE
    exit -1
fi

# Check that the path to the eboa project exists
if [ ! -d $PATH_TO_EBOA_SRC ];
then
    echo "ERROR: The directory $PATH_TO_EBOA_SRC provided does not exist"
    exit -1
fi

# Check that option -p has been specified
if [ "$PATH_TO_VBOA_SRC" == "" ];
then
    echo "ERROR: The option -p has to be provided"
    echo $USAGE
    exit -1
fi

# Check that the path to the eboa project exists
if [ ! -d $PATH_TO_VBOA_SRC ];
then
    echo "ERROR: The directory $PATH_TO_VBOA_SRC provided does not exist"
    exit -1
fi

######
# Create EBOA database container
######
# Remove eboa database container if it already exists
docker stop eboa-database-container
docker rm eboa-database-container
# Execute container
docker run  --name eboa-database-container -d mdillon/postgis

######
# Create EBOA and VBOA container
######
# Remove eboa and vboa image and container if it already exists
docker stop eboa-vboa-container
docker rm eboa-vboa-container
docker rmi $(docker images eboa-vboa -q)
find . -name *pyc -delete
docker build -t eboa-vboa .
# Initialize the eboa database
docker run -p 8000:5000 -it --name eboa-vboa-container --link eboa-database-container:eboa-vboa -d -v $PATH_TO_EBOA_SRC:/eboa -v $PATH_TO_VBOA_SRC:/vboa eboa-vboa
# Generate the python archive
PATH_TO_DOCKERFILE=$PWD
cd $PATH_TO_EBOA_SRC/src
rm -r dist
python3 setup.py sdist
cd $PATH_TO_DOCKERFILE
docker exec -it eboa-vboa-container bash -c "pip3 install --upgrade pip"
docker exec -it eboa-vboa-container bash -c "pip3 install /eboa/src/dist/*"
cd $PATH_TO_VBOA_SRC/src
rm -r dist
python3 setup.py sdist
cd $PATH_TO_DOCKERFILE
docker exec -it eboa-vboa-container bash -c "pip3 install --upgrade pip"
docker exec -it eboa-vboa-container bash -c "pip3 install /vboa/src/dist/*"

# Initialize the EBOA database inside the postgis-database container
status=255
while true
do
    echo "Trying to initialize database..."
    docker exec -it eboa-vboa-container bash -c '/eboa/datamodel/init_ddbb.sh -h $EBOA_VBOA_PORT_5432_TCP_ADDR -p $EBOA_VBOA_PORT_5432_TCP_PORT -f /eboa/datamodel/eboa_data_model.sql' > /dev/null
    status=$?
    if [ $status -ne 0 ]
    then
        echo "Server is not ready yet..."
        # Wait for the server to be initialize
        sleep 1
    else
        echo "Database has been initialized..."
        break
    fi
done
# Change port and address configuration of the eboa defined by the postgis container
docker exec -it eboa-vboa-container bash -c 'sed -i "s/localhost/$EBOA_VBOA_PORT_5432_TCP_ADDR/" /eboa/src/config/datamodel.json'
docker exec -it eboa-vboa-container bash -c 'sed -i "s/5432/$EBOA_VBOA_PORT_5432_TCP_PORT/" /eboa/src/config/datamodel.json'

