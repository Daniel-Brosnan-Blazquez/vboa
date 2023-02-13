#################################################################
#
# Generate BOA image from already available packages
#
# Written by DEIMOS Space S.L. (dibb)
#
# module boa
#################################################################

USAGE="Usage: `basename $0` -p path_to_boa_packages -d path_to_dockerfile -o path_to_orc_packages -u uid_host_user_to_map [-a app] [-l version] [-g export_docker_image]"

########
# Initialization
########
PATH_TO_BOA_PACKAGES=""
PATH_TO_DOCKERFILE=""
APP="vboa"
PATH_TO_ORC=""
VERSION="0.1.0"
EXPORT_DOCKER_IMAGE="NO"
UID_HOST_USER_TO_MAP=""

while getopts d:p:a:o:l:u:g option
do
    case "${option}"
        in
        p) PATH_TO_BOA_PACKAGES=${OPTARG};;
        d) PATH_TO_DOCKERFILE=${OPTARG};;
        a) APP=${OPTARG};;
        o) PATH_TO_ORC=${OPTARG};;
        l) VERSION=${OPTARG};;
        u) UID_HOST_USER_TO_MAP=${OPTARG};;        
        g) EXPORT_DOCKER_IMAGE="YES";;
        ?) echo -e $USAGE
            exit -1
    esac
done

# Check that option -p has been specified
if [ "$PATH_TO_BOA_PACKAGES" == "" ];
then
    echo "ERROR: The option -p has to be provided"
    echo $USAGE
    exit -1
fi

# Check that the path to the BOA packages exists
if [ ! -d $PATH_TO_BOA_PACKAGES ];
then
    echo "ERROR: The directory $PATH_TO_BOA_PACKAGES provided does not exist"
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
minarc_count=$(find $PATH_TO_ORC/ -maxdepth 1 -name "minarc*.gem" | wc -l)
if [ $minarc_count == 0 ];
then
    echo "ERROR: The directory $PATH_TO_ORC does not contain a minarc packet"
    exit -1
elif [ $minarc_count -gt 1 ];
then
    echo "ERROR: The directory $PATH_TO_ORC contains more than one minarc packet"
    exit -1
fi
orc_count=$(find $PATH_TO_ORC/ -maxdepth 1 -name "orc*.gem" | wc -l)
if [ $orc_count == 0 ];
then
    echo "ERROR: The directory $PATH_TO_ORC does not contain a orc packet"
    exit -1
elif [ $orc_count -gt 1 ];
then
    echo "ERROR: The directory $PATH_TO_ORC contains more than one orc packet"
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

# Check that option -u has been specified
if [ "$UID_HOST_USER_TO_MAP" == "" ];
then
    echo "ERROR: The option -u has to be provided"
    echo $USAGE
    exit -1
fi

APP_CONTAINER="boa_app_$APP"

while true; do
read -p "
Welcome to the docker image generator (from BOA packages) of the BOA environment :-)

You are going to generate the docker image for the app: $APP...
These are the configuration options that will be applied to initialize the environment:
- PATH_TO_BOA_PACKAGES: $PATH_TO_BOA_PACKAGES
- PATH_TO_DOCKERFILE: $PATH_TO_DOCKERFILE
- APP: $APP
- PATH_TO_ORC: $PATH_TO_ORC
- UID_HOST_USER_TO_MAP: $UID_HOST_USER_TO_MAP
- VERSION: $VERSION

Do you wish to proceed with the generation of the docker image?" answer
    case $answer in
        [Yy]* )
            break;;
        [Nn]* )
            echo "No worries, the docker image will not be generated";
            exit;;
        * ) echo "Please answer Y or y for yes or N or n for no. Answered: $answer";;
    esac
done

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

# Build image
echo "Building BOA image..."
docker build --build-arg FLASK_APP=$APP --build-arg UID_HOST_USER=$UID_HOST_USER_TO_MAP -t boa:$VERSION -t boa:latest -f $PATH_TO_DOCKERFILE `dirname $PATH_TO_DOCKERFILE`

# Create container
echo "Intantiating BOA image..."
docker run -it --name $APP_CONTAINER -d -v $PATH_TO_BOA_PACKAGES:/boa_packages boa:$VERSION

# Install BOA packages
echo "Installing BOA packages..."
docker exec -it -u root $APP_CONTAINER bash -c "pip3 install --upgrade pip"
docker exec -it -u root $APP_CONTAINER bash -c "pip3 install /boa_packages/*tar.gz"

# Uncompress BOA packages and copy relevant auxiliary files
docker exec -it -u root $APP_CONTAINER bash -c "chown boa /boa_packages"
docker exec -it -u boa $APP_CONTAINER bash -c 'for package in /boa_packages/*tar.gz; do tar xzvf /boa_packages/`basename $package` -C /boa_packages/; done'

# Copy EBOA configurations
echo "Copying EBOA configurations..."
docker exec -it -u boa $APP_CONTAINER bash -c "cp /boa_packages/eboa*/config/* /resources_path"

# Copy EBOA scripts
echo "Copying EBOA scripts..."
docker exec -it -u boa $APP_CONTAINER bash -c "cp /boa_packages/eboa*/scripts/* /scripts"

# Copy EBOA ingestion chain
echo "Copying EBOA ingestion chain..."
docker exec -it -u boa $APP_CONTAINER bash -c "cp /boa_packages/eboa*/eboa/triggering/eboa_triggering.py /scripts/eboa_triggering.py"
docker exec -it -u boa $APP_CONTAINER bash -c "cp /boa_packages/eboa*/eboa/ingestion/eboa_ingestion.py /scripts/eboa_ingestion.py"

# Copy EBOA data models
echo "Copying EBOA data models..."
docker exec -it -u boa $APP_CONTAINER bash -c "cp /boa_packages/eboa*/datamodel/eboa_data_model.sql /datamodel"
docker exec -it -u boa $APP_CONTAINER bash -c "cp /boa_packages/eboa*/datamodel/sboa_data_model.sql /datamodel"
docker exec -it -u boa $APP_CONTAINER bash -c "cp /boa_packages/eboa*/datamodel/uboa_data_model.sql /datamodel"

# Copy EBOA schemas
echo "Copying EBOA schemas..."
docker exec -it -u boa $APP_CONTAINER bash -c "cp /boa_packages/eboa*/schemas/* /schemas"

# Install EBOA cron activities
echo "Installing EBOA cron activities..."

# Copy RBOA reporting chain
echo "Installing RBOA reporting chain..."
docker exec -it -u boa $APP_CONTAINER bash -c "cp /boa_packages/eboa*/rboa/triggering/rboa_triggering.py /scripts/rboa_triggering.py"
docker exec -it -u boa $APP_CONTAINER bash -c "cp /boa_packages/eboa*/rboa/reporting/rboa_reporting.py /scripts/rboa_reporting.py"

# Copy SBOA scheduler chain
echo "Installing SBOA scheduler chain..."
docker exec -it -u boa $APP_CONTAINER bash -c "cp /boa_packages/eboa*/sboa/scheduler/boa_scheduler.py /scripts/boa_scheduler.py"
docker exec -it -u boa $APP_CONTAINER bash -c "cp /boa_packages/eboa*/sboa/scheduler/boa_execute_triggering.py /scripts/boa_execute_triggering.py"

# Copy VBOA scripts
echo "Installing VBOA scripts..."
docker exec -it -u boa $APP_CONTAINER bash -c "cp /boa_packages/vboa*/scripts/* /scripts"

# Copy tailored BOA configurations
echo "Copying tailored BOA configurations..."
docker exec -it -u boa $APP_CONTAINER bash -c "cp /boa_packages/*/boa_config/* /resources_path"

# Copy tailored BOA schemas
echo "Copying tailored BOA schemas..."
docker exec -it -u boa $APP_CONTAINER bash -c "cp /boa_packages/*/boa_schemas/* /schemas"

# Copy tailored BOA cron activities
echo "Copying tailored BOA cron activities..."
docker exec -it -u boa $APP_CONTAINER bash -c "cp /boa_packages/*/boa_cron/boa_cron /etc/cron.d/"

# Specify the ID of the HEAD versions used for EBOA, VBOA and the tailored BOA
docker exec -it -u boa $APP_CONTAINER bash -c "cp /boa_packages/eboa*/boa_package_versions/boa_package_versions /resources_path/boa_package_versions"

# Activate crontab
echo "Activating cron activities..."
docker exec -d -it -u root $APP_CONTAINER bash -c "crontab /etc/cron.d/boa_cron"

# Install orc
echo "Installing ORC..."
for file in $PATH_TO_ORC/*;
do
    docker cp $file $APP_CONTAINER:/orc_packages
done
docker exec -it -u root $APP_CONTAINER bash -c "source scl_source enable rh-ruby27; cd /orc_packages/; gem install minarc*"
docker exec -it -u root $APP_CONTAINER bash -c "source scl_source enable rh-ruby27; cd /orc_packages/; gem install orc*"

if [ "$EXPORT_DOCKER_IMAGE" == "YES" ];
then
    TMP_DIR=`mktemp -d`
    # Docker commit and save image
    docker commit $APP_CONTAINER boa:$VERSION
    docker commit $APP_CONTAINER boa:latest
    docker save boa > $TMP_DIR/boa.tar
    
    echo "BOA image exported in: "$TMP_DIR/boa.tar
    
    echo "Removing temporal docker container and image"
    
    docker stop $APP_CONTAINER
    docker rm $APP_CONTAINER
    docker rmi -f $(docker images boa -q)
fi
