#!/bin/sh -l
cd $GITHUB_WORKSPACE
echo "::set-output name=release_notes::$(compile-release-notes $1 $2 $3 $4 $5)"
