# Get A Real Shoe Size

## Description
Create a github repository for the `true shoe size`. This is all run using the `nest.js` framework while using `TrueORM` to run connections to `Postgresql`.

## How to Read this README Guide

This application documents come in 4 parts:

1. The intro installment guide on this `README.md`
   * This part is cruicial for getting the basic node.js application app up. The basic node.js app doesn't inculde the machine learning service.
   * This is focused only on setting up the key database (postgresql) and run the docker file.
   * At the end of running this document you should have the Node.js service completely up and running. The very nature of the application is that it'll work entirely fine without the machine learning aspect. The machine learning feature is there to provide the user with an estimate of the true size of the application.
2. The README in the [docs folder](docs/README.md). The fundamental aspect of the README here is that it highlights the inner workings of the nestjs framework upfront. The key difference is that it's separate from the main document as highlighted [here](https://docs.nestjs.com/).
3. The [docs folder](docs/README.md) also has information regarding the API calls. It explains what the developer might want to call to get various responses.
   * The documentation also should explain what you need to know to test the full pipeline automatically. The full pipeline includes the following:
     * `Node.js/Typescript` Microservice
     * Machine learning proxy microservice using `Python`
       * A `uvloop` based microservice on python (the same event-loop from node.js) that prepares the data to be sent to the `online machine learning service`. This also buffers all of the calls to the machine learning service (only capping at 200 req/sec with single machine training)
     * The machine learning service itself.
       * This service is responsible for training the regression model online. Online Learning, according to the Quora writer, [Håkon Hapnes Strand](https://qr.ae/TWGSCl), is a machine learning model that trains itself for ever new bit of data that comes in.
4. `How-it-works` document in the [docs folder](docs/README.md). This document will be used to explain how the various services work. The key service you'll want to understand is the machine learning microservice. For online learing to work in a production-like manner, we need to store the model inside of a local storage or an external store such as S3 or azure datalake. This needs to be done periodically. We'll explain how this is done inside of the document. 

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

After running running the following, you should be able to run the `node.js` app as root in `postgresql`.

## Installation Guide for Machine Learning

For the machine learning process we use mongodb and python for it to operate. The mongodb database is a flat document store. One in which we use to store meta-data regarding the model stored inside the machine learning model. I'll explain how it's used inside of the how it works database.


I'm assuming the transition is from Ubuntu on Windows or some other debian based operating system. Prior to following the rest of the document, please read and follow:

> https://tutorials.ubuntu.com/tutorial/tutorial-ubuntu-on-windows#0

After you follow that tutorial, please follow this tutorial to install all of python/python3:
> http://timmyreilly.azurewebsites.net/python-with-ubuntu-on-windows/

### Installing Pip3 and pipenv
I use `pipenv` to ensure all of this code works properly. Before continuing. Open `Ubuntu on Windows` and begin with installing the following commands:

**This upgrades your system**
```bash
sudo apt-get update
sudo apt-get -y upgrade
```

**This installs everything necessary**

```
sudo apt-get install -y python3-pip
sudo apt-get install build-essential libssl-dev libffi-dev python-dev
```

**Try testing to see if that worked by running a simple numpy operation**

```
pip3 install numpy
python3
```

You should enter into a shell and be able to run python code.


Now install pipenv:

>`pip install --user --upgrade pipenv`

### Installing MongoDB Ubuntu
We use mongodb to manage timeseries data. Make sure to install. 
Run these from the site given:
> https://docs.mongodb.com/manual/tutorial/install-mongodb-on-ubuntu/

```
sudo apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv 9DA31620334BD75D9DCB49F368818C72E52529D4
```

```
echo "deb [ arch=amd64 ] https://repo.mongodb.org/apt/ubuntu bionic/mongodb-org/4.0 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-4.0.list
```

```
sudo apt-get update
sudo apt-get install -y mongodb-org
```

#### Run it:
```
sudo service mongod start
```

```
sudo service mongod stop # To stop
sudo service mongod restart # To restart
```


## Accessing Your Files In Ubuntu On Windows 10

Please follow the tutorial for accessing your files:

> https://www.howtogeek.com/261383/how-to-access-your-ubuntu-bash-files-in-windows-and-your-windows-system-drive-in-bash/


### Finishing Setup
Now, enter into the two separate folders and install the required packages for the machine learning.

To install all of the dependencies: **Run:** 

```bash
$ cd 
$ pipenv install -e .
```

This installs all of the main dependencies for the project. Follow that with: `pipenv shell` in the main directory to enter into the project's virtual environment.


### How to Run `S3`
To run the necessary test, you'll need to first get IAM keys for s3 (to test s3 functionality). The keys need to have s3 access and be stored in `~/.aws/credentials`. 

### Test Methods

To test, after you activate `pipenv shell`, run `python setup.py test` at the root of the command line. After it's run you should have the full capacity see which tests work or don't.
