#################################################################
#
# Generate BOA image
#
# Written by DEIMOS Space S.L. (dibb)
#
# module boa
#################################################################

USAGE="Usage: `basename $0` -e path_to_eboa_src -v path_to_vboa_src -d path_to_dockerfile -p path_to_dockerfile_pkg -o path_to_orc_packets -u uid_host_user_to_map [-t path_to_tailored] [-b path_to_common_base] [-a app] [-c boa_tailoring_configuration_path] [-l version] [-g export_docker_image]"

########
# Initialization
########
PATH_TO_EBOA=""
PATH_TO_VBOA=""
PATH_TO_TAILORED=""
PATH_TO_COMMON_BASE=""
PATH_TO_DOCKERFILE="Dockerfile"
APP="vboa"
PATH_TO_ORC=""
VERSION="0.1.0"
EXPORT_DOCKER_IMAGE="NO"
UID_HOST_USER_TO_MAP=""

while getopts e:v:d:p:t:b:a:o:c:p:l:u:g option
do
    case "${option}"
        in
        e) PATH_TO_EBOA=${OPTARG}; PATH_TO_EBOA_CALL="-e ${OPTARG}";;
        v) PATH_TO_VBOA=${OPTARG}; PATH_TO_VBOA_CALL="-v ${OPTARG}";;
        t) PATH_TO_TAILORED=${OPTARG}; PATH_TO_TAILORED_CALL="-t ${OPTARG}";;
        b) PATH_TO_COMMON_BASE=${OPTARG}; COMMON_BASE_FOLDER=`basename $PATH_TO_COMMON_BASE`; PATH_TO_COMMON_BASE_CALL="-b ${OPTARG}";;
        d) PATH_TO_DOCKERFILE=${OPTARG}; PATH_TO_DOCKERFILE_CALL="-d ${OPTARG}";;
        p) PATH_TO_DOCKERFILE_PKG=${OPTARG}; PATH_TO_DOCKERFILE_PKG_CALL="-d ${OPTARG}";;
        a) APP=${OPTARG}; APP_CALL="-a ${OPTARG}";;
        o) PATH_TO_ORC=${OPTARG}; PATH_TO_ORC_CALL="-o ${OPTARG}";;
        c) PATH_TO_BOA_TAILORING_CONFIGURATION=${OPTARG}; PATH_TO_BOA_TAILORING_CONFIGURATION_CALL="-c ${OPTARG}";;
        l) VERSION=${OPTARG};;
        u) UID_HOST_USER_TO_MAP=${OPTARG};;        
        g) EXPORT_DOCKER_IMAGE="YES";;
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
minarc_count=$(find $PATH_TO_ORC/ -maxdepth 1 -name 'minarc*.gem' | wc -l)
if [ $minarc_count == 0 ];
then
    echo "ERROR: The directory $PATH_TO_ORC does not contain a minarc packet"
    exit -1
elif [ $minarc_count -gt 1 ];
then
    echo "ERROR: The directory $PATH_TO_ORC contains more than one minarc packet"
    exit -1
fi
orc_count=$(find $PATH_TO_ORC/ -maxdepth 1 -name 'orc*.gem' | wc -l)
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

# Check that option -p has been specified
if [ "$PATH_TO_DOCKERFILE_PKG" == "" ];
then
    echo "ERROR: The option -p has to be provided"
    echo $USAGE
    exit -1
fi

# Check that the docker file exists
if [ ! -f $PATH_TO_DOCKERFILE_PKG ];
then
    echo "ERROR: The file $PATH_TO_DOCKERFILE_PKG provided does not exist"
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

# Check that option -u has been specified
if [ "$UID_HOST_USER_TO_MAP" == "" ];
then
    echo "ERROR: The option -u has to be provided"
    echo $USAGE
    exit -1
fi

EBOA_RESOURCES_PATH="/eboa/src/config"
APP_CONTAINER="boa_app_$APP"

while true; do
read -p "
Welcome to the docker image generator of the BOA environment :-)

You are going to generate the docker image for the app: $APP...
These are the configuration options that will be applied to initialize the environment:
- PATH_TO_EBOA: $PATH_TO_EBOA
- PATH_TO_VBOA: $PATH_TO_VBOA
- PATH_TO_TAILORED: $PATH_TO_TAILORED
- PATH_TO_COMMON_BASE: $PATH_TO_COMMON_BASE
- PATH_TO_DOCKERFILE: $PATH_TO_DOCKERFILE
- PATH_TO_DOCKERFILE_PKG: $PATH_TO_DOCKERFILE_PKG
- APP: $APP
- PATH_TO_ORC: $PATH_TO_ORC
- PATH_TO_BOA_TAILORING_CONFIGURATION: $PATH_TO_BOA_TAILORING_CONFIGURATION
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

######
# Generate BOA packages
######
TMP_DIR=`mktemp -d`
$PATH_TO_VBOA/generate_boa_packages.sh $PATH_TO_EBOA_CALL $PATH_TO_VBOA_CALL $PATH_TO_DOCKERFILE_PKG_CALL $APP_CALL -o $TMP_DIR $PATH_TO_TAILORED_CALL $PATH_TO_COMMON_BASE_CALL

# Check that BOA packages could be generated
status=$?
if [ $status -ne 0 ]
then
    echo "BOA packages could not be generated :-("
    exit -1
else
    echo "The BOA packages have been generated successfully :-)"
fi

# Build image
docker build --build-arg FLASK_APP=$APP --build-arg UID_HOST_USER=$UID_HOST_USER_TO_MAP -t boa:$VERSION -t boa:latest -f $PATH_TO_DOCKERFILE $PATH_TO_VBOA

# Create container
if [ "$PATH_TO_TAILORED" != "" ] && [ "$PATH_TO_COMMON_BASE" != "" ];
then
    docker run -it --name $APP_CONTAINER -d -v $PATH_TO_EBOA:/eboa -v $PATH_TO_VBOA:/vboa -v $PATH_TO_TAILORED:/$APP -v $PATH_TO_COMMON_BASE:/$COMMON_BASE_FOLDER -v $TMP_DIR:/boa_packages boa:$VERSION
elif [ "$PATH_TO_TAILORED" != "" ];
then
    docker run -it --name $APP_CONTAINER -d -v $PATH_TO_EBOA:/eboa -v $PATH_TO_VBOA:/vboa -v $PATH_TO_TAILORED:/$APP -v $TMP_DIR:/boa_packages boa:$VERSION
else
    docker run -it --name $APP_CONTAINER -d -v $PATH_TO_EBOA:/eboa -v $PATH_TO_VBOA:/vboa -v $TMP_DIR:/boa_packages boa:$VERSION
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
for file in $PATH_TO_ORC/*;
do
    docker cp $file $APP_CONTAINER:/orc_packages
done

# Generate the python archive
docker exec -it -u root $APP_CONTAINER bash -c "pip3 install --upgrade pip"
docker exec -it -u root $APP_CONTAINER bash -c "pip3 install /boa_packages/eboa*"
docker exec -it -u root $APP_CONTAINER bash -c "pip3 install /boa_packages/vboa*"
docker exec -it -u root $APP_CONTAINER bash -c "pip3 install /boa_packages/*"

# Install EBOA scripts
docker exec -it -u boa $APP_CONTAINER bash -c 'for script in /eboa/src/scripts/*; do cp $script /scripts/`basename $script`; done'
# EBOA ingestion chain
docker exec -it -u boa $APP_CONTAINER bash -c 'cp /eboa/src/eboa/triggering/eboa_triggering.py /scripts/eboa_triggering.py'
docker exec -it -u boa $APP_CONTAINER bash -c 'cp /eboa/src/eboa/ingestion/eboa_ingestion.py /scripts/eboa_ingestion.py'
# RBOA reporting chain 
docker exec -it -u boa $APP_CONTAINER bash -c 'cp /eboa/src/rboa/triggering/rboa_triggering.py /scripts/rboa_triggering.py'
docker exec -it -u boa $APP_CONTAINER bash -c 'cp /eboa/src/rboa/reporting/rboa_reporting.py /scripts/rboa_reporting.py'
# SBOA scheduler chain 
docker exec -it -u boa $APP_CONTAINER bash -c 'cp /eboa/src/sboa/scheduler/boa_scheduler.py /scripts/boa_scheduler.py'
docker exec -it -u boa $APP_CONTAINER bash -c 'cp /eboa/src/sboa/scheduler/boa_execute_triggering.py /scripts/boa_execute_triggering.py'
# Install VBOA scripts
docker exec -it -u boa $APP_CONTAINER bash -c 'for script in /vboa/src/scripts/*; do cp $script /scripts/`basename $script`; done'

# Copy datamodels
docker exec -it -u boa $APP_CONTAINER bash -c 'cp /eboa/datamodel/eboa_data_model.sql /datamodel'
docker exec -it -u boa $APP_CONTAINER bash -c 'cp /eboa/datamodel/sboa_data_model.sql /datamodel'
docker exec -it -u boa $APP_CONTAINER bash -c 'cp /eboa/datamodel/uboa_data_model.sql /datamodel'

# Copy schemas
docker exec -it -u boa $APP_CONTAINER bash -c 'cp /eboa/src/schemas/* /schemas'

# Specify the ID of the HEAD versions used for EBOA, VBOA and the tailored BOA
HEAD_ID_EBOA=`git -C $PATH_TO_EBOA rev-parse HEAD`
HEAD_ID_VBOA=`git -C $PATH_TO_VBOA rev-parse HEAD`
if [ "$PATH_TO_TAILORED" != "" ];
then
    HEAD_ID_TAILORED=`git -C $PATH_TO_TAILORED rev-parse HEAD`
fi
if [ "$PATH_TO_COMMON_BASE" != "" ];
then
    HEAD_ID_COMMON_BASE=`git -C $PATH_TO_COMMON_BASE rev-parse HEAD`
fi
docker exec -it -u boa $APP_CONTAINER bash -c "echo -e 'HEAD_ID_EBOA=$HEAD_ID_EBOA\nHEAD_ID_VBOA=$HEAD_ID_VBOA\nHEAD_ID_TAILORED=$HEAD_ID_TAILORED\nHEAD_ID_COMMON_BASE=$HEAD_ID_COMMON_BASE' > /resources_path/boa_package_versions"

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
docker exec -it -u root $APP_CONTAINER bash -c "source scl_source enable rh-ruby27; cd /orc_packages/; gem install minarc*"
docker exec -it -u root $APP_CONTAINER bash -c "source scl_source enable rh-ruby27; cd /orc_packages/; gem install orc*"

if [ "$EXPORT_DOCKER_IMAGE" == "YES" ];
then
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
