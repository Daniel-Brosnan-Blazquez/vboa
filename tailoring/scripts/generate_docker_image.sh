#################################################################
#
# Default BOA image generator for an instance
#
# Written by DEIMOS Space S.L. (dibb)
#
# module vboa
#################################################################

USAGE="Usage: `basename $0` -e path_to_eboa_src -v path_to_vboa_src -d path_to_dockerfile -p path_to_dockerfile_pkg -o path_to_orc_packets -u uid_host_user_to_map -t path_to_tailored [-b path_to_common_base] [-a app] [-c boa_tailoring_configuration_path] [-l version]"

########
# Initialization
########
PATH_TO_EBOA=""
PATH_TO_VBOA=""
PATH_TO_TAILORED=""
PATH_TO_COMMON_BASE=""
COMMON_BASE_FOLDER=""
PATH_TO_DOCKERFILE="Dockerfile"
APP="vboa"
PATH_TO_ORC=""
VERSION="0.1.0"
UID_HOST_USER_TO_MAP=""

while getopts e:v:d:t:b:a:o:c:p:l:f:u: option
do
    case "${option}"
        in
        e) PATH_TO_EBOA=${OPTARG}; PATH_TO_EBOA_CALL="-e ${OPTARG}";;
        v) PATH_TO_VBOA=${OPTARG}; PATH_TO_VBOA_CALL="-v ${OPTARG}";;
        t) PATH_TO_TAILORED=${OPTARG}; PATH_TO_TAILORED_CALL="-t ${OPTARG}";;
        b) PATH_TO_COMMON_BASE=${OPTARG}; COMMON_BASE_FOLDER=`basename $PATH_TO_COMMON_BASE`; PATH_TO_COMMON_BASE_CALL="-b ${OPTARG}";;
        d) PATH_TO_DOCKERFILE=${OPTARG}; PATH_TO_DOCKERFILE_CALL="-d ${OPTARG}";;
        p) PATH_TO_DOCKERFILE_PKG=${OPTARG}; PATH_TO_DOCKERFILE_PKG_CALL="-p ${OPTARG}";;
        a) APP=${OPTARG}; APP_CALL="-a ${OPTARG}";;
        o) PATH_TO_ORC=${OPTARG}; PATH_TO_ORC_CALL="-o ${OPTARG}";;
        c) PATH_TO_BOA_TAILORING_CONFIGURATION=${OPTARG}; PATH_TO_BOA_TAILORING_CONFIGURATION_CALL="-c ${OPTARG}";;
        u) UID_HOST_USER_TO_MAP=${OPTARG}; UID_HOST_USER_TO_MAP_CALL="-u ${OPTARG}";;        
        l) VERSION=${OPTARG}; VERSION_CALL="-l ${OPTARG}";;
        ?) echo -e $USAGE
            exit -1
    esac
done

# Check that option -t has been specified
if [ "$PATH_TO_TAILORED" == "" ];
then
    echo "ERROR: The option -t has to be provided"
    echo $USAGE
    exit -1
fi

# Check that the path to the tailored exists
if [ ! -d $PATH_TO_TAILORED ];
then
    echo "ERROR: The directory $PATH_TO_TAILORED provided does not exist"
    exit -1
fi

# Check that the path to the common base project exists
if [ "$PATH_TO_COMMON_BASE" != "" ] && [ ! -d $PATH_TO_COMMON_BASE ];
then
    echo "ERROR: The directory $PATH_TO_COMMON_BASE provided does not exist"
    exit -1
fi

APP_CONTAINER="boa_app_$APP"

while true; do
read -p "
Welcome to the docker image generator of the $APP environment :-)

You are going to generate the docker image for the app: $APP...
These are the specific configuration options that will be applied to initialize the environment:

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

# Generate docker image
$PATH_TO_VBOA/generate_docker_image.sh $PATH_TO_EBOA_CALL $PATH_TO_VBOA_CALL $PATH_TO_TAILORED_CALL $PATH_TO_COMMON_BASE_CALL $PATH_TO_DOCKERFILE_CALL $PATH_TO_DOCKERFILE_PKG_CALL $APP_CALL $PATH_TO_ORC_CALL $PATH_TO_BOA_TAILORING_CONFIGURATION_CALL $UID_HOST_USER_TO_MAP_CALL $VERSION_CALL

# Check that the BOA image could be generated
status=$?
if [ $status -ne 0 ]
then
    echo "The BOA image could not be generated :-("
    exit -1
else
    echo "The BOA image has been generated successfully :-)"
fi

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
