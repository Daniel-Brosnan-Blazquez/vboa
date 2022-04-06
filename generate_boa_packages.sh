#################################################################
#
# Generate boa packages of the boa and its tailored app
#
# Written by DEIMOS Space S.L. (dibb)
#
# module vboa
#################################################################

USAGE="Usage: `basename $0` -e path_to_eboa_src -v path_to_vboa_src -d path_to_dockerfile -o path_to_output_folder [-t path_to_tailored] [-b path_to_common_base]"

########
# Initialization
########
PATH_TO_EBOA=""
PATH_TO_VBOA=""
PATH_TO_TAILORED=""
PATH_TO_COMMON_BASE=""
PATH_TO_DOCKERFILE="Dockerfile.pkg"
APP="vboa"
PATH_TO_OUTPUT="/tmp"

while getopts e:v:d:t:b:o:a: option
do
    case "${option}"
        in
        e) PATH_TO_EBOA=${OPTARG};;
        v) PATH_TO_VBOA=${OPTARG};;
        t) PATH_TO_TAILORED=${OPTARG};;
        b) PATH_TO_COMMON_BASE=${OPTARG}; COMMON_BASE_FOLDER=`basename $PATH_TO_COMMON_BASE`;;
        d) PATH_TO_DOCKERFILE=${OPTARG};;
        a) APP=${OPTARG};;
        o) PATH_TO_OUTPUT=${OPTARG};;
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

# Check that the path to the common base project exists
if [ "$PATH_TO_COMMON_BASE" != "" ] && [ ! -d $PATH_TO_COMMON_BASE ];
then
    echo "ERROR: The directory $PATH_TO_COMMON_BASE provided does not exist"
    exit -1
fi

# Check that option -o has been specified
if [ "$PATH_TO_OUTPUT" == "" ];
then
    echo "ERROR: The option -o has to be provided"
    echo $USAGE
    exit -1
fi

# Check that the path to the output folder exists
if [ ! -d $PATH_TO_OUTPUT ];
then
    echo "ERROR: The directory $PATH_TO_OUTPUT provided does not exist"
    exit -1
fi

read -p "
Welcome to the generator of the BOA packages for the BOA app :-)

You are trying to generate BOA packages for the app: $APP...
These are the configuration options that will be applied to initialize the environment:
- PATH_TO_EBOA: $PATH_TO_EBOA
- PATH_TO_VBOA: $PATH_TO_VBOA
- PATH_TO_TAILORED: $PATH_TO_TAILORED
- PATH_TO_COMMON_BASE: $PATH_TO_COMMON_BASE
- APP: $APP
- PATH_TO_DOCKERFILE: $PATH_TO_DOCKERFILE
- PATH_TO_OUTPUT: $PATH_TO_OUTPUT

Do you wish to proceed with the generation of the image?" answer

PKG_CONTAINER="boa_pkg_$APP"

if [ "$(docker ps -a | grep -w $PKG_CONTAINER)" ];
then
    while true; do
        read -p "There has been detected a container with the same name: $PKG_CONTAINER. Do you wish to remove it and proceed with the new installation?" answer
        case $answer in
            [Yy]* )
                # Remove app image and container if it already exists
                docker stop $PKG_CONTAINER
                docker rm $PKG_CONTAINER
                docker rmi $(docker images boa_pkg -q)

                break;;
            [Nn]* ) exit;;
            * ) echo "Please answer Y or y for yes or N or n for no.";;
        esac
    done
fi

######
# Create container for generating the packages
######
find $PATH_TO_VBOA -name *pyc -delete
find $PATH_TO_EBOA -name *pyc -delete
if [ "$PATH_TO_TAILORED" != "" ];
then
    find $PATH_TO_TAILORED -name *pyc -delete
fi
if [ "$PATH_TO_COMMON_BASE" != "" ];
then
    find $PATH_TO_COMMON_BASE -name *pyc -delete
fi

echo "Building image for generating BOA packages"
docker build --build-arg FLASK_APP=$APP -t boa_pkg -f $PATH_TO_DOCKERFILE $PATH_TO_VBOA

echo "Running container for generating the BOA packages"
# Initialize the eboa database
if [ "$PATH_TO_TAILORED" != "" ] && [ "$PATH_TO_COMMON_BASE" != "" ];
then
    docker run -it --name $PKG_CONTAINER -d -v $PATH_TO_EBOA:/eboa -v $PATH_TO_VBOA:/vboa -v $PATH_TO_TAILORED:/$APP -v $PATH_TO_COMMON_BASE:/$COMMON_BASE_FOLDER -v $PATH_TO_OUTPUT:/output boa_pkg
elif [ "$PATH_TO_TAILORED" != "" ];
then
    docker run -it --name $PKG_CONTAINER -d -v $PATH_TO_EBOA:/eboa -v $PATH_TO_VBOA:/vboa -v $PATH_TO_TAILORED:/$APP -v $PATH_TO_OUTPUT:/output boa_pkg
else
    docker run -it --name $PKG_CONTAINER -d -v $PATH_TO_EBOA:/eboa -v $PATH_TO_VBOA:/vboa -v $PATH_TO_OUTPUT:/output boa_pkg
fi

echo "Generating BOA packages"
# Generate eboa package
docker exec -it $PKG_CONTAINER bash -c "cd /eboa/src; python3 setup.py sdist -d /output/"

# Generate the javascript and css necessary for VBOA
docker exec -it $PKG_CONTAINER bash -c "npm --force --prefix /vboa/src/vboa/static install"
docker exec -it $PKG_CONTAINER bash -c "npm --prefix /vboa/src/vboa/static run build"
# Copy cesium library for 3D world maps as ol-cesium needs this to be external
docker exec -it -u $HOST_USER_TO_MAP $APP_CONTAINER bash -c "cp -r /vboa/src/vboa/static/node_modules/cesium /vboa/src/vboa/static/dist"

# Generate vboa package
docker exec -it $PKG_CONTAINER bash -c "cd /vboa/src; python3 setup.py sdist -d /output/"
if [ "$PATH_TO_TAILORED" != "" ];
then
    # Generate the application package
    docker exec -it $PKG_CONTAINER bash -c "cd /$APP/src; python3 setup.py sdist -d /output/"
fi
if [ "$PATH_TO_COMMON_BASE" != "" ];
then
    # Generate the package common to several applications
    docker exec -it $PKG_CONTAINER bash -c "cd /$COMMON_BASE_FOLDER/src; python3 setup.py sdist -d /output/"
fi

echo "BOA packages generated... Removing the docker environment"
# Destroy docker environment
docker stop $PKG_CONTAINER
docker rm $PKG_CONTAINER
docker rmi boa_pkg
