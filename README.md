# StockX Interview

## Description
Create a github repository for the `true shoe size`. This is all run using the `nest.js` framework while using `TrueORM` to run connections to `Postgresql`.


## Installation in Development

```bash
$ npm install
```

## Running the app

This makes the assumption that you're at the root of the folder.

```bash
# development
$ npm run start

# watch mode
$ npm run start:dev

# production mode
$ npm run start:prod
```

## Test

```bash
# unit tests
$ npm run test

# e2e tests
$ npm run test:e2e

# test coverage
$ npm run test:cov
```


## Running Using Docker

There's two modes to run the application using docker. Inside of development mode and production mode. The instructions to run in each are different.

### Development Mode

Inside of development mode we tether to the host machine to access the local database. Usually this should be to check to see if the microservice

```bash
# Build the image on your host machine
$ docker build -t stockx_env .

# Run the stockx enviornment
$ docker run -it --net=host stockx_env
```

The app should then run on port `3000`.


### Production Mode

Here you set the database you're aiming to run to by setting the database host, port, database username & password, then the actual database itself. This to be an expected external service, such as Amazon Aurora or RDS.

```bash
# Build the image on your host machine. This is a build just as we've seen it before.
$ docker build -t stockx_env .

# Run the stockx enviornment using the various postgres environment variables. 
$ docker run -it -e DBPORT='5432' \
                 -e POSTUSER='root' \
                 -e POSTPASS='root' \
                 -e DATABASE='db' \
```


## Installing Postgresql

Following Tutorial: We're working on the [following tutorial](https://tecadmin.net/install-postgresql-server-on-ubuntu/). 

### Linux (Debian/Ubuntu)

```bash
# Download keys
$ sudo apt-get install wget ca-certificates
$ wget --quiet -O - https://www.postgresql.org/media/keys/ACCC4CF8.asc | sudo apt-key add -
$ sudo sh -c 'echo "deb http://apt.postgresql.org/pub/repos/apt/ `lsb_release -cs`-pgdg main" >> /etc/apt/sources.list.d/pgdg.list'


# Update the repositories & Install Postgresql
$ sudo apt-get update
$ sudo apt-get install postgresql postgresql-contrib


# Connect to postgresql
$ sudo su - postgres
$ psql

postgres-# \conninfo

postgres-# \q
```