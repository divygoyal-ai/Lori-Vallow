import pg from 'pg';
import 'dotenv/config';

export const pool = new pg.Pool({ connectionString: process.env.DATABASE_URL });
export const q = (text, params) => pool.query(text, params);

export async function migrate() {
  await q(`
  create table if not exists users (
    id serial primary key,
    email text unique not null,
    name text not null,
    password_hash text,
    google_id text unique,
    avatar text,
    role text not null default 'user',
    created_at timestamptz default now()
  );
  create table if not exists cars (
    id serial primary key,
    slug text unique not null,
    brand text not null,
    model text not null,
    year int not null,
    price numeric not null,
    category text not null,
    description text,
    model_url text,
    hero_image text,
    specs jsonb not null default '{}',
    colors jsonb not null default '[]',
    featured boolean default false,
    created_at timestamptz default now()
  );
  create table if not exists wishlist (
    user_id int references users(id) on delete cascade,
    car_id int references cars(id) on delete cascade,
    primary key (user_id, car_id)
  );
  create table if not exists auctions (
    id serial primary key,
    car_id int references cars(id) on delete cascade,
    starting_bid numeric not null,
    min_increment numeric not null default 1000,
    ends_at timestamptz not null,
    status text not null default 'live'
  );
  create table if not exists bids (
    id serial primary key,
    auction_id int references auctions(id) on delete cascade,
    user_id int references users(id) on delete cascade,
    amount numeric not null,
    created_at timestamptz default now()
  );
  create table if not exists celebrities (
    id serial primary key,
    name text not null,
    profession text,
    bio text,
    photo text,
    cars jsonb not null default '[]'
  );
  create table if not exists viewing_requests (
    id serial primary key,
    user_id int references users(id) on delete set null,
    car_id int references cars(id) on delete cascade,
    preferred_date date,
    note text,
    created_at timestamptz default now()
  );`);
}
