#!/bin/bash

CURRENTDATE=`date +"%Y-%m"`
CURRENTEPOCTIME=`date +"%s"`

echo ${CURRENTDATE}_${CURRENTEPOCTIME}

mkdir -p ~/.local/bin/scribe
mkdir -p ~/.config/scribe

echo Creating backup ~/.local/bin/scribe_${CURRENTDATE}${CURRENTEPOCTIME}
mv ~/.local/bin/scribe ~/.local/bin/scribe_${CURRENTDATE}${CURRENTEPOCTIME}

#in future we should handle the config file better
#back up old config
mv ~/.config/scribe/scribe.config  ~/.config/scribe/scribe.config_${CURRENTDATE}${CURRENTEPOCTIME}

#run the normal install script
~/source/scribe/install.sh

echo **upgrade complete**
