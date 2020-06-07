#!/bin/bash

source "$fbrd/fb_cli/utils.sh"

function create_infra_lock {
    lockfile="$fbrd/experiments/$1/$2/infra.lock"
    if [ ! -f "$lockfile" ] ; then
        pmsg "$1:$2: Creating infrastructure lock file ..."
        touch "$lockfile"
    else
        errmsg "$1:$2: lockfile already exists, exitting ..."
        exit
    fi
}

function release_infra_lock {
    lockfile="$fbrd/experiments/$1/$2/infra.lock"
    if [ -f "$lockfile" ] ; then
        pmsg "$1:$2: Removing infra lock ..."
        rm "$lockfile"
    else
        errmsg "$1:$2: Could not find lockfile, exiting..."
        exit
    fi
}

function check_infra_lockfile {
    lockfile="$fbrd/experiments/$1/$2/infra.lock"
    if [ -f "$lockfile" ] ; then
        pmsg "$1:$2: Found lockfile ..."
    else
        errmsg "$1:$2: Could not find lockfile, exitting ..."
        exit
    fi
}
