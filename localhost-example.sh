#! /bin/bash

echo "Start the snappy data server"
podman run \
    --detach \
    --name=snappy \
    --net=host \
    --env DATA_SERVER_PUBLIC_HOST=localhost \
    --env DATA_SERVER_PORT=7070 \
    --env DATA_SERVER_LOG_LVL=info \
    --volume "$HOME/data_server/results:/data_server/app/results:z" \
    quay.io/openshift-scale/snappy-data-server
sleep 2

FILE=red-hat.jpg
echo  "Post the file $FILE"
curl localhost:7070/api --form file=@$FILE
echo ""
sleep 2

echo "Validate $FILE is in server storage"
diff $FILE $HOME/data_server/results/$FILE
if [[ $? == 0 ]]; then
    echo "$FILE was posted to the server and saved!"
fi
sleep 2

echo "Stopping and removing the snappy data server"
podman rm -f snappy