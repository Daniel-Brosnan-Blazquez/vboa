#################################################################
#
# Init docker environment of the vboa and its tailored app
#
# Written by DEIMOS Space S.L. (dibb)
#
# module vboa
#################################################################

USAGE="Usage: `basename $0` -d path_to_docker_image -i path_to_external_inputs_folder -b path_to_boa_ddbb -r path_to_rboa_archive -o path_to_orc_ddbb -m path_to_minarc_archive [-p port] [-l containers_label]"

########
# Initialization
########
PORT="5000"
CONTAINERS_LABEL="dev"
PATH_TO_BOA_INPUTS=""
PATH_TO_BOA_DDBB=""
PATH_TO_RBOA_ARCHIVE=""
PATH_TO_ORC_DDBB=""
PATH_TO_MINARC_ARCHIVE=""

while getopts d:p:l:i:b:r:o:m: option
do
    case "${option}"
        in
        d) PATH_TO_DOCKERIMAGE=${OPTARG};;
        p) PORT=${OPTARG};;
        l) CONTAINERS_LABEL=${OPTARG};;
        i) PATH_TO_BOA_INPUTS=${OPTARG};;
        b) PATH_TO_BOA_DDBB=${OPTARG};;
        r) PATH_TO_RBOA_ARCHIVE=${OPTARG};;
        o) PATH_TO_ORC_DDBB=${OPTARG};;
        m) PATH_TO_MINARC_ARCHIVE=${OPTARG};;
        ?) echo -e $USAGE
            exit -1
    esac
done

# Check that option -d has been specified
if [ "$PATH_TO_DOCKERIMAGE" == "" ];
then
    echo "ERROR: The option -d has to be provided"
    echo $USAGE
    exit -1
fi

# Check that the docker image exists
if [ ! -f $PATH_TO_DOCKERIMAGE ];
then
    echo "ERROR: The file $PATH_TO_DOCKERIMAGE provided does not exist"
    exit -1
fi

# Check that option -i has been specified
if [ "$PATH_TO_BOA_INPUTS" == "" ];
then
    echo "ERROR: The option -i has to be provided"
    echo $USAGE
    exit -1
fi

# Check that the path to the inputs folder exists
if [ ! -d $PATH_TO_BOA_INPUTS ];
then
    echo "ERROR: The directory $PATH_TO_BOA_INPUTS provided does not exist"
    exit -1
fi

# Check that option -b has been specified
if [ "$PATH_TO_BOA_DDBB" == "" ];
then
    echo "ERROR: The option -b has to be provided"
    echo $USAGE
    exit -1
fi

# Check that the path to the BOA DDBB folder exists
if [ ! -d $PATH_TO_BOA_DDBB ];
then
    echo "ERROR: The directory $PATH_TO_BOA_DDBB provided does not exist"
    exit -1
fi

# Check that option -r has been specified
if [ "$PATH_TO_RBOA_ARCHIVE" == "" ];
then
    echo "ERROR: The option -r has to be provided"
    echo $USAGE
    exit -1
fi

# Check that the path to the RBOA archive folder exists
if [ ! -d $PATH_TO_RBOA_ARCHIVE ];
then
    echo "ERROR: The directory $PATH_TO_RBOA_ARCHIVE provided does not exist"
    exit -1
fi

# Check that option -o has been specified
if [ "$PATH_TO_ORC_DDBB" == "" ];
then
    echo "ERROR: The option -o has to be provided"
    echo $USAGE
    exit -1
fi

# Check that the path to the ORC DDBB folder exists
if [ ! -d $PATH_TO_ORC_DDBB ];
then
    echo "ERROR: The directory $PATH_TO_ORC_DDBB provided does not exist"
    exit -1
fi

# Check that option -m has been specified
if [ "$PATH_TO_MINARC_ARCHIVE" == "" ];
then
    echo "ERROR: The option -m has to be provided"
    echo $USAGE
    exit -1
fi

# Check that the path to the MINARC archive folder exists
if [ ! -d $PATH_TO_MINARC_ARCHIVE ];
then
    echo "ERROR: The directory $PATH_TO_MINARC_ARCHIVE provided does not exist"
    exit -1
fi

DATABASE_CONTAINER="boa_database_$CONTAINERS_LABEL"
APP_CONTAINER="boa_app_$CONTAINERS_LABEL"
DOCKER_NETWORK="boa_network_$CONTAINERS_LABEL"

read -p "
Welcome to the builder of the BOA environment :-)

You are trying to initialize a new development environment for the app: $APP...
These are the configuration options that will be applied to initialize the environment:
- PATH_TO_DOCKERIMAGE: $PATH_TO_DOCKERIMAGE
- PORT: $PORT
- CONTAINERS_LABEL: $CONTAINERS_LABEL
- PATH_TO_BOA_INPUTS: $PATH_TO_BOA_INPUTS
- PATH_TO_BOA_DDBB: $PATH_TO_BOA_DDBB
- PATH_TO_RBOA_ARCHIVE: $PATH_TO_RBOA_ARCHIVE
- PATH_TO_ORC_DDBB: $PATH_TO_ORC_DDBB
- PATH_TO_MINARC_ARCHIVE: $PATH_TO_MINARC_ARCHIVE

Do you wish to proceed with the building of the production environment?" answer

if [ "$(docker ps -a | grep -w $DATABASE_CONTAINER)" ];
then
    while true; do
        read -p "There has been detected a container with the same name: $DATABASE_CONTAINER. Do you wish to remove it and proceed with the new installation?" answer
        case $answer in
            [Yy]* )
                # Remove eboa database container if it already exists
                docker stop $DATABASE_CONTAINER
                docker rm $DATABASE_CONTAINER
                break;;
            [Nn]* ) exit;;
            * ) read -p "Please answer Y or y for yes or N or n for no: " answer;;
        esac
    done
fi

if [ "$(docker ps -a | grep -w $APP_CONTAINER)" ];
then
    while true; do
        read -p "There has been detected a container with the same name: $APP_CONTAINER. Do you wish to remove it and proceed with the new installation?" answer
        case $answer in
            [Yy]* )
                # Remove app image and container if it already exists
                docker stop $APP_CONTAINER
                docker rm $APP_CONTAINER

                break;;
            [Nn]* ) exit;;
            * ) echo "Please answer Y or y for yes or N or n for no.";;
        esac
    done
fi

######
# Create network
######
docker network inspect $DOCKER_NETWORK &>/dev/null || docker network create --driver bridge $DOCKER_NETWORK

######
# Create database container
######
# Execute container
# Check configuration of postgis/postgres with -> psql -U postgres -> show all;
docker run --shm-size 512M --network=$DOCKER_NETWORK --name $DATABASE_CONTAINER -v $PATH_TO_BOA_DDBB:/var/lib/postgresql/data -d mdillon/postgis -c 'max_connections=5000' -c 'max_locks_per_transaction=5000'

######
# Create APP container
######
docker load -i $PATH_TO_DOCKERIMAGE

docker run --shm-size 512M --network=$DOCKER_NETWORK -p $PORT:5000 -it --name $APP_CONTAINER -v $PATH_TO_ORC_DDBB:/var/lib/pgsql/data -v $PATH_TO_MINARC_ARCHIVE:/minarc_root -v $PATH_TO_BOA_INPUTS:/inputs -v $PATH_TO_RBOA_ARCHIVE:/rboa_archive --restart=always -d `basename $PATH_TO_DOCKERIMAGE .tar`

# Change port and address configuration of the eboa defined by the postgis container
docker exec -it -u boa $APP_CONTAINER bash -c "sed -i 's/\"host\".*\".*\"/\"host\": \"$DATABASE_CONTAINER\"/' /resources_path/datamodel.json"

# Execute web server
docker exec -d -it -u boa $APP_CONTAINER bash -c "source scl_source enable rh-ruby25; gunicorn -b 0.0.0.0:5000 -w 12 $FLASK_APP.wsgi:app -D"

echo "
Docker environment successfully built :-)"
