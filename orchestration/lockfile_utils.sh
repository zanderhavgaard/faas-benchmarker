#!/bin/bash

source "$fbrd/fb_cli/utils.sh"

function create_bootstrap_lock {
    bootstrap_lockfile="$fbrd/experiments/$1/$2/build.lock"
    infra_lockfile="$fbrd/experiments/$1/$2/infra.lock"
    if [ ! -f "$bootstrap_lockfile" ] && [ ! -f "$infra_lockfile" ] ; then
        pmsg "$1:$2: Creating bootstrap lock ..."
        touch "$bootstrap_lockfile"
    else
        errmsg "$1:$2: Found existing lockfiles, aborting ..."
        exit 1
    fi
}

function create_infra_lock {
    bootstrap_lockfile="$fbrd/experiments/$1/$2/build.lock"
    infra_lockfile="$fbrd/experiments/$1/$2/infra.lock"
    if [ ! -f "$infra_lockfile" ] && [ -f "$bootstrap_lockfile" ] ; then
        pmsg "$1:$2: Removing bootstrap lock file ..."
        rm "$bootstrap_lockfile"
        pmsg "$1:$2: Creating infrastructure lock file ..."
        touch "$infra_lockfile"
    else
        errmsg "$1:$2: lockfile already exists, exitting ..."
        exit 1
    fi
}

function release_infra_lock {
    lockfile="$fbrd/experiments/$1/$2/infra.lock"
    if [ -f "$lockfile" ] ; then
        pmsg "$1:$2: Removing infra lock ..."
        rm "$lockfile"
    else
        errmsg "$1:$2: Could not find lockfile, exiting..."
        exit 1
    fi
}

function check_infra_lockfile {
    lockfile="$fbrd/experiments/$1/$2/infra.lock"
    if [ -f "$lockfile" ] ; then
        pmsg "$1:$2: Found lockfile ..."
    else
        errmsg "$1:$2: Could not find lockfile, exitting ..."
        exit 1
    fi
}
