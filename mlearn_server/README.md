# PA Regressor Service

Concurrent PA Regressor that will run in container. 

This is V1. We'll refactor this to support training and utilizing services in a cluster. This will increase the training and predictions at scale. Right now this will work on one server with 36 vCPU cores.

We do this by decoupling the predictions in the pipeline and directly placing every prediction in storage (S3) after training and use. While also increasing the number of workers (increasingly).
