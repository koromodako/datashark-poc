#!/usr/bin/env bash
# -!- encoding:utf8 -!-
#
# ENVARS
#
PWD=$(pwd)
PIP=$(which pip3)
CORE_DIR="core"
CONF_SRC_DIR="${CORE_DIR}/config"
CONF_DST_DIR="${HOME}/.config/datashark"
BIN_DST_DIR="${HOME}/bin"
#
# FUNCTIONS
#
function check_python_version {
	echo "checking python version..."
	VALID=$(python3 -c 'import sys; v=sys.version_info[:]; print("OK" if v[0] >= 3 and v[1] >= 6 else "")')
	if [ "${VALID}" == "" ]
	then
		echo "please install Python version 3.6.x or newer."
		exit 1
	fi
}

function install_python_requirements {
	if [ "${PIP}" == "" ]
	then
		echo "please install pip3 first."
		exit 1
	else
		echo "installing requirements <${1}>..."
		sudo ${PIP} install -r ${1}
	fi
}

function makedirs {
	echo "making directory <${1}>..."
	mkdir -p ${1}
}

function deploy_conf {
	echo "deploying <${1}> configuration file..."
	cp -i ${CONF_SRC_DIR}/${1}.conf.dist ${CONF_DST_DIR}/${1}.conf
}

function deploy_command {
	echo "deploying <${1}> command..."
	ln -s -i ${PWD}/${1} ${BIN_DST_DIR}/${1}
}
#
# SCRIPT
#
##
## Install Python requirements
##
check_python_version
install_python_requirements ${CORE_DIR}/requirements.txt
##
## Copy configuration file
##
makedirs ${CONF_DST_DIR}
deploy_conf datashark
deploy_conf whitelist
deploy_conf blacklist
deploy_conf dissection
##
## Create symlinks
##
makedirs ${BIN_DST_DIR}
deploy_command datashark
deploy_command datashark-gui
