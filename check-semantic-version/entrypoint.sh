#!/bin/sh -l

cd $GITHUB_WORKSPACE
check-semantic-version $1 $2
