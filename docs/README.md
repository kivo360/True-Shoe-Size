# How This Project Was Built

This project was built using the framework `nest`. 

The entire idea of the `nest` framework is that it takes and abstracts away everything from `express.js` and `fastify.js` for easy creation of APIs on `typescript`. They have some pieces available to allow for extremely loosely coupled via robust microservices. To understand how the machine learning service works. Visit this document [here](how-it-works.md).


The key components for the `nest.js` :

1. `Controllers` - These handle requests and reponses
2. `Providers` - These handle injections
3. `Modules` - These are aggregates of providers and controllers. They allow everything to be injected into a single place.
    * Modules can accept other modules
    * This means we can bundle all relavent pieces of code together inside of their own modules. 


Some relavant pieces of code you'll read:

## Declaring Controllers

Controllers are the main locations where we get requests and return a response. Each controller can have a handle that acts as the fundamental endpoint. For instance, in the following example we'll see that the controller has the handle `cats`. Everything beyond that point is an extension to that. For example `@Get()` is the route `/cats/`. If we use the example `@Get('all')`, the route would be `/cats/all`

```ts
import { Controller, Get } from '@nestjs/common';

@Controller('cats')
export class CatsController {
  @Get()
  findAll(): string {
    return 'This action returns all cats';
  }
}
```