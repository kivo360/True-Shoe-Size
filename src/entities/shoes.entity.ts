import { Entity, Column, PrimaryGeneratedColumn } from 'typeorm';

@Entity()
export class Shoe {
    @PrimaryGeneratedColumn()
    id: number;

    @Column("text")
    maker: string;

    @Column('text')
    brand: string;

    @Column('int')
    year: number;
}

@Entity()
export class ShoeRating {
    @PrimaryGeneratedColumn()
    id: number;

    @Column('int')
    userid: number;

    @Column("text")
    maker: string;

    @Column('text')
    brand: string;

    @Column('int')
    year: number;

    // @Column('decimal', { precision: 5, scale: 2 })
    @Column()
    shoeSize: number;
    
    @Column('int')
    shoeFit: number;

    @Column()
    isafter: boolean;
}


// readonly shoeSize: number;
    // readonly shoeFit: number;
    // readonly isafter: boolean;