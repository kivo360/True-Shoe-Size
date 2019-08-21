# How Things Work

This document explains how the various parts of the application works. The subjects we'll be overviewing are the following:

* The system design.
* The machine learning microservice.


The reason for this design document is to make aware of how these sets of microservices work and why. To start, I'll get into the machine learning microservice.


## Service system design

The system design includes: |`node.js` server| <-> |`python` high I/O proxy server| <-> |machine learning service|

The reason for this system design is to reduce the number of calls directly to the machine learning service. If we have direct information on the node.js end, we can prevent ourselves from touching the I/O proxy server. If data is not in the correct format, or needs to be slightly modified prior to being used by the machine learning model, it can happen via the proxy service or filtered out. The end result is that the user experiences reasonable response times, and only getting `50-100ms` slowdowns when the user is getting a pair of sneakers nobody has voted on before.


## Machine Learning Microservice

To appropiately handle online learning, we need to handle online regressions appropiately appropiately. This means the model updates per data point instead of training it once and calling it a day.

I'm using a library I created to host these models called `funguauniverse` it's a pypi library I used to create full online machine learning pipelines and deploy online, non-static models in as little as `3-4 hours` using python. 

The non-static model is periodically saved inside of storage and is assigned meta-data according to what the user sets. The metadata is stored inside of `mongodb`. The reason it's stored inside of mongodb is so one can dynamically create schemas and use them. The key element to the schema is that the docuement must include a `type` and `timestamp`. These are both constraints using the `funtime` database library, which I also created, where the user can do timeseries queries quickly on mongodb. 

The timeseries query is done using the `timestamp`, and the `type` is an explicit entity identifier. It must be there so we can find all documents of its entity class.

The `funtime` database can help with a lot more specialized timeseries queries as well. It has a lot of the functionality of `influxdb`.


![diagram_how_works](images/renessance_man.gif)


## The Gist
The idea is that the model that's getting trained in live is stored inside of a hash table and is periodically stored inside of storage. The hash table is holds any form of data that needs to be quickly accessed. For this example, the data that's stored in memory are the scalars (evening out data), the model itself, and the list of makes to fully partital_fit the labels using sklearn's `LabelEncoder`, as it doesn't have any partial fit capabilities. Every 1 minute, the data is stored into storage (local or s3 depending on the settings) with the associated data. It does this using a `background thread`.

The data itself is referenced by hash. The hash is generated using a `dict`, which is an object to identify the model we want to work with. The dictionary we use to identify the data is also the metadata we use to locate the most recent model inside of our mongodb database.


This design is single machine right now, though it'll be very easy to replace the hash-table from a pythonic `dict` and replace it using `redis`. Where the machine learning model would be periodically updated and stored to redis as a replacement for memory. That way the model would be accessible from multiple machines inside of a docker cluster (perhap managed by `kubernetes`). Redis would then be a foundation for scaling between many machines. The machines themselves would take turns updating and sharing stuff via hash. 

The means of access is done using the client.py file. It pickles file inputs then transports the data into the model. The pickled information itself can be of any serializable data type. Including `numpy arrays`, or pandas `dataframe`. If the data is extremely large it should be pulled from a large web source, then processed on. Otherwise, all extremely small data `< 500MB` can be sent through the http interface. GZip can be used to pass more data through faster.


Because we're storing all models inside of the local store, if the server dies, and restarts, we can pull that model in from memory and continue from where we left off.

**All of the code can be seen in mlearn_server**

