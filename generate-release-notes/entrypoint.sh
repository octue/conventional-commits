#!/bin/sh -l
cd $GITHUB_WORKSPACE
echo "::set-output name=release_notes::$(compile-release-notes PULL_REQUEST_START --pull-request-url="$1" --api-token="$2" --header="$3" --list-item-symbol="$4")"
