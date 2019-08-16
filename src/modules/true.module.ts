// import { Photo } from './photo.entity';

import { Module } from '@nestjs/common';
import { TypeOrmModule } from '@nestjs/typeorm';

import { TrueController } from '../controllers/true.controller';
import { TrueToSizeCalculation } from '../services/true.service';
import { Shoe, ShoeRating } from '../entities/shoes.entity';

@Module({
    imports: [TypeOrmModule.forFeature([Shoe, ShoeRating])],
    providers: [TrueToSizeCalculation],
    controllers: [TrueController],
})
export class TrueModule { }