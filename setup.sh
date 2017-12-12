#/usr/bin/env bash
#
# ENVARS
#
BIN_DIR="~/bin"
CONF_DIR="~/.config/datashark"
#
# Copy configuration file
#
mkdir -p ${CONF_DIR}
cp core/datashark.conf.dist ${CONF_DIR}/datashark.conf
#
# Create symlinks
#
mkdir -p ${BIN_DIR}
ln -s datashark ${BIN_DIR}/datashark
ln -s datashark-gui ${BIN_DIR}/datashark-gui
