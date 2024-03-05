#!/bin/bash

# Define the directories where you want to move the files
CGI_TARGET_DIR="/usr/lib/cgi-bin"
HOME_DIR=~/assignment_files

# Create a directory in the home directory for the assignment files
mkdir -p $HOME_DIR

# Unpack the tarball into the new directory
tar -xzvf assignment_files.tar.gz -C $HOME_DIR

# Move the CGI files to the CGI target directory
find $HOME_DIR -name "*.cgi" -exec mv {} $CGI_TARGET_DIR \;