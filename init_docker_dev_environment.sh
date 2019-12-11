#################################################################
#
# Init docker development environment of the vboa and its tailored app
#
# Written by DEIMOS Space S.L. (dibb)
#
# module vboa
#################################################################

USAGE="Usage: `basename $0` -e path_to_eboa_src -v path_to_vboa_src -d path_to_dockerfile -o path_to_orc_packets -u host_user_to_map [-p port] [-t path_to_tailored] [-l containers_label] [-a app] [-c boa_tailoring_configuration_path] [-x orc_tailoring_configuration_path]"

########
# Initialization
########
PATH_TO_EBOA=""
PATH_TO_VBOA=""
PATH_TO_TAILORED=""
PATH_TO_DOCKERFILE="Dockerfile.dev"
PORT="5000"
CONTAINERS_LABEL="dev"
APP="vboa"
PATH_TO_ORC=""
HOST_USER_TO_MAP=""

while getopts e:v:d:p:t:l:a:o:c:x:u: option
do
    case "${option}"
        in
        e) PATH_TO_EBOA=${OPTARG};;
        v) PATH_TO_VBOA=${OPTARG};;
        t) PATH_TO_TAILORED=${OPTARG};;
        d) PATH_TO_DOCKERFILE=${OPTARG};;
        p) PORT=${OPTARG};;
        l) CONTAINERS_LABEL=${OPTARG};;
        a) APP=${OPTARG};;
        o) PATH_TO_ORC=${OPTARG};;
        c) PATH_TO_BOA_TAILORING_CONFIGURATION=${OPTARG};;
        x) PATH_TO_ORC_CONFIGURATION=${OPTARG};;
        u) HOST_USER_TO_MAP=${OPTARG};;
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

# Check that option -o has been specified
if [ "$PATH_TO_ORC" == "" ];
then
    echo "ERROR: The option -o has to be provided"
    echo $USAGE
    exit -1
fi

# Check that the path to the orc packets exists
if [ ! -d $PATH_TO_ORC ];
then
    echo "ERROR: The directory $PATH_TO_ORC provided does not exist"
    exit -1
fi

# Check that the needed orc packets are present
minarc_count=$(find $PATH_TO_ORC/ -maxdepth 1 -mindepth 1 -name 'minarc*' | wc -l)
if [ $minarc_count == 0 ];
then
    echo "ERROR: The directory $PATH_TO_ORC does not contain a minarc packet"
    exit -1
elif [ $minarc_count -gt 1 ];
then
    echo "ERROR: The directory $PATH_TO_ORC contains more than one minarc packet"
    exit -1
fi
orc_count=$(find $PATH_TO_ORC/ -maxdepth 1 -mindepth 1 -name 'orc*' | wc -l)
if [ $orc_count == 0 ];
then
    echo "ERROR: The directory $PATH_TO_ORC does not contain a orc packet"
    exit -1
elif [ $orc_count -gt 1 ];
then
    echo "ERROR: The directory $PATH_TO_ORC contains more than one orc packet"
    exit -1
fi
gemfile_count=$(find $PATH_TO_ORC/ -maxdepth 1 -mindepth 1 -name 'Gemfile' | wc -l)
if [ $gemfile_count == 0 ];
then
    echo "ERROR: The directory $PATH_TO_GEMFILE does not contain a Gemfile file"
    exit -1
elif [ $gemfile_count -gt 1 ];
then
    echo "ERROR: The directory $PATH_TO_GEMFILE contains more than one Gemfile file"
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

# Check that the path to the boa tailoring congiguration exists
if [ "$PATH_TO_BOA_TAILORING_CONFIGURATION" != "" ] && [ ! -d $PATH_TO_BOA_TAILORING_CONFIGURATION ];
then
    echo "ERROR: The directory $PATH_TO_BOA_TAILORING_CONFIGURATION provided does not exist"
    exit -1
fi

# Check that the path to the orc tailoring congiguration exists
if [ "$PATH_TO_ORC_CONFIGURATION" != "" ] && [ ! -d $PATH_TO_ORC_CONFIGURATION ];
then
    echo "ERROR: The directory $PATH_TO_ORC_CONFIGURATION provided does not exist"
    exit -1
fi

# Check that option -u has been specified
if [ "$HOST_USER_TO_MAP" == "" ];
then
    echo "ERROR: The option -u has to be provided"
    echo $USAGE
    exit -1
fi

# Check that the path to the MINARC archive folder exists
if [ ! id $HOST_USER_TO_MAP >/dev/null 2>&1 ];
then
    while true; do
        read -p "The user $HOST_USER_TO_MAP does not exist. Do you wish to create it and proceed with the new installation?" answer
        case $answer in
            [Yy]* )
                useradd -m $HOST_USER_TO_MAP
                break;;
            [Nn]* ) exit;;
            * ) read -p "Please answer Y or y for yes or N or n for no: " answer;;
        esac
    done
fi

EBOA_RESOURCES_PATH="/eboa/src/config"
DATABASE_CONTAINER="boa_database_$CONTAINERS_LABEL"
APP_CONTAINER="boa_app_$CONTAINERS_LABEL"
DOCKER_NETWORK="boa_network_$CONTAINERS_LABEL"

read -p "
Welcome to the initializer of the BOA development environment :-)

You are trying to initialize a new development environment for the app: $APP...
These are the configuration options that will be applied to initialize the environment:
- PATH_TO_EBOA: $PATH_TO_EBOA
- PATH_TO_VBOA: $PATH_TO_VBOA
- PATH_TO_TAILORED: $PATH_TO_TAILORED
- PATH_TO_DOCKERFILE: $PATH_TO_DOCKERFILE
- PORT: $PORT
- CONTAINERS_LABEL: $CONTAINERS_LABEL
- APP: $APP
- PATH_TO_ORC: $PATH_TO_ORC
- PATH_TO_BOA_TAILORING_CONFIGURATION: $PATH_TO_BOA_TAILORING_CONFIGURATION
- PATH_TO_ORC_CONFIGURATION: $PATH_TO_ORC_CONFIGURATION
- HOST_USER_TO_MAP: $HOST_USER_TO_MAP

Do you wish to proceed with the initialization of the development environment?" answer

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
                docker rmi $(docker images boa_dev -q)

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
docker run --network=$DOCKER_NETWORK --name $DATABASE_CONTAINER -d mdillon/postgis -c 'max_connections=5000' -c 'max_locks_per_transaction=5000'

######
# Create APP container
######
find $PATH_TO_VBOA -name *pyc -delete
find $PATH_TO_EBOA -name *pyc -delete
if [ "$PATH_TO_TAILORED" != "" ];
then
    find $PATH_TO_TAILORED -name *pyc -delete
fi

HOST_UID_USER_TO_MAP=`id -u $HOST_USER_TO_MAP`

docker build --build-arg FLASK_APP=$APP --build-arg UID_HOST_USER=$HOST_UID_USER_TO_MAP --build-arg HOST_USER=$HOST_USER_TO_MAP -t boa_dev -f $PATH_TO_DOCKERFILE $PATH_TO_VBOA

# Initialize the eboa database
if [ "$PATH_TO_TAILORED" != "" ];
then
    docker run --network=$DOCKER_NETWORK -p $PORT:5000 -it --name $APP_CONTAINER -d -v $PATH_TO_EBOA:/eboa -v $PATH_TO_VBOA:/vboa -v $PATH_TO_TAILORED:/$APP boa_dev
else
    docker run --network=$DOCKER_NETWORK -p $PORT:5000 -it --name $APP_CONTAINER -d -v $PATH_TO_EBOA:/eboa -v $PATH_TO_VBOA:/vboa boa_dev
fi

# Copy configurations
for file in $PATH_TO_EBOA/src/config/*;
do
    docker cp $file $APP_CONTAINER:/resources_path
done
for file in $PATH_TO_BOA_TAILORING_CONFIGURATION/*;
do
    docker cp $file $APP_CONTAINER:/resources_path
done
for file in $PATH_TO_ORC_CONFIGURATION/*;
do
    docker cp $file $APP_CONTAINER:/orc_config
done
for file in $PATH_TO_ORC/*;
do
    docker cp $file $APP_CONTAINER:/orc_packages
done

# Change ownership
docker exec -it -u root $APP_CONTAINER bash -c "chown $HOST_USER_TO_MAP:$HOST_USER_TO_MAP /resources_path/*"
docker exec -it -u root $APP_CONTAINER bash -c "chown $HOST_USER_TO_MAP:$HOST_USER_TO_MAP /orc_config/*"
docker exec -it -u root $APP_CONTAINER bash -c "chown $HOST_USER_TO_MAP:$HOST_USER_TO_MAP /orc_packages//*"

# Generate the python archive
docker exec -it -u root $APP_CONTAINER bash -c "pip3 install --upgrade pip"
docker exec -it -u root $APP_CONTAINER bash -c "pip3 install -e '/eboa/src[tests]'"
docker exec -it -u root $APP_CONTAINER bash -c "pip3 install -e '/vboa/src[tests]'"
if [ "$PATH_TO_TAILORED" != "" ];
then
    docker exec -it -u root $APP_CONTAINER bash -c "pip3 install -e /$APP/src"
fi

# Change port and address configuration of the eboa defined by the postgis container
docker exec -it -u $HOST_USER_TO_MAP $APP_CONTAINER bash -c "sed -i 's/\"host\".*\".*\"/\"host\": \"$DATABASE_CONTAINER\"/' /resources_path/datamodel.json"

# Execute flask server
docker exec -d -it -u $HOST_USER_TO_MAP $APP_CONTAINER bash -c "source scl_source enable rh-ruby25; flask run --host=0.0.0.0 -p 5000"

# Install web packages
docker exec -it -u root $APP_CONTAINER bash -c "npm --prefix /vboa/src/vboa/static install"

# Install scripts
docker exec -it -u $HOST_USER_TO_MAP $APP_CONTAINER bash -c 'for script in /eboa/src/scripts/*; do ln -s $script /scripts/`basename $script`; done'

# Link datamodels
docker exec -it -u $HOST_USER_TO_MAP $APP_CONTAINER bash -c 'ln -s /eboa/datamodel/eboa_data_model.sql /datamodel/'
docker exec -it -u $HOST_USER_TO_MAP $APP_CONTAINER bash -c 'ln -s /eboa/datamodel/sboa_data_model.sql /datamodel/'

# Initialize the EBOA database inside the postgis-database container
while true
do
    echo "Trying to initialize database..."
    docker exec -it $APP_CONTAINER bash -c "/eboa/src/scripts/init_ddbb.sh -h $DATABASE_CONTAINER -p 5432 -f /eboa/datamodel/eboa_data_model.sql" > /dev/null
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

# Initialize the SBOA database
docker exec -it -u root $APP_CONTAINER bash -c "sboa_init.py"

# Listen for changes on the web packages
docker exec -d -it -u root $APP_CONTAINER bash -c "npm --prefix /vboa/src/vboa/static run watch"

# Install cron activities
echo "Installing cron activities"
docker exec -d -it -u root $APP_CONTAINER bash -c "cp /eboa/src/cron/boa_cron /etc/cron.d/"
if [ "$PATH_TO_TAILORED" != "" ] && [ -f "$PATH_TO_TAILORED/src/cron/boa_cron" ];
then
    docker exec -d -it -u root $APP_CONTAINER bash -c "cp /$APP/src/cron/boa_cron /etc/cron.d/"
fi

# Copy cron to crontab
docker exec -d -it -u root $APP_CONTAINER bash -c "crontab /etc/cron.d/boa_cron"

echo "Cron activities installed"

# Install orc
docker exec -it -u root $APP_CONTAINER bash -c "source scl_source enable rh-ruby25; cd /orc_packages/; bundle install --gemfile Gemfile"
docker exec -it -u root $APP_CONTAINER bash -c "source scl_source enable rh-ruby25; cd /orc_packages/; gem install minarc*"
docker exec -it -u root $APP_CONTAINER bash -c "source scl_source enable rh-ruby25; cd /orc_packages/; gem install orc*"

# Initialize the ORC DDBB
docker exec -it -u root $APP_CONTAINER bash -c "createdb s2boa_orc"
docker exec -it $APP_CONTAINER bash -c "source scl_source enable rh-ruby25; minArcDB --create-tables"
docker exec -it $APP_CONTAINER bash -c "source scl_source enable rh-ruby25; orcManageDB --create-tables"

# Execute the ORC server
docker exec -it -u $HOST_USER_TO_MAP $APP_CONTAINER bash -c "source scl_source enable rh-ruby25; orcBolg -c start"
