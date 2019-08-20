import { Injectable } from '@nestjs/common';
import { Shoe, ShoeRating } from '../entities/shoes.entity';
import { Repository } from 'typeorm';
import { InjectRepository } from '@nestjs/typeorm';
import { isNullOrUndefined } from 'util';
import { trainRegressor } from '../microservices/regression'

@Injectable()
export class TrueToSizeCalculation {

    constructor(
        @InjectRepository(Shoe)
        private readonly shoeRepository: Repository<Shoe>,
        @InjectRepository(ShoeRating)
        private readonly shoeRatingRepository: Repository<ShoeRating>,
    ) { }

    /**
     * Get the true to size calculation for the given model
     * returns: The latest calculation for the given shoe
     */
    getCalculation(maker: string, brand: string, year: number): number {
        // Check to see if the year is within the bounds of normal
        // This is a filtration check
        if (year < 1950 || year > new Date().getFullYear()) {
            throw new TypeError("The year is not within the correct range 1960 - 2019 (now)");
        }

        // Call to an outside service to get the general calculation

        return 0;
    }


    async createShoe(maker:string, brand:string, year:number) {
        if (year < 1960 && year > new Date().getFullYear()) {
            throw new TypeError("The year is not within the correct range 1960 - 2019 (now)");
        }

        const insertedData = {
            maker: maker,
            brand: brand,
            year: year
        }
        await this.shoeRepository
            .findOne(insertedData)
            .then(res=>{
                console.log(res);
                if(res === undefined){
                    return this.shoeRepository.insert(insertedData);
                }    
                return
                
                
            })
            .then(res => {
               if ((res == undefined)) {
                    insertedData['message'] = "The shoe already exist";
                    insertedData['status'] = 202
                }else{
                    insertedData['message'] = "Yay!!! We were able to create a new record inside of the database.";
                    insertedData['status'] = 200
                }
            }) 
            .catch((reason)=>{
                insertedData['message'] = "There was an error on our end!!!";
                insertedData['reason'] = reason;
                insertedData['status'] = 500;
            })
        return {
            ...insertedData
        }
        
        // Create a string placeholder
        // Allow any brand to exist
    }



    /**
     * Checks to see if a shoe exist, then adds a rating if the shoe exist 
     * @param userid 
     * @param maker 
     * @param brand 
     * @param year 
     * @param shoeSize 
     * @param shoeFit 
     * @param isAfter 
     */
    async createShoeRating(userid:number, maker: string, brand: string, year: number, shoeSize: number, shoeFit: number, isAfter: boolean) {
        if (year < 1950 || year > new Date().getFullYear()) {
            throw new TypeError("The year is not within the correct range 1960 - 2019 (now)");
        }

        const insertedData = {
            userid: userid,
            maker: maker,
            brand: brand,
            year: year,
            shoeSize: shoeSize,
            shoeFit: shoeFit,
            isafter: isAfter
        }

        const shoeCheck = {
            maker: maker,
            brand: brand,
            year: year
        }


        await this.shoeRepository
            .findOne(shoeCheck)
            .then(res => {
                if (res !== undefined) {
                    return this.shoeRatingRepository.findOne({...shoeCheck, userid: userid})
                }
                throw new Error("The shoe doesn't exist")
            })
            .then(res => {
                console.log(res);
                if (res === undefined) {
                    return this.shoeRatingRepository.insert(insertedData);
                }
                return
            })
            .then(res => {
                if ((res == undefined)) {
                    insertedData['message'] = "The shoe rating already exist with that shoe and user";
                    insertedData['status'] = 202
                } else {
                    insertedData['message'] = "We were able to create a new record inside of the database.";
                    insertedData['status'] = 200
                }
            })
            .catch((reason) => {
                if("The shoe doesn't exist" == reason.message){
                    insertedData['status'] = 400;
                    insertedData['message'] = "You gave us the wrong input";
                }else{
                    insertedData['status'] = 500;
                    insertedData['message'] = "There was an error on our end!!!";
                }
                
                insertedData['reason'] = reason.message;
            })
        

        const sums = await this.shoeRatingRepository
            .createQueryBuilder("ShoeRating")
            .select("AVG(ShoeRating.shoeFit)", "truesize")
            .where("ShoeRating.maker = :maker", { maker: maker })
            .andWhere("ShoeRating.brand = :brand", { brand: brand })
            .andWhere("ShoeRating.year = :year", { year: year })
            .getRawOne();
        
        const trainObj = {}
        trainObj['make'] = maker;
        trainObj['year'] = year;
        trainObj['trueSize'] = sums["truesize"];
        
        const callObj = {
            train: [trainObj],
            pred: []
        }

        try {
            trainRegressor(callObj).then(res=>{
                console.log(res.data);
                console.log(res.status);
                console.log(res.statusText);
                console.log(res.headers);
                console.log(res.config);

            
            }).catch((reason)=>{
                if (reason.response){
                    console.log(reason.response.data);
                    console.log(reason.response.status);
                    console.log(reason.response.headers);
                }
            });
        } catch (error) {
            console.log(error);
        }
        // Send call to micro-service regarding what the sum should be
        // Send the call to another 
        
        return insertedData;
    }



    /**
     * This gets the true shoe size. We also reach out to the other micro-service here. 
     * That microservice interacts with the machine learning algorithm.
     * @param make 
     * @param brand 
     * @param year 
     */
    async getTrueShoeSize(make:string, brand:string, year:number){
        
        const responseData: {[key: string]: any}= {}

        const sums = await this.shoeRatingRepository
            .createQueryBuilder("ShoeRating")
            .select("AVG(ShoeRating.shoeFit)", "truesize")
            .where("ShoeRating.maker = :maker", {maker: make})
            .andWhere("ShoeRating.brand = :brand", { brand: brand })
            .andWhere("ShoeRating.year = :year", { year: year })
            .getRawOne();
        
        if (!isNullOrUndefined(sums)){
            responseData['message'] = `Successfully retrived the truesize for the shoe ${brand} made by ${make} in the year ${year}`
            responseData['data'] = sums
        }else{
            // Search the micro-service to find if you can get an estimate.
            responseData['message'] = `We weren't able to find the truesize of the shoe ${brand} made by ${make} in the year ${year}`
            responseData['data'] = {}
        }

        return responseData;
    }

}