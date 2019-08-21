# API Calls

All of the API calls assume the following:

* That the microservice will be behind a firewall and won't have direct contact with the outside.
* That the user management would be handled by another microservice. 

## **`Node.js` API Calls**

The API calls we'll be overviewing are the following:

### 1. **POST** - `/true/add`

Add a brand and make of shoe to the service. This requires no information from the the user regarding the user.

### 2. **POST** - `/true/addsize`

Have a user publish the true size of the given shoe. The assumption here is that the true size will be between: `1-5`.

The input this API expects. The following code is directly in the codebase. It also includes the types. 

**No user can put the true size of the shoe twice**

```ts
class ShoeRating {
    readonly userid: number; // The user that's publishing the reviewed shoe. This is to prevent the user from posting twice
    readonly maker: string; // This make of the shoe
    readonly brand: string; // This is the brand of the shoe
    readonly year: number; // This is the year of the shoe
    readonly shoeSize: number; // This is the shoe size
    readonly shoeFit: number; // This is the shoe fit
    readonly isafter: boolean; // This is a simple boolean explaining if the shoe review was placed in before or after the shoe was shipped and purchased.
}
```

### 3. **POST** - `/true/single`

Gets the true size of the given shoe. In the final version this should either be the existing mean or the estimated mean. The estimate is the number we get from the machine learning application. Call requires the same information as the true add call. 


```ts
export class SingleShoe {
    readonly maker: string;
    readonly brand: string;
    readonly year: number;
}
```

### 4. **GET** - `/true/score`

Gets the score for the machine learning application. It's useless if the machine learning application isn't added. It'll just return a 500 error explaining that the model isn't accessible.

It gets all of the shoes inside of the database then pushes their `TrueSize` to the machine learning app to see how close our models are from reality. The score can be stored into the log-server. If we insert middleware, we can use the normal logging module to save machine learning model information relevant.


## Machine Learning Proxy
It'll be a shame to go into the depth of the machine learning server itself, right now. Instead I'll overview the machine learning proxy server.

### 1. **POST** - `/train`



### 2. **POST** - `/pred`

### 3. **POST** - `/score`