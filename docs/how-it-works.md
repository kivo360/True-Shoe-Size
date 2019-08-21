# How Things Work

This document explains how the various parts of the application works. The subjects we'll be overviewing are the following:

* The service system design.
* The machine learning microservice.


The reason for this design document is to make aware of how these sets of microservices work and why. To start, I'll get into the machine learning microservice.


## Machine Learning Microservice

To appropiately handle online learning, we need to handle online regressions appropiately appropiately. This means the model updates per data point instead of training it once and calling it a day.

I'm using a library I created to host these models called `funguauniverse` it's a pypi library I used to create full online machine learning pipelines and deploy online, non-static models in as little as `3-4 hours` using python. 

The non-static model is periodically saved inside of storage and is assigned meta-data according to what the user sets. The metadata is stored inside of `mongodb`. The reason it's stored inside of mongodb is so one can dynamically create schemas and use them. The key element to the schema is that the docuement must include a `type` and `timestamp`. These are both constraints using the `funtime` database library, which I also created, where the user can do timeseries queries quickly on mongodb. 

The timeseries query is done using the `timestamp`, and the `type` is an explicit entity identifier. It must be there so we can find all documents of its entity class.

The `funtime` database can help with a lot more specialized timeseries queries as well. It has a lot of the functionality of influxdb.