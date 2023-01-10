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
  
  #enter container
  docker exec -ti $( docker ps | grep -v mongo | grep -Eo "^[0-9a-z]+" ) /bin/bash
  
  #service
  #/etc/init.d/nftspy
```

##### Demo
```http://127.0.0.1/policy/86ec26a91051e4d42df00b023202e177a0027dca4294a20a0326a116/asset/86ec26a91051e4d42df00b023202e177a0027dca4294a20a0326a116617175616661726d657237353535```
```http://127.0.0.1/all```
```http://127.0.0.1/all/limit/1```