#!/usr/bin/env bash

SCRIPTDIR="$(readlink -f `dirname $0`)"
cd "$(git rev-parse --show-toplevel)"

SRV_ADDR="127.0.0.1:64956"
SRV_WEBDIR="/tmp/omega-temp-server/"

# reset srv_webdir
mkdir -p "$SRV_WEBDIR"

# inject backdoor on server
./omega -e 'set BACKDOOR %%DEFAULT%%; exploit --get-backdoor' > "$SRV_WEBDIR/index.php"

# return omega command
echo "use the following command to connect omega to server:"
echo "    ----------------------------------------"
echo "    $(pwd)/omega -t $SRV_ADDR -ie 'set BACKDOOR %%DEFAULT%%; set REQ_HEADER_PAYLOAD %%DEFAULT%%; exploit'"
echo "    ----------------------------------------"

# start server
php -S "$SRV_ADDR" -t "$SRV_WEBDIR"
