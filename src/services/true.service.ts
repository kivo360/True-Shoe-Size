import { Injectable } from '@nestjs/common';
import { Shoe, ShoeRating } from '../entities/shoes.entity';
import { Repository } from 'typeorm';
import { InjectRepository } from '@nestjs/typeorm';
import { isNullOrUndefined } from 'util';
import { trainRegressor, scoreRegressor, predictRegressor } from '../microservices/regression'
import { Logger } from '@nestjs/common';

@Injectable()
export class TrueToSizeCalculation {
    private readonly logger = new Logger(TrueToSizeCalculation.name);

    constructor(
        @InjectRepository(Shoe)
        private readonly shoeRepository: Repository<Shoe>,
        @InjectRepository(ShoeRating)
        private readonly shoeRatingRepository: Repository<ShoeRating>,
    ) { }


    async getScore(){
        let sums = await this.shoeRatingRepository
            .createQueryBuilder("ShoeRating")
            .select("maker, year, AVG(ShoeRating.shoeFit)", "trueSize")
            .groupBy("ShoeRating.maker")
            .addGroupBy("ShoeRating.year")
            .getRawMany();
        

        sums = sums.map(function(element){
            element["trueSize"] = parseFloat(element["trueSize"])
            return element;
        })

        const callObj = {
            train: sums,
            pred: []
        }

        scoreRegressor(callObj, (err, result) => {
            if (err){
                if (err.response) {
                    this.logger.error(err.response.data['detail']);
                }
            }
        })
        return sums;
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
                this.logger.error(reason.message);
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
            }).catch((reason)=>{
                if (reason.response){
                    this.logger.error(reason.response.message)
                }
            });
        } catch (error) {
            // console.log(error);
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
            

        if (!isNullOrUndefined(sums['truesize'])){
            responseData['message'] = `Successfully retrived the truesize for the shoe ${brand} made by ${make} in the year ${year}`
            responseData['data'] = sums
        }else{
            // Search the micro-service to find if you can get an estimate.
            // check for a prediction
            await predictRegressor({
                make: make, 
                year: year
            }).then(res => {
                responseData['message'] = `We were able to estimate the number of responses`
                responseData['data'] = res.data.data.data;
            }).catch((reason) => {
                if (reason.response) {
                    responseData['message'] = `We weren't able to find the truesize of the shoe ${brand} made by ${make} in the year ${year}`
                    this.logger.error("Remember to place stuff here");
                }
            });
        }

        return responseData;
    }

}