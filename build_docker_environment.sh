#################################################################
#
# Init docker environment of the vboa and its tailored app
#
# Written by DEIMOS Space S.L. (dibb)
#
# module vboa
#################################################################

USAGE="Usage: `basename $0` -d path_to_docker_image -i path_to_external_inputs_folder -b path_to_boa_ddbb -r path_to_rboa_archive -m path_to_minarc_archive -s path_to_boa_certificates -o log_folder [-p port] [-l containers_label]\n
Where:\n
-s path_to_boa_certificates_and_secret_key: Path to SSL certificates which names should be boa_certificate.pem and boa_key.pem and to the secret key used for encripting cookies\n"

########
# Initialization
########
PORT="5000"
CONTAINERS_LABEL="dev"
PATH_TO_BOA_INPUTS=""
PATH_TO_BOA_DDBB=""
PATH_TO_RBOA_ARCHIVE=""
PATH_TO_MINARC_ARCHIVE=""
PATH_TO_BOA_CERTIFICATES_AND_SECRET_KEY=""
PATH_TO_LOG_FOLDER=""

while getopts d:p:l:i:b:r:m:s:o: option
do
    case "${option}"
        in
        d) PATH_TO_DOCKERIMAGE=${OPTARG};;
        p) PORT=${OPTARG};;
        l) CONTAINERS_LABEL=${OPTARG};;
        i) PATH_TO_BOA_INPUTS=${OPTARG};;
        b) PATH_TO_BOA_DDBB=${OPTARG};;
        r) PATH_TO_RBOA_ARCHIVE=${OPTARG};;
        m) PATH_TO_MINARC_ARCHIVE=${OPTARG};;
        s) PATH_TO_BOA_CERTIFICATES_AND_SECRET_KEY=${OPTARG};;
        o) PATH_TO_LOG_FOLDER=${OPTARG};;
        ?) echo -e $USAGE
            exit -1
    esac
done

# Check that option -d has been specified
if [ "$PATH_TO_DOCKERIMAGE" == "" ];
then
    echo "ERROR: The option -d has to be provided"
    echo -e $USAGE
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
    echo -e $USAGE
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
    echo -e $USAGE
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
    echo -e $USAGE
    exit -1
fi

# Check that the path to the RBOA archive folder exists
if [ ! -d $PATH_TO_RBOA_ARCHIVE ];
then
    echo "ERROR: The directory $PATH_TO_RBOA_ARCHIVE provided does not exist"
    exit -1
fi

# Check that option -m has been specified
if [ "$PATH_TO_MINARC_ARCHIVE" == "" ];
then
    echo "ERROR: The option -m has to be provided"
    echo -e $USAGE
    exit -1
fi

# Check that the path to the MINARC archive folder exists
if [ ! -d $PATH_TO_MINARC_ARCHIVE ];
then
    echo "ERROR: The directory $PATH_TO_MINARC_ARCHIVE provided does not exist"
    exit -1
fi

# Check that option -s has been specified
if [ "$PATH_TO_BOA_CERTIFICATES_AND_SECRET_KEY" == "" ];
then
    echo "ERROR: The option -s has to be provided"
    echo -e $USAGE
    exit -1
fi

# Check that the path to the BOA certificates exists
if [ ! -d $PATH_TO_BOA_CERTIFICATES_AND_SECRET_KEY ];
then
    echo "ERROR: The directory $PATH_TO_BOA_CERTIFICATES_AND_SECRET_KEY provided does not exist"
    exit -1
fi

# Check that the needed certificates are available
if [ ! -f $PATH_TO_BOA_CERTIFICATES_AND_SECRET_KEY/boa_certificate.pem ];
then
    echo "ERROR: The file $PATH_TO_BOA_CERTIFICATES_AND_SECRET_KEY/boa_certificate.pem does not exist"
    exit -1
fi
if [ ! -f $PATH_TO_BOA_CERTIFICATES_AND_SECRET_KEY/boa_key.pem ];
then
    echo "ERROR: The file $PATH_TO_BOA_CERTIFICATES_AND_SECRET_KEY/boa_key.pem does not exist"
    exit -1
fi

# Check that the needed secret key is available
if [ ! -f $PATH_TO_BOA_CERTIFICATES_AND_SECRET_KEY/web_server_secret_key.txt ];
then
    echo "ERROR: The file $PATH_TO_BOA_CERTIFICATES_AND_SECRET_KEY/web_server_secret_key.txt does not exist"
    exit -1
fi

# Check that option -o has been specified
if [ "$PATH_TO_LOG_FOLDER" == "" ];
then
    echo "ERROR: The option -o has to be provided"
    echo -e $USAGE
    exit -1
fi

# Check that the docker image exists
if [ ! -d $PATH_TO_LOG_FOLDER ];
then
    echo "ERROR: The directory $PATH_TO_LOG_FOLDER provided does not exist"
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
- PATH_TO_MINARC_ARCHIVE: $PATH_TO_MINARC_ARCHIVE
- PATH_TO_BOA_CERTIFICATES_AND_SECRET_KEY: $PATH_TO_BOA_CERTIFICATES_AND_SECRET_KEY
- PATH_TO_LOG_FOLDER: $PATH_TO_LOG_FOLDER

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
docker run --shm-size 512M --network=$DOCKER_NETWORK --name $DATABASE_CONTAINER -v $PATH_TO_BOA_DDBB:/var/lib/postgresql/data --restart=always -d mdillon/postgis -c 'max_connections=5000' -c 'max_locks_per_transaction=5000'

######
# Create APP container
######
docker load -i $PATH_TO_DOCKERIMAGE

docker run -e EBOA_DDBB_HOST=$DATABASE_CONTAINER -e SBOA_DDBB_HOST=$DATABASE_CONTAINER -e UBOA_DDBB_HOST=$DATABASE_CONTAINER -e MINARC_DATABASE_HOST=$DATABASE_CONTAINER -e ORC_DATABASE_HOST=$DATABASE_CONTAINER --shm-size 512M --network=$DOCKER_NETWORK -p $PORT:5000 -it --name $APP_CONTAINER -v $PATH_TO_MINARC_ARCHIVE:/minarc_root -v $PATH_TO_BOA_INPUTS:/inputs -v $PATH_TO_RBOA_ARCHIVE:/rboa_archive -v $PATH_TO_LOG_FOLDER:/log --restart=always -d `basename $PATH_TO_DOCKERIMAGE .tar`

# Copy certificates and secret key to the container
docker cp $PATH_TO_BOA_CERTIFICATES_AND_SECRET_KEY/boa_certificate.pem $APP_CONTAINER:/resources_path
docker cp $PATH_TO_BOA_CERTIFICATES_AND_SECRET_KEY/boa_key.pem $APP_CONTAINER:/resources_path
docker cp $PATH_TO_BOA_CERTIFICATES_AND_SECRET_KEY/web_server_secret_key.txt $APP_CONTAINER:/resources_path

# Store environment variables for the usege of cron tasks
docker exec -d -it -u boa $APP_CONTAINER bash -c "declare -p | grep -Ev 'BASHOPTS|BASH_VERSINFO|EUID|PPID|SHELLOPTS|UID' > /resources_path/container.env"

echo "
Docker environment successfully built :-)"
