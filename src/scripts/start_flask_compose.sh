# Install TAILORED
# The following options are needed to install a python package in editable mode since pip 21.3:
#   --config-setting editable_mode=compat --no-build-isolation --use-pep517
# Reference: https://github.com/pypa/pip/issues/11457
echo "###########################"
echo "# Installing tailored BOA #"
echo "###########################"
python -c "import $FLASK_APP" &> /dev/null
flask_app_installed=`echo $?`
if [ $flask_app_installed != 0 ];
then
    pip3 install -e "/tboa/src[tests]"
    echo "Tailored BOA installed"
else
    echo "Tailored BOA was already installed"
fi

# Install ORC and minArc packages if provided
echo
echo "###################################"
echo "Installing ORC and minArc packages"
echo "###################################"
orc_installed=`gem list -i "^orc$"`
if [ $orc_installed == "false" ];
then
    for file in `find /orc_packages -name '*' -type f`;
    do
        file_name=`basename $file`
        echo "Installing ruby package: $file_name"
        gem install $file
        echo "Ruby package: $file_name, has been installed"
    done
else
    echo "ORC and minArc packages already installed"
fi

# Link to tailored BOA configurations
echo
echo "#########################"
echo "Installing configurations"
echo "#########################"
if [ -d /tboa/src/boa_config ];
then
    for file in `find /tboa/src/boa_config -name '*' -type f`;
    do
        file_name=`basename $file`
        echo "Installing configuration file: $file_name"
        # Remove file it existed already
        if [ -f /resources_path/$file_name ];
        then
            rm /resources_path/$file_name;
        fi
        ln -s /tboa/src/boa_config/$file_name /resources_path/$file_name
        echo "Configuration file: $file_name, has been installed"
    done
else
    echo "There are no tailored BOA configurations"
fi

# Link to tailored BOA schemas
echo
echo "##################"
echo "Installing schemas"
echo "##################"
if [ -d /tboa/src/boa_schemas ];
then
    for file in `find /tboa/src/boa_schemas -name '*' -type f`;
    do
        file_name=`basename $file`
        echo "Installing schema file: $file_name"
        # Remove file it existed already
        if [ -f /schemas/$file_name ];
        then
            rm /schemas/$file_name;
        fi
        ln -s /tboa/src/boa_schemas/$file_name /schemas/$file_name
        echo "Schema file: $file_name, has been installed"
    done
else
    echo "There are no tailored BOA schemas"
fi

# Link to tailored BOA scripts
echo
echo "##################"
echo "Installing scripts"
echo "##################"
if [ -d /tboa/src/boa_scripts ];
then
    for file in `find /tboa/src/boa_scripts -name '*' -type f`;
    do
        file_name=`basename $file`
        echo "Installing script file: $file_name"
        # Remove file it existed already
        if [ -f /scripts/$file_name ];
        then
            rm /scripts/$file_name;
        fi
        ln -s /tboa/src/boa_scripts/$file_name /scripts/$file_name
        echo "Script file: $file_name, has been installed"
    done
else
    echo "There are no tailored BOA scripts"
fi

# Install cron activities
echo
echo "##########################"
echo "Installing cron activities"
echo "##########################"
if [ -d /tboa/src/boa_cron/boa_cron ];
then
    if [ -f "/tboa/src/boa_cron/boa_cron" ];
    then
        cp /tboa/src/boa_cron/boa_cron /cron/
        echo "Cron file: $file_name, has been installed"
    fi
else
    echo "There are no tailored BOA cron activities"
fi

# Copy the environment variables to a file for later use of cron
echo
echo "##############################################################"
echo "Copy the environment variables to a file for later use of cron"
echo "##############################################################"
declare -p | grep -Ev 'BASHOPTS|BASH_VERSINFO|EUID|PPID|SHELLOPTS|UID' > /resources_path/container.env
echo "Environment variables copied into file: /resources_path/container.env"

# Start flask server on port 5000 for testing purposes
echo
echo "#######################################"
echo "Start flask server for testing purposes"
echo "#######################################"
export VBOA_DEBUG=FALSE; export VBOA_TEST=TRUE; nohup flask run --host=0.0.0.0 -p 5000 &> /log/flask_5000.log &
echo "Flask server for testing purposes started and listening at port 5000. Logs are dropped into file: /log/flask_5000.log"

# Start flask server on port 5001 for SSL connection
# Create certificates if they are not available
if [ ! -f /resources_path/boa_certificate.pem ] || [ ! -f /resources_path/boa_key.pem ];
then
    echo
    echo "###################"
    echo "Create certificates"
    echo "###################"
    openssl req -x509 -newkey rsa:4096 -nodes -out /resources_path/boa_certificate.pem -keyout /resources_path/boa_key.pem -subj "/emailAddress=daniel.brosnan@elecnor.es/C=SP/ST=Madrid/L=Tres Cantos/O=Elecnor Deimos/OU=Ground Segment/CN=BOA"
    echo "Certificates generated into files: /resources_path/boa_certificate.pem, /resources_path/boa_key.pem"
fi
echo
echo "#############################################"
echo "Start flask server to access from the browser"
echo "#############################################"
export VBOA_DEBUG=TRUE; export VBOA_TEST=TRUE; nohup flask run --cert=/resources_path/boa_certificate.pem --key=/resources_path/boa_key.pem  --host=0.0.0.0 -p 5001 &> /log/flask_5001.log &
echo "Flask server to access from the browser started and listening at port 5001. Logs are dropped into file: /log/flask_5001.log"

echo
echo "##############"
echo "Sleep infinity"
echo "##############"
sleep infinity
