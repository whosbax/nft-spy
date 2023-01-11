## NFT SPY
* reach https://server.jpgstoreapis.com/policy/verified?page=1
* Add collections in /spies/jpgstoreapis/config/config.yml

##### Get Asset history
```http
  GET /policy/<policy>/asset-name/<asset>
```


| Parameter | Type     | Description                       |
| :-------- | :------- | :-------------------------------- |
| `policy`  | `string` | **Required**. Collection Policy   |
| `asset`   | `string` | **Required**. Asset id            |

##### Deployment
```bash
  #force build and run
  #docker-compose --build -d
  
  #run containers
  docker-compose up    
  #same in backgroud
  #docker-compose up -d 

  #enter container nftspy
  docker exec -ti $( docker ps | grep -v mongo | grep -Eo "^[0-9a-z]+" ) /bin/bash

  #enter container mongo
  docker exec -ti $( docker ps | grep mongo | grep -Eo "^[0-9a-z]+" ) /bin/bash

  #service
  #/etc/init.d/nftspy
```

##### Mongo examples
```bash
  #enter container
    docker exec -ti $( docker ps | grep mongo | grep -Eo "^[0-9a-z]+" ) /bin/bash
  
  #enter mongocli
    mongosh "mongodb://root:password@localhost:27017"

    test> show dbs;
      #JpgStoreApi_db  396.00 KiB
      #admin           100.00 KiB
      #config          152.00 KiB
      #local            72.00 KiB
  
    test> use JpgStoreApi_db;
      #switched to db JpgStoreApi_db
    JpgStoreApi_db> show collections;
      #listings_901ba6e9831b078e131a1cc403d6139af21bda255cea6c9f770f4834
      #listings_a616aab3b18eb855b4292246bd58f9e131d7c8c25d1d1d7c88b666c4
      #...

  #group asset by name
    db.listings_11ebbfbfd62985cbae7330b95488b9dcf17ecb5e728442031362ad81.aggregate(
      [
        {
          $group :
            {
              _id : "$display_name",
              totalSaleAmount: { $count: { } }
            }
        },
        {
          $match: { "totalSaleAmount": { $gt: 1 } }
        }
      ]
    );

  #search asset
    db.listings_11ebbfbfd62985cbae7330b95488b9dcf17ecb5e728442031362ad81.fin({"display_name":"HungryCow#1277"})


```


##### Demo
```http://127.0.0.1/policy/86ec26a91051e4d42df00b023202e177a0027dca4294a20a0326a116/asset/86ec26a91051e4d42df00b023202e177a0027dca4294a20a0326a116617175616661726d657237353535```

```http://127.0.0.1/all```

```http://127.0.0.1/all/limit/1```