#!/bin/bash
#script to install scribe to ~/.local/bin
echo ===== Scribe install script ========
src_dir=.
dest_dir=~/.local/bin/scribe
conf_dir=~/.config/scribe
release_db="/home/marc/Sync/scribe/scibe_data.db"

mkdir -p $dest_dir
mkdir -p $dest_dir/scripts
mkdir -p $dest_dir/resources
mkdir -p $conf_dir

cp $src_dir/*.py $dest_dir
cp $src_dir/scripts/* $dest_dir/scripts
cp $src_dir/resources/* $dest_dir/resources
cp $src_dir/scribe.config $conf_dir

#remove original config file
#rm $dest_dir/scribe.conifg

# Set release to True
file=$dest_dir/version_info.py
sed -i -e 's/release = False/release = True/g' $file

#set database to the default release path - note as string contains '/' use ':' as delimiter
conf_file=$conf_dir/scribe.config
sed -i -e 's:database = /home/marc/Documents/marcnotes_db:database = /home/marc/Sync/scribe/scribe_data.db:g' $conf_file

echo Finished!
