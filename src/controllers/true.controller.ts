
import { Controller, Post, Get, Req, Body } from '@nestjs/common';
import { Request } from 'express';
import { TrueToSizeCalculation } from '../services/true.service';
import { CreateShoe, ShoeRating, ShoeSearch } from "./../models/shoes";

@Controller('true')
export class TrueController {
    
    constructor(private readonly trueService: TrueToSizeCalculation) { }


    /**
     * Creates a new shoe inside of the database.
     * @param request 
     * @param addedShoe 
     */
    @Post("add")
    addNewShoe(@Req() request: Request, @Body() addedShoe: CreateShoe): {[key: string]: any} {
        return this.trueService.createShoe(addedShoe.maker, addedShoe.brand, addedShoe.year);
    }

    /**
     * Adds a calculation to the database for a given user.
     * We might want to have the user's information because it gives a solid understanding of how our user overshoots (great for machine learning)
     * @param request 
     * @param mysize 
     */
    @Post("addsize")
    addNewCalculation(@Req() request: Request, @Body() mysize: ShoeRating): {[key: string]: any} {
        return this.trueService.createShoeRating(mysize.userid, mysize.maker, mysize.brand, mysize.year, mysize.shoeSize, mysize.shoeFit, mysize.isafter);
    }

    
    /**
     * 
     * @param request 
     * @param singleShoe 
     */
    @Get("single")
    findSingleTrueCalaculation(@Req() request: Request, @Body() singleShoe: CreateShoe): { [key: string]: any } {
        return this.trueService.getTrueShoeSize(singleShoe.maker, singleShoe.brand, singleShoe.year);
    }

    
}