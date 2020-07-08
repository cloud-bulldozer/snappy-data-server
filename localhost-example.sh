#! /bin/bash

echo "Start the snappy data server"
container_id=$(podman run \
    --detach \
    --name=snappy \
    --net=host \
    --env DATA_SERVER_PUBLIC_HOST=localhost \
    --env DATA_SERVER_PORT=7070 \
    --env DATA_SERVER_LOG_LVL=info \
    --volume "$HOME/data_server/results:/data_server/app/results:z" \
    quay.io/openshift-scale/snappy-data-server)
echo "Server Container id: $container_id"
sleep 2

file=red-hat.jpg
echo "Post the file $file"
echo "Server response: $(curl localhost:7070/api --form file=@$file)"
sleep 2

echo "Validate $file is in server storage"
diff $file $HOME/data_server/results/$file
if [[ $? == 0 ]]; then
    echo "$file was posted to the server and saved!"
fi
sleep 2

echo "Stopping and removing the snappy data server"
podman rm -f $container_id 1> /dev/null