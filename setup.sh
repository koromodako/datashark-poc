#!/usr/bin/env bash
# -!- encoding:utf8 -!-
#
# ENVARS
#
PWD=$(pwd)
CONF_SRC_DIR="core/config"
CONF_DST_DIR="${HOME}/.config/datashark"
BIN_DST_DIR="${HOME}/bin"
#
# FUNCTIONS
#
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
