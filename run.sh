#! /bin/bash
until nc -z $MONGO_INITDB_IP 27017
do
    sleep 1
done
running=$( ps aux | grep -Ec "(api|main)" )

echo "health check.."
if [ "$running" -lt 4 ] 
then
        echo "restart nftpy"
        /etc/init.d/nftspy restart
else
echo "nftpy is running"
fi
