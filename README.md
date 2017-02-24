# caipirinha
Visualization metadata information for Lemonade Project

### Install
```
git clone git@github.com:eubr-bigsea/caipirinha.git
cd caipirinha
pip install -r requirements.txt
```

### Config
Copy `caipirinha.yaml.example` to `caipirinha.yaml`
```
cp caipirinha.yaml.example caipirinha.yaml
```

Create a database named `caipirinha` in a MySQL server and grant permissions to a user.
```
#Example
mysql -uroot -pmysecret -e "CREATE DATABASE caipirinha;"
```

Edit `caipirinha.yaml` according to your database config
```
caipirinha:
    debug: true
    environment: prod
    port: 3324
    servers:
        database_url: mysql+pymysql://user:secret@server:3306/caipirinha
        redis_url: redis://localhost:6379
        #redis_url: redis://beta.ctweb.inweb.org.br:6379
    services:
    config:
        SQLALCHEMY_POOL_SIZE: 0
        SQLALCHEMY_POOL_RECYCLE: 60
```
### Create tables in the database
CAIPIRINHA_CONFIG=caipirinha.yaml PYTHONPATH=. python caipirinha/manage.py upgrade

### Run
```
CAIPIRINHA_CONFIG=caipirinha.yaml PYTHONPATH=. python caipirinha/app.py
```

#### Using docker
Build the container
```
docker build -t bigsea/caipirinha .
```

Repeat [config](#config) stop and run using config file
```
docker run \
  -v $PWD/caipirinha.yaml:/usr/src/app/caipirinha.yaml \
  -p 3321:3321 \
  bigsea/caipirinha
```
