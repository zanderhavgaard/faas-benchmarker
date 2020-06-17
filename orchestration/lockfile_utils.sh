#!/bin/bash

source "$fbrd/fb_cli/utils.sh"

function create_lock {
    experiment_name=$1
    platform=$2
    lock_type=$3
    lockfile="$fbrd/experiments/$experiment_name/$platform/$lock_type.lock"
    case "$lock_type" in

        build)
            if ! check_lock "$experiment_name" "$platform" "build" \
                && ! check_lock "$experiment_name" "$platform" "infra" \
                && ! check_lock "$experiment_name" "$platform" "destroy"
            then
                pmsg "$experiment_name:$platform: Creating $lock_type lock ..."
                touch "$lockfile"
                return 0
            else
                errmsg "$experiment_name:$platform: No lockfiles may be present, aborting ..."
                return 1
            fi
            ;;

        infra)
            if check_lock "$experiment_name" "$platform" "build" \
                && ! check_lock "$experiment_name" "$platform" "infra" \
                && ! check_lock "$experiment_name" "$platform" "destroy"
            then
                pmsg "$experiment_name:$platform: Releasing build lock ..."
                release_lock "$experiment_name" "$platform" "build"
                pmsg "$experiment_name:$platform: Creating $lock_type lock ..."
                touch "$lockfile"
                return 0
            else
                errmsg "$experiment_name:$platform: Must only be a build lock, aborting ..."
                return 1
            fi
            ;;

        destroy)
            if ! check_lock "$experiment_name" "$platform" "build"  \
                && check_lock "$experiment_name" "$platform" "infra" \
                && ! check_lock "$experiment_name" "$platform" "destroy"
            then
                pmsg "$experiment_name:$platform: Releasing infra lock ..."
                release_lock "$experiment_name" "$platform" "infra"
                pmsg "$experiment_name:$platform: Creating $lock_type lock ..."
                touch "$lockfile"
                return 0
            else
                errmsg "$experiment_name:$platform: Must only be a destroy lock, aborting ..."
                return 1
            fi
            ;;

        *)
            errmsg "Unknown lock, exiting ..."
            exit 1
            ;;
    esac
}

function release_lock {
    rl_experiment_name=$1
    rl_platform=$2
    rl_lock_type=$3
    rl_lockfile="$fbrd/experiments/$rl_experiment_name/$rl_platform/$rl_lock_type.lock"
    case "$rl_lock_type" in

        build)
            if check_lock "$rl_experiment_name" "$rl_platform" "build" \
                && ! check_lock "$rl_experiment_name" "$rl_platform" "infra" \
                && ! check_lock "$rl_experiment_name" "$rl_platform" "destroy"
            then
                pmsg "$rl_experiment_name:$rl_platform: Releasing $rl_lock_type lock ..."
                rm "$rl_lockfile"
                return 0
            else
                errmsg "$rl_experiment_name:$rl_platform: Must only be a build lock, aborting ..."
                return 1
            fi
            ;;

        infra)
            if ! check_lock "$rl_experiment_name" "$rl_platform" "build" \
                && check_lock "$rl_experiment_name" "$rl_platform" "infra" \
                && ! check_lock "$rl_experiment_name" "$rl_platform" "destroy"
            then
                pmsg "$rl_experiment_name:$rl_platform: Releasing $rl_lock_type lock ..."
                rm "$rl_lockfile"
                return 0
            else
                errmsg "$rl_experiment_name:$rl_platform: Must only be a infra lock, aborting ..."
                return 1
            fi
            ;;

        destroy)
            if ! check_lock "$rl_experiment_name" "$rl_platform" "build"  \
                && ! check_lock "$rl_experiment_name" "$rl_platform" "infra" \
                && check_lock "$rl_experiment_name" "$rl_platform" "destroy"
            then
                pmsg "$rl_experiment_name:$rl_platform: Releasing $rl_lock_type lock ..."
                rm "$rl_lockfile"
                return 0
            else
                errmsg "$rl_experiment_name:$rl_platform: Must only be a destroy lock, aborting ..."
                return 1
            fi
            ;;

        *)
            errmsg "Unknown lock, exiting ..."
            exit 1
            ;;
    esac
}

function check_lock {
    en=$1
    p=$2
    lt=$3
    lf="$fbrd/experiments/$en/$p/$lt.lock"
    # pmsg "$en:$p: Checking for $lt lock ..."
    if [ -f "$lf" ] ; then
        # pmsg "$en:$p: Found $lt lock ..."
        return 0
    else
        # pmsg "$en:$p: Did not find $lt lock ..."
        return 1
    fi
}
