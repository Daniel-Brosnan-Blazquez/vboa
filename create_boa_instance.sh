#################################################################
#
# Create BOA instance (tailoring of BOA for a specific project)
#
# Written by DEIMOS Space S.L. (dibb)
#
# module vboa
#################################################################

# TODO:
# Add path to common base

USAGE="Usage: `basename $0` -v path_to_vboa_src -t path_to_tailored -i ingestions_dir -w views_dir"

########
# Initialization
########
PATH_TO_VBOA=""
PATH_TO_TAILORED=""
INGESTIONS_DIR=""
VIEWS_DIR=""

while getopts v:t:i:w: option
do
    case "${option}"
    in
        v) PATH_TO_VBOA=${OPTARG};;
        t) PATH_TO_TAILORED=${OPTARG};;
        i) INGESTIONS_DIR=${OPTARG};;
        w) VIEWS_DIR=${OPTARG};;
        ?) echo -e $USAGE
            exit -1
    esac
done

# Check that option -v has been specified
if [ "$PATH_TO_VBOA" == "" ];
then
    echo "ERROR: The option -v has to be provided"
    echo -e $USAGE
    exit -1
fi

# Check that the path to the vboa project exists
if [ ! -d $PATH_TO_VBOA ];
then
    echo "ERROR: The directory $PATH_TO_VBOA provided does not exist"
    exit -1
fi

# Check that option -t has been specified
if [ "$PATH_TO_TAILORED" == "" ];
then
    echo "ERROR: The option -t has to be provided"
    echo $USAGE
    exit -1
fi

# Check that the path to the tailored project exists
if [ "$PATH_TO_TAILORED" != "" ] && [ ! -d $PATH_TO_TAILORED ];
then
    echo "ERROR: The directory $PATH_TO_TAILORED provided does not exist"
    exit -1
fi

# Check that option -i has been specified
if [ "$INGESTIONS_DIR" == "" ];
then
    echo "ERROR: The option -i has to be provided"
    echo $USAGE
    exit -1
fi

# Check that option -w has been specified
if [ "$VIEWS_DIR" == "" ];
then
    echo "ERROR: The option -w has to be provided"
    echo $USAGE
    exit -1
fi

while true; do
    read -p "
Welcome to the generator of a BOA instance :-)

You are trying to create an instance of BOA with the following configuration options:
- PATH_TO_TAILORED: $PATH_TO_TAILORED
- INGESTIONS_DIR: $INGESTIONS_DIR
- VIEWS_DIR: $VIEWS_DIR

Do you wish to proceed with the generation of the BOA instance?" answer
    case $answer in
        [Yy]* )
            break;;
        [Nn]* )
            echo "No worries, the generator will not continue";
            exit;;
        * ) echo "Please answer Y or y for yes or N or n for no. Answered: $answer";;
    esac
done

# Check if the path to the tailoring is empty
if [ ! -z "$(ls -A $PATH_TO_TAILORED)" ]; then
    while true; do
        read -p "The directory $PATH_TO_TAILORED is not empty.
            Do you wish to proceed with the generation of the BOA instance?" answer
        case $answer in
            [Yy]* )
                break;;
            [Nn]* )
                echo "No worries, the generator will not continue";
                exit;;
            * ) echo "Please answer Y or y for yes or N or n for no. Answered: $answer";;
        esac
    done
fi

# Copy scripts for initializing the development environment and generating a docker image
cp $PATH_TO_VBOA/tailoring/scripts/* $PATH_TO_TAILORED

###########################
# Build default directories
###########################
# Documentation
echo "Creating directories for documentation"
mkdir -p $PATH_TO_TAILORED/doc/tex/
mkdir -p $PATH_TO_TAILORED/doc/fig/

# Source
mkdir -p $PATH_TO_TAILORED/src

# BOA Configuration
echo "Creating directory for configuration"
mkdir -p $PATH_TO_TAILORED/src/boa_config

# BOA schemas
echo "Creating directory for schemas"
mkdir -p $PATH_TO_TAILORED/src/boa_schemas

# BOA scripts
echo "Creating directory for scripts"
mkdir -p $PATH_TO_TAILORED/src/boa_scripts

# Setup and MANIFEST
echo "Copying setup for the application"
cp $PATH_TO_VBOA/tailoring/setup/* $PATH_TO_TAILORED/src
sed -i "s/#VIEWS_DIR#/$VIEWS_DIR/g" $PATH_TO_TAILORED/src/MANIFEST.in
sed -i "s/#VIEWS_DIR#/$VIEWS_DIR/g" $PATH_TO_TAILORED/src/setup.py

###########################
# Ingestions
###########################
echo "Creating directories for the ingestions"
mkdir -p $PATH_TO_TAILORED/src/$INGESTIONS_DIR/
touch $PATH_TO_TAILORED/src/$INGESTIONS_DIR/__init__.py

# Ingestions
mkdir -p $PATH_TO_TAILORED/src/$INGESTIONS_DIR/ingestions
touch $PATH_TO_TAILORED/src/$INGESTIONS_DIR/ingestions/__init__.py

# Tests
mkdir -p $PATH_TO_TAILORED/src/$INGESTIONS_DIR/ingestions/tests

###########################
# Views
###########################
echo "Creating directories for the views"
mkdir -p $PATH_TO_TAILORED/src/$VIEWS_DIR/

# Static
mkdir -p $PATH_TO_TAILORED/src/$VIEWS_DIR/static/images

# Templates
mkdir -p $PATH_TO_TAILORED/src/$VIEWS_DIR/templates
mkdir -p $PATH_TO_TAILORED/src/$VIEWS_DIR/templates/panel
mkdir -p $PATH_TO_TAILORED/src/$VIEWS_DIR/templates/security
cp $PATH_TO_VBOA/tailoring/panel/* $PATH_TO_TAILORED/src/$VIEWS_DIR/templates/panel
cp $PATH_TO_VBOA/tailoring/security/* $PATH_TO_TAILORED/src/$VIEWS_DIR/templates/security
sed -i "s/#VIEWS_DIR#/$VIEWS_DIR/g" $PATH_TO_TAILORED/src/$VIEWS_DIR/templates/panel/index.html
sed -i "s/#VIEWS_DIR#/$VIEWS_DIR/g" $PATH_TO_TAILORED/src/$VIEWS_DIR/templates/security/login_user.html
sed -i "s/#VIEWS_DIR#/$VIEWS_DIR/g" $PATH_TO_TAILORED/src/$VIEWS_DIR/templates/security/change_password.html

# Tests
mkdir -p $PATH_TO_TAILORED/src/$VIEWS_DIR/tests

# Views
mkdir -p $PATH_TO_TAILORED/src/$VIEWS_DIR/views
cp $PATH_TO_VBOA/tailoring/app/* $PATH_TO_TAILORED/src/$VIEWS_DIR
sed -i "s/#VIEWS_DIR#/$VIEWS_DIR/g" $PATH_TO_TAILORED/src/$VIEWS_DIR/__init__.py
sed -i "s/#VIEWS_DIR#/$VIEWS_DIR/g" $PATH_TO_TAILORED/src/$VIEWS_DIR/wsgi.py

echo "The BOA instance has been created"
echo "Now, you should review the documentation to complete the instantiation"
echo "For quicker reference, at least you will have to review/complete the content of the following files to have a working instance:"
echo "$PATH_TO_TAILORED/src/setup.py"
echo "$PATH_TO_TAILORED/src/MANIFEST.in"
echo "$PATH_TO_TAILORED/src/$VIEWS_DIR/wsgi.py"
echo "$PATH_TO_TAILORED/src/$VIEWS_DIR/templates/panel/index.html"
echo "$PATH_TO_TAILORED/src/$VIEWS_DIR/templates/panel/project_header.html"
echo "$PATH_TO_TAILORED/src/$VIEWS_DIR/templates/security/login_user.html"
echo "$PATH_TO_TAILORED/src/$VIEWS_DIR/templates/security/change_password.html"
