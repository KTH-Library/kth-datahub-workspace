#!/usr/bin/env bash

# https://betterdev.blog/minimal-safe-bash-script-template
# https://vaneyckt.io/posts/safer_bash_scripts_with_set_euxo_pipefail
# https://wizardzines.com/comics/bash-errors
# https://social.jvns.ca/@b0rk_reruns/112033146491358262 includes comments on -E parameter
# I don't see the need for traps, so I skipped -E
set -euo pipefail

usage() {
   cat <<EOF
Usage: $(basename "${BASH_SOURCE[0]}") [-h/--help] [-v/--verbose]

This script is a convenience wrapper to rebuild MkDocs site, rebuild Docker image
and deploy the image to KTH Cloud in one go.

Available options:

-h, --help         print this help and exit
-v, --verbose      useful for debugging, sets "set -x"

EOF
   exit
}

cleanup() {
   trap - SIGINT SIGTERM ERR EXIT
   # script cleanup here
   # not doing anything at the moment
}

msg() {
   echo >&2 -e "${1-}"
}

die() {
   local msg=$1
   local code=${2-1} # default exit status 1
   msg "$msg"
   exit "$code"
}

parse_params() {
   while :; do
      case "${1-}" in
      -h | --help) usage ;;
      -v | --verbose) set -x ;;
      -?*) die "Unknown option: $1" ;;
      *) break ;;
      esac
      shift
   done
   return 0
}
parse_params "$@"

# keep track of runtime of entire script
starttime=$(date +%s)

# fetch secrets from passwordstore
# (or if you want to use this script on your own computer, simply replace the contents of these variables)
docker_host=$(pass hosts/datahub-workspace-cbhcloud/docker/host)
docker_name=$(pass hosts/datahub-workspace-cbhcloud/docker/name)
docker_path=$(pass hosts/datahub-workspace-cbhcloud/docker/path)
docker_pwd=$(pass hosts/datahub-workspace-cbhcloud/docker/pwd)

# Rebuild the site HTML/CSS in the local directory site
msg "=== mkdocs build ..."
uv run mkdocs build -d site

# Rebuild the Docker image and deploy it in one step (after authenticating, secrets redacted):
msg "=== docker login KTH Cloud ..."
docker login "$docker_host" -u "robot\$$docker_path+$docker_name" -p "$docker_pwd"
msg "=== docker buildx ..."
docker buildx build --platform="linux/amd64" -t "$docker_host/$docker_path/$docker_name" --push .

# keep track of runtime of entire script
endtime=$(date +%s)
runtime=$(( $endtime - $starttime ))

# the padding for runtime makes the formatting work
# two digits for seconds is enough for just above 1.5 minute (should never take that long)
printf "=== Script completed in %02.1f s\n" $runtime 1>&2
msg "Visit staging at https://workspace.datahub.kth.chepec.se"

exit 0
