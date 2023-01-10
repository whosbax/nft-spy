#! /bin/bash
until nc -z $MONGO_INITDB_IP 27017
do
    sleep 1
done

/etc/init.d/nftspy start