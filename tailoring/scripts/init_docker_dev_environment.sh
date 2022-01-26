#################################################################
#
# Default init docker development environment script for BOA
# Modify accordingly to the project
#
# Written by DEIMOS Space S.L. (dibb)
#
# module vboa
#################################################################

USAGE="Usage: `basename $0` -e path_to_eboa_src -v path_to_vboa_src -d path_to_dockerfile -o path_to_orc_packets -u host_user_to_map -t path_to_tailored [-b path_to_common_base] [-p port] [-l containers_label] [-a app] [-c boa_tailoring_configuration_path] [-s path_to_boa_certificates] [-n] [-r]\n
Where:\n
-s path_to_boa_certificates: Path to SSL certificates which names should be boa_certificate.pem and boa_key.pem\n
-n: disable DDBB port exposure (5432). Exposure of this port is needed for obtaining differences between data models
-r: disable removal available BOA images
"

########
# Initialization
########
PATH_TO_EBOA=""
PATH_TO_VBOA=""
PATH_TO_TAILORED=""
PATH_TO_COMMON_BASE=""
COMMON_BASE_FOLDER=""
PATH_TO_DOCKERFILE="Dockerfile.dev"
PORT="5000"
CONTAINERS_LABEL="dev"
APP="vboa"
PATH_TO_ORC=""
HOST_USER_TO_MAP=""
EXPOSE_DDBB_PORT="TRUE"
PATH_TO_BOA_CERTIFICATES=""
REMOVE_AVAILABLE_BOA_IMAGES="TRUE"

while getopts e:v:d:o:u:p:t:b:l:a:c:s:nrf: option
do
    case "${option}"
        in
        e) PATH_TO_EBOA=${OPTARG}; PATH_TO_EBOA_CALL="-e ${OPTARG}";;
        v) PATH_TO_VBOA=${OPTARG}; PATH_TO_VBOA_CALL="-v ${OPTARG}";;
        d) PATH_TO_DOCKERFILE=${OPTARG}; PATH_TO_DOCKERFILE_CALL="-d ${OPTARG}";;
        o) PATH_TO_ORC=${OPTARG}; PATH_TO_ORC_CALL="-o ${OPTARG}";;
        u) HOST_USER_TO_MAP=${OPTARG}; HOST_USER_TO_MAP_CALL="-u ${OPTARG}";;
        p) PORT=${OPTARG}; PORT_CALL="-p ${OPTARG}";;
        t) PATH_TO_TAILORED=${OPTARG}; PATH_TO_TAILORED_CALL="-t ${OPTARG}";;
        b) PATH_TO_COMMON_BASE=${OPTARG}; COMMON_BASE_FOLDER=`basename $PATH_TO_COMMON_BASE`; PATH_TO_COMMON_BASE_CALL="-b ${OPTARG}";;
        l) CONTAINERS_LABEL=${OPTARG}; CONTAINERS_LABEL_CALL="-l ${OPTARG}";;
        a) APP=${OPTARG}; APP_CALL="-a ${OPTARG}";;
        c) PATH_TO_BOA_TAILORING_CONFIGURATION=${OPTARG}; PATH_TO_BOA_TAILORING_CONFIGURATION_CALL="-c ${OPTARG}";;
        s) PATH_TO_BOA_CERTIFICATES=${OPTARG}; PATH_TO_BOA_CERTIFICATES_CALL="-s ${OPTARG}";;
        n) EXPOSE_DDBB_PORT="FALSE"; EXPOSE_DDBB_PORT_CALL="-n ${OPTARG}";;
        r) REMOVE_AVAILABLE_BOA_IMAGES="FALSE"; REMOVE_AVAILABLE_BOA_IMAGES_CALL="-r ${OPTARG}";;
        f) PATH_TO_EOPCFI=${OPTARG}; PATH_TO_EOPCFI_CALL="-f ${OPTARG}";;
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

# Check that the path to the common base exists
if [ "$PATH_TO_COMMON_BASE" != "" ] && [ ! -d $PATH_TO_COMMON_BASE ];
then
    echo "ERROR: The directory $PATH_TO_COMMON_BASE provided does not exist"
    exit -1
fi

APP_CONTAINER="boa_app_$CONTAINERS_LABEL"

while true; do
    read -p "
Welcome to the initializer of the $APP development environment :-)

You are trying to initialize a new development environment for the app: $APP...
These are the specific configuration options that will be applied to initialize the environment:

Do you wish to proceed with the initialization of the development environment?" answer
    case $answer in
        [Yy]* )
            break;;
        [Nn]* )
            echo "No worries, the initializer will not continue";
            exit;;
        * ) echo "Please answer Y or y for yes or N or n for no. Answered: $answer";;
    esac
done

# Initialize development environment
# Generate docker image
$PATH_TO_VBOA/init_docker_dev_environment.sh $PATH_TO_EBOA_CALL $PATH_TO_VBOA_CALL $PATH_TO_DOCKERFILE_CALL $PATH_TO_ORC_CALL $HOST_USER_TO_MAP_CALL $PORT_CALL $PATH_TO_TAILORED_CALL $PATH_TO_COMMON_BASE_CALL $CONTAINERS_LABEL_CALL $APP_CALL $PATH_TO_BOA_TAILORING_CONFIGURATION_CALL $PATH_TO_BOA_CERTIFICATES_CALL $EXPOSE_DDBB_PORT_CALL $REMOVE_AVAILABLE_BOA_IMAGES_CALL

# Check that the BOA development environment could be generated
status=$?
if [ $status -ne 0 ]
then
    echo "The BOA development environment could not be generated :-("
    exit -1
else
    echo "The BOA development environment has been generated successfully :-)"
fi

echo "
The development environment for $APP has been initialized :-)"
