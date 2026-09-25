# exit when any command fails
set -e

# The three images are independent, so build them in parallel to cut down
# total wall-clock time. Set DOCKER_PLATFORM (e.g. linux/amd64) in the
# environment to cross-build for a different architecture; left unset,
# builds target the host arch natively (much faster, e.g. avoids amd64
# emulation on Apple Silicon).
pids=""
statuses_dir=$(mktemp -d)

for folder in game-node redis-server server
do
    (
        echo "Building $folder..."
        cd "$folder"
        if sh build.sh > "$statuses_dir/$folder.log" 2>&1; then
            echo "Done building $folder"
        else
            echo "FAILED building $folder"
            exit 1
        fi
    ) &
    pids="$pids $!"
done

exit_code=0
for pid in $pids; do
    wait "$pid" || exit_code=1
done

for folder in game-node redis-server server
do
    echo "----- $folder log -----"
    cat "$statuses_dir/$folder.log"
done

rm -rf "$statuses_dir"

exit $exit_code
