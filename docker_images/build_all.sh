# exit when any command fails
set -e

for folder in game-node redis-server server
do 
    echo "Updating task $folder..."
    cd $folder
    sh build.sh
    cd ..
    echo "Done updating task $folder"
done
