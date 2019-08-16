# API Calls

All of the API calls assume the following:

* That the microservice will be behind a firewall and won't have direct contact with the outside.
* That the user management would be handled by another microservice. 

The API calls we'll be overviewing are the following:

## 1. /true/add

Add a model and make of shoe to the service. This requires no information from the the user regarding the user.

## 2. /true/addsize

Have a user publish the true size of the given shoe. The assumption here is that the true size will be between: 1-5.

The input this API expects. The following code is directly in the codebase. It also includes the types. 

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

## 3. /true/single

Gets the true size of the given shoe. In the final version this should either be the existing mean or the estimated mean.


```ts
class SingleShoe {
    readonly maker: string; // The make of the shoe
    readonly brand: string; // The brand of the shoe
    readonly year: number; // The year of the shoe
}
```



