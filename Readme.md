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
  #build and run
  docker-compose --build -d
  
  #enter container
  docker exec -ti jpeg_snipe_py-jpeg_snipe-1 /bin/bash
  
  #start flask (started in build)
  #python3 ./api.py &
```

##### Demo
```http://127.0.0.1/policy/86ec26a91051e4d42df00b023202e177a0027dca4294a20a0326a116/asset/86ec26a91051e4d42df00b023202e177a0027dca4294a20a0326a116617175616661726d65723631333```

