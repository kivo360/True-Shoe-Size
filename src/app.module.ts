import { Module } from '@nestjs/common';
import { TypeOrmModule } from '@nestjs/typeorm';
import { Connection } from 'typeorm';
import { TrueModule } from './modules/true.module'

import { AppController } from './app.controller';
import { AppService } from './app.service';


// Environment Variables
const PORT:number = parseInt(process.env.DBPORT) || 5432;
const POSTGRESUSER:string = process.env.POSTUSER || "root";
const POSTGRESPASS:string = process.env.POSTPASS || "root";
const DATABASE:string = process.env.DATABASE || "db";

@Module({
  imports: [
    TypeOrmModule.forRoot({
    type: 'postgres',
    host: "localhost",
    port: PORT,
    username: POSTGRESUSER,
    password: POSTGRESPASS,
    database: DATABASE,
    entities: [__dirname + '/**/*.entity{.ts,.js}'],
    synchronize: true,
  }), TrueModule],
  controllers: [AppController],
  providers: [AppService],
})
export class AppModule {
  constructor(private readonly connection: Connection) { }
}
