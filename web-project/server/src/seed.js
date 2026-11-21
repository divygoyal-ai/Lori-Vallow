import { q, migrate, pool } from './db.js';
import bcrypt from 'bcryptjs';

const colors = (list) => list.map(([name, hex]) => ({ name, hex }));
const cars = [
  ['ferrari-sf90', 'Ferrari', 'SF90 Stradale', 2024, 524000, 'Hypercar', 'Plug-in hybrid V8 with 986 hp, the most powerful road-going Ferrari series-production car of its time.',
   { engine: '4.0L twin-turbo V8 + 3 e-motors', power_hp: 986, torque_nm: 800, zero_to_100: 2.5, top_speed_kmh: 340, drivetrain: 'AWD', weight_kg: 1570 },
   colors([['Rosso Corsa', '#b30000'], ['Giallo Modena', '#e8b400'], ['Nero Daytona', '#15151a'], ['Bianco Avus', '#f2f2ee']]), true],
  ['lamborghini-revuelto', 'Lamborghini', 'Revuelto', 2024, 608000, 'Hypercar', 'The first V12 plug-in hybrid HPEV from Sant’Agata, with 1,001 hp.',
   { engine: '6.5L V12 + 3 e-motors', power_hp: 1001, torque_nm: 725, zero_to_100: 2.5, top_speed_kmh: 350, drivetrain: 'AWD', weight_kg: 1772 },
   colors([['Verde Mantis', '#4d9a1f'], ['Arancio Xanto', '#ff6a00'], ['Blu Nethuns', '#143a8c'], ['Grigio Titans', '#6b6e73']]), true],
  ['mclaren-750s', 'McLaren', '750S', 2024, 324000, 'Supercar', 'Lightweight carbon-tub supercar with 750 PS and razor-sharp handling.',
   { engine: '4.0L twin-turbo V8', power_hp: 740, torque_nm: 800, zero_to_100: 2.8, top_speed_kmh: 332, drivetrain: 'RWD', weight_kg: 1389 },
   colors([['Papaya Spark', '#ff7a00'], ['Volcano Grey', '#4a4d52'], ['Burton Blue', '#1c3f94']]), true],
  ['porsche-911-gt3rs', 'Porsche', '911 GT3 RS', 2024, 241000, 'Sports', 'Track-focused 911 with active aero and a 9,000 rpm flat-six.',
   { engine: '4.0L flat-six NA', power_hp: 518, torque_nm: 465, zero_to_100: 3.2, top_speed_kmh: 296, drivetrain: 'RWD', weight_kg: 1450 },
   colors([['Shark Blue', '#2a7fa8'], ['Guards Red', '#c4161c'], ['White', '#f4f4f2'], ['Python Green', '#6fa33a']]), false],
  ['rolls-royce-spectre', 'Rolls-Royce', 'Spectre', 2024, 420000, 'Luxury', 'The first fully electric Rolls-Royce: silent, effortless, bespoke.',
   { engine: 'Dual e-motors', power_hp: 577, torque_nm: 900, zero_to_100: 4.5, top_speed_kmh: 250, drivetrain: 'AWD', weight_kg: 2975 },
   colors([['Arctic White', '#f5f5f3'], ['Black Diamond', '#0b0b0d'], ['Midnight Sapphire', '#13204a']]), true],
  ['bentley-continental-gt', 'Bentley', 'Continental GT Speed', 2024, 285000, 'Grand Tourer', 'Hand-built grand tourer with a 782 hp plug-in hybrid V8.',
   { engine: '4.0L V8 PHEV', power_hp: 782, torque_nm: 1000, zero_to_100: 3.2, top_speed_kmh: 335, drivetrain: 'AWD', weight_kg: 2410 },
   colors([['Beluga', '#0e0e10'], ['Moonbeam', '#d9d6cf'], ['British Racing Green', '#0f3b2a']]), false],
  ['aston-martin-valhalla', 'Aston Martin', 'Valhalla', 2025, 800000, 'Hypercar', 'Mid-engined hybrid hypercar with 998 hp and F1-derived aero.',
   { engine: '4.0L V8 + e-motors', power_hp: 998, torque_nm: 1000, zero_to_100: 2.5, top_speed_kmh: 350, drivetrain: 'AWD', weight_kg: 1550 },
   colors([['Quantum Silver', '#b9bcc2'], ['Lime Essence', '#a7d211'], ['Onyx Black', '#101012']]), false],
];

const celebs = [
  ['Jay Leno', 'TV host & collector', 'Owns one of the world’s most famous car collections, documented on Jay Leno’s Garage.',
   [{ car: 'McLaren F1', note: 'Publicly shown on Jay Leno’s Garage', source: 'https://www.jaylenosgarage.com' }]],
  ['Cristiano Ronaldo', 'Footballer', 'Frequently photographed with supercars; his collection has been widely reported.',
   [{ car: 'Bugatti Veyron', note: 'Widely reported in press', source: 'https://en.wikipedia.org/wiki/Cristiano_Ronaldo' }]],
  ['Lewis Hamilton', 'F1 driver', 'Seven-time F1 champion with a well-documented taste for rare Ferraris and Mercedes.',
   [{ car: 'Ferrari LaFerrari', note: 'Publicly reported', source: 'https://en.wikipedia.org/wiki/Lewis_Hamilton' }]],
];

await migrate();
await q('truncate bids, auctions, wishlist, viewing_requests, cars, celebrities restart identity cascade');
for (const [slug, brand, model, year, price, category, description, specs, cols, featured] of cars) {
  await q(`insert into cars (slug,brand,model,year,price,category,description,specs,colors,featured) values ($1,$2,$3,$4,$5,$6,$7,$8,$9,$10)`,
    [slug, brand, model, year, price, category, description, specs, JSON.stringify(cols), featured]);
}
for (const [name, profession, bio, c] of celebs)
  await q('insert into celebrities (name,profession,bio,cars) values ($1,$2,$3,$4)', [name, profession, bio, JSON.stringify(c)]);

const hash = await bcrypt.hash('admin1234', 10);
await q(`insert into users (email,name,password_hash,role) values ('admin@showroom.test','Admin',$1,'admin') on conflict (email) do nothing`, [hash]);

// live auctions on a few cars
const now = Date.now();
for (const [carId, startBid, hours] of [[1, 450000, 6], [3, 280000, 30], [7, 700000, 72]])
  await q(`insert into auctions (car_id, starting_bid, min_increment, ends_at) values ($1,$2,5000,$3)`, [carId, startBid, new Date(now + hours * 3600e3)]);

console.log('Seeded. Admin: admin@showroom.test / admin1234');
await pool.end();
