#################################################################
#
# Init docker environment of the vboa and its tailored app
#
# Written by DEIMOS Space S.L. (dibb)
#
# module vboa
#################################################################

USAGE="Usage: `basename $0` -e path_to_eboa_src -v path_to_vboa_src -d path_to_dockerfile [-p port] [-t path_to_tailored] [-l containers_label] [-a app] [-c eboa_resources_path]"

########
# Initialization
########
PATH_TO_EBOA=""
PATH_TO_VBOA=""
PATH_TO_DOCKERFILE="Dockerfile"
PORT="5000"
PATH_TO_TAILORED=""
CONTAINERS_LABEL="dev"
APP="vboa"
EBOA_RESOURCES_PATH="/eboa/src/config"

while getopts e:v:d:p:t:l:a:c: option
do
    case "${option}"
        in
        e) PATH_TO_EBOA=${OPTARG};;
        v) PATH_TO_VBOA=${OPTARG};;
        d) PATH_TO_DOCKERFILE=${OPTARG};;
        p) PORT=${OPTARG};;
        t) PATH_TO_TAILORED=${OPTARG};;
        l) CONTAINERS_LABEL=${OPTARG};;
        a) APP=${OPTARG};;
        c) EBOA_RESOURCES_PATH=${OPTARG};;
        ?) echo -e $USAGE
            exit -1
    esac
done

# Check that option -e has been specified
if [ "$PATH_TO_EBOA" == "" ];
then
    echo "ERROR: The option -e has to be provided"
    echo $USAGE
    exit -1
fi

# Check that the path to the eboa project exists
if [ ! -d $PATH_TO_EBOA ];
then
    echo "ERROR: The directory $PATH_TO_EBOA provided does not exist"
    exit -1
fi

# Check that option -v has been specified
if [ "$PATH_TO_VBOA" == "" ];
then
    echo "ERROR: The option -v has to be provided"
    echo $USAGE
    exit -1
fi

# Check that the path to the vboa project exists
if [ ! -d $PATH_TO_VBOA ];
then
    echo "ERROR: The directory $PATH_TO_VBOA provided does not exist"
    exit -1
fi

# Check that option -d has been specified
if [ "$PATH_TO_DOCKERFILE" == "" ];
then
    echo "ERROR: The option -d has to be provided"
    echo $USAGE
    exit -1
fi

# Check that the docker file exists
if [ ! -f $PATH_TO_DOCKERFILE ];
then
    echo "ERROR: The file $PATH_TO_DOCKERFILE provided does not exist"
    exit -1
fi

# Check that the path to the tailored project exists
if [ "$PATH_TO_TAILORED" != "" ] && [ ! -d $PATH_TO_TAILORED ];
then
    echo "ERROR: The directory $PATH_TO_TAILORED provided does not exist"
    exit -1
fi

# Check that the path to the tailored project exists
if [ ! -d $EBOA_RESOURCES_PATH ];
then
    echo "ERROR: The directory $EBOA_RESOURCES_PATH provided does not exist"
    exit -1
fi

DATABASE_CONTAINER="boa-database-$CONTAINERS_LABEL"
APP_CONTAINER="boa-app-$CONTAINERS_LABEL"

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
            * ) echo "Please answer Y or y for yes or N or n for no.";;
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
                docker rmi $(docker images boa -q)

                break;;
            [Nn]* ) exit;;
            * ) echo "Please answer Y or y for yes or N or n for no.";;
        esac
    done
fi

######
# Create database container
######
# Execute container
docker run  --name $DATABASE_CONTAINER -d mdillon/postgis

######
# Create APP container
######
find . -name *pyc -delete
docker build --build-arg FLASK_APP=$APP -t boa -f $PATH_TO_DOCKERFILE $PATH_TO_VBOA
# Initialize the eboa database
docker run -p $PORT:5000 -it --name $APP_CONTAINER --link $DATABASE_CONTAINER:boa -d -v $PATH_TO_EBOA:/eboa -v $PATH_TO_VBOA:/vboa -v $PATH_TO_TAILORED:/$APP -v $EBOA_RESOURCES_PATH:/resources_path boa
# Generate the python archive
docker exec -it $APP_CONTAINER bash -c "pip3 install --upgrade pip"
docker exec -it $APP_CONTAINER bash -c "pip3 install -e /eboa/src"
docker exec -it $APP_CONTAINER bash -c "pip3 install -e /vboa/src"
if [ "$PATH_TO_TAILORED" != "" ];
then
    docker exec -it $APP_CONTAINER bash -c "pip3 install -e /$APP/src"
fi

# Initialize the EBOA database inside the postgis-database container
status=255
while true
do
    echo "Trying to initialize database..."
    docker exec -it $APP_CONTAINER bash -c '/eboa/datamodel/init_ddbb.sh -h $BOA_PORT_5432_TCP_ADDR -p $BOA_PORT_5432_TCP_PORT -f /eboa/datamodel/eboa_data_model.sql' > /dev/null
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
docker exec -it $APP_CONTAINER bash -c 'sed -i "s/\"host\".*\".*\"/\"host\": \"$BOA_PORT_5432_TCP_ADDR\"/" /resources_path/datamodel.json'
docker exec -it $APP_CONTAINER bash -c 'sed -i "s/\"port\".*\".*\"/\"port\": \"$BOA_PORT_5432_TCP_PORT\"/" /resources_path/datamodel.json'

# Execute flask server
docker exec -d -it $APP_CONTAINER bash -c 'flask run --host=0.0.0.0 -p 5000'

# Install web packages
docker exec -it $APP_CONTAINER bash -c "npm --prefix /vboa/src/vboa/static install"

# Listen for changes on the web packages
docker exec -d -it $APP_CONTAINER bash -c "npm --prefix /vboa/src/vboa/static run watch"
