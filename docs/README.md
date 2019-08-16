# How This Project Was Built

This project was built using the framework `nest`. 

The entire idea of the `nest` framework is that it takes and abstracts away everything from `express.js` and `fastify.js` for easy creation of APIs on `typescript`. They have some pieces available to allow for extremely loosely coupled via robust microservices.


The key components for the `nest.js` :

1. `Controllers` - These handle requests and reponses
2. `Providers` - These handle injections
3. `Modules` - These are aggregates of providers and controllers. They allow everything to be injected into a single place.
    * Modules can accept other modules
    * This means we can bundle all relavent pieces of code together inside of their own modules. 


Some relavant pieces of code you'll read.