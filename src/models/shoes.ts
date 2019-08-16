import { NumericLiteral } from "@babel/types";

export class CreateShoe {
    readonly maker: string;
    readonly brand: string;
    readonly year: number;
}


/**
 * 
 */
export class ShoeRating {
    readonly userid: number;
    readonly maker: string;
    readonly brand: string;
    readonly year: number;
    readonly shoeSize: number;
    readonly shoeFit: number;
    readonly isafter: boolean;
}

/**
 *  When searching for shoes, it's possible to get the shoes by any one of the available fields. 
 *  Will check in controller to see if all of them are undefined
 */
export class ShoeSearch {
    readonly maker?: string | undefined;
    readonly brand?: string | undefined;
    readonly year?: string | undefined;
}