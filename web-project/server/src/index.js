import 'dotenv/config';
import express from 'express';
import cors from 'cors';
import helmet from 'helmet';
import rateLimit from 'express-rate-limit';
import http from 'http';
import { Server } from 'socket.io';
import jwt from 'jsonwebtoken';
import { q, migrate } from './db.js';
import { authRouter, requireAuth, requireAdmin } from './auth.js';

const origin = process.env.CLIENT_ORIGIN || 'http://localhost:5173';
const app = express();
const server = http.createServer(app);
const io = new Server(server, { cors: { origin } });

app.use(helmet());
app.use(cors({ origin }));
app.use(express.json({ limit: '1mb' }));
app.use('/api/auth', rateLimit({ windowMs: 15 * 60e3, limit: 50 }), authRouter);

const ah = (fn) => (req, res, next) => fn(req, res, next).catch(next);

// ---- Cars ----
app.get('/api/cars', ah(async (req, res) => {
  const { brand, category, search, sort } = req.query;
  const where = [], p = [];
  if (brand) { p.push(brand); where.push(`brand = $${p.length}`); }
  if (category) { p.push(category); where.push(`category = $${p.length}`); }
  if (search) { p.push(`%${search}%`); where.push(`(brand ilike $${p.length} or model ilike $${p.length})`); }
  const order = { price_asc: 'price asc', price_desc: 'price desc', power: "(specs->>'power_hp')::int desc" }[sort] || 'featured desc, id';
  const { rows } = await q(`select * from cars ${where.length ? 'where ' + where.join(' and ') : ''} order by ${order}`, p);
  res.json(rows);
}));
app.get('/api/cars/:slug', ah(async (req, res) => {
  const { rows } = await q('select * from cars where slug=$1', [req.params.slug]);
  rows[0] ? res.json(rows[0]) : res.status(404).json({ error: 'Not found' });
}));

// ---- Wishlist ----
app.get('/api/wishlist', requireAuth, ah(async (req, res) => {
  const { rows } = await q('select c.* from wishlist w join cars c on c.id=w.car_id where w.user_id=$1', [req.user.id]);
  res.json(rows);
}));
app.post('/api/wishlist/:carId', requireAuth, ah(async (req, res) => {
  await q('insert into wishlist values ($1,$2) on conflict do nothing', [req.user.id, req.params.carId]);
  res.json({ ok: true });
}));
app.delete('/api/wishlist/:carId', requireAuth, ah(async (req, res) => {
  await q('delete from wishlist where user_id=$1 and car_id=$2', [req.user.id, req.params.carId]);
  res.json({ ok: true });
}));

// ---- Celebrities ----
app.get('/api/celebrities', ah(async (_req, res) => res.json((await q('select * from celebrities order by id')).rows)));

// ---- Viewings ----
app.post('/api/viewings', requireAuth, ah(async (req, res) => {
  const { carId, date, note } = req.body;
  await q('insert into viewing_requests (user_id,car_id,preferred_date,note) values ($1,$2,$3,$4)', [req.user.id, carId, date, note]);
  res.json({ ok: true });
}));

// ---- Auctions ----
const auctionSql = `
  select a.*, c.slug, c.brand, c.model, c.year, c.colors, c.model_url,
    coalesce((select max(amount) from bids where auction_id=a.id), a.starting_bid) as current_bid,
    (select count(*) from bids where auction_id=a.id)::int as bid_count
  from auctions a join cars c on c.id=a.car_id`;
app.get('/api/auctions', ah(async (_req, res) => res.json((await q(`${auctionSql} where a.status='live' order by a.ends_at`)).rows)));
app.get('/api/auctions/:id', ah(async (req, res) => {
  const { rows } = await q(`${auctionSql} where a.id=$1`, [req.params.id]);
  if (!rows[0]) return res.status(404).json({ error: 'Not found' });
  const bids = (await q(`select b.amount, b.created_at, u.name from bids b join users u on u.id=b.user_id where auction_id=$1 order by amount desc limit 20`, [req.params.id])).rows;
  res.json({ ...rows[0], bids });
}));

io.on('connection', (socket) => {
  socket.on('join', (id) => socket.join(`auction:${id}`));
  socket.on('bid', async ({ auctionId, amount, token }, ack) => {
    try {
      const user = jwt.verify(token, process.env.JWT_SECRET || 'dev-secret');
      const { rows } = await q(`${auctionSql} where a.id=$1`, [auctionId]);
      const a = rows[0];
      if (!a || a.status !== 'live' || new Date(a.ends_at) < new Date()) throw new Error('Auction closed');
      const min = Number(a.current_bid) + Number(a.min_increment) * (a.bid_count ? 1 : 0);
      if (Number(amount) < min) throw new Error(`Minimum bid is $${min.toLocaleString()}`);
      await q('insert into bids (auction_id,user_id,amount) values ($1,$2,$3)', [auctionId, user.id, amount]);
      // anti-sniping: extend by 2 minutes if bid lands in the final 2 minutes
      let endsAt = new Date(a.ends_at);
      if (endsAt - Date.now() < 120e3) {
        endsAt = new Date(Date.now() + 120e3);
        await q('update auctions set ends_at=$1 where id=$2', [endsAt, auctionId]);
      }
      const name = (await q('select name from users where id=$1', [user.id])).rows[0].name;
      io.to(`auction:${auctionId}`).emit('bid', { auctionId, amount: Number(amount), name, endsAt, at: new Date() });
      ack?.({ ok: true });
    } catch (e) { ack?.({ ok: false, error: e.name === 'JsonWebTokenError' || e.name === 'TokenExpiredError' ? 'Please sign in to bid' : e.message }); }
  });
});

// ---- Admin ----
app.get('/api/admin/stats', requireAdmin, ah(async (_req, res) => {
  const one = async (sql) => Number((await q(sql)).rows[0].n);
  res.json({
    users: await one('select count(*) n from users'),
    cars: await one('select count(*) n from cars'),
    liveAuctions: await one("select count(*) n from auctions where status='live'"),
    bids: await one('select count(*) n from bids'),
    viewings: await one('select count(*) n from viewing_requests'),
    topWishlisted: (await q('select c.brand, c.model, count(*)::int n from wishlist w join cars c on c.id=w.car_id group by c.id order by n desc limit 5')).rows,
  });
}));
const carFields = ['slug', 'brand', 'model', 'year', 'price', 'category', 'description', 'model_url', 'hero_image', 'specs', 'colors', 'featured'];
const j = (k, v) => (k === 'specs' || k === 'colors' ? JSON.stringify(v) : v);
app.post('/api/admin/cars', requireAdmin, ah(async (req, res) => {
  const vals = carFields.map((k) => j(k, req.body[k] ?? (k === 'specs' ? {} : k === 'colors' ? [] : null)));
  const { rows } = await q(`insert into cars (${carFields}) values (${carFields.map((_, i) => '$' + (i + 1))}) returning *`, vals);
  res.json(rows[0]);
}));
app.put('/api/admin/cars/:id', requireAdmin, ah(async (req, res) => {
  const ks = carFields.filter((k) => k in req.body);
  if (!ks.length) return res.status(400).json({ error: 'No fields' });
  const { rows } = await q(`update cars set ${ks.map((k, i) => `${k}=$${i + 1}`)} where id=$${ks.length + 1} returning *`, [...ks.map((k) => j(k, req.body[k])), req.params.id]);
  res.json(rows[0]);
}));
app.delete('/api/admin/cars/:id', requireAdmin, ah(async (req, res) => { await q('delete from cars where id=$1', [req.params.id]); res.json({ ok: true }); }));
app.post('/api/admin/auctions', requireAdmin, ah(async (req, res) => {
  const { carId, startingBid, minIncrement = 1000, endsAt } = req.body;
  res.json((await q('insert into auctions (car_id,starting_bid,min_increment,ends_at) values ($1,$2,$3,$4) returning *', [carId, startingBid, minIncrement, endsAt])).rows[0]);
}));
app.get('/api/admin/users', requireAdmin, ah(async (_req, res) => res.json((await q('select id,email,name,role,created_at from users order by id')).rows)));
app.get('/api/admin/viewings', requireAdmin, ah(async (_req, res) =>
  res.json((await q('select v.*, u.email, c.brand, c.model from viewing_requests v left join users u on u.id=v.user_id join cars c on c.id=v.car_id order by v.id desc')).rows)));
app.post('/api/admin/celebrities', requireAdmin, ah(async (req, res) => {
  const { name, profession, bio, photo, cars = [] } = req.body;
  res.json((await q('insert into celebrities (name,profession,bio,photo,cars) values ($1,$2,$3,$4,$5) returning *', [name, profession, bio, photo, JSON.stringify(cars)])).rows[0]);
}));

// ---- AI concierge (optional) ----
app.post('/api/concierge', rateLimit({ windowMs: 60e3, limit: 15 }), ah(async (req, res) => {
  const key = process.env.ANTHROPIC_API_KEY;
  const cars = (await q('select brand,model,year,price,category,specs from cars')).rows;
  if (!key) return res.json({ reply: 'The concierge is offline: set ANTHROPIC_API_KEY on the server to enable it.' });
  const r = await fetch('https://api.anthropic.com/v1/messages', {
    method: 'POST',
    headers: { 'x-api-key': key, 'anthropic-version': '2023-06-01', 'content-type': 'application/json' },
    body: JSON.stringify({
      model: 'claude-haiku-5-5', max_tokens: 500,
      system: `You are the concierge of a luxury car showroom. Be concise and elegant. Only recommend cars from this inventory: ${JSON.stringify(cars)}`,
      messages: (req.body.messages || []).slice(-10),
    }),
  });
  const data = await r.json();
  res.json({ reply: data.content?.[0]?.text || 'Sorry, I could not answer that.' });
}));

app.use((err, _req, res, _next) => { console.error(err); res.status(500).json({ error: 'Server error' }); });

// close expired auctions every 30s
setInterval(() => q("update auctions set status='ended' where status='live' and ends_at < now()").catch(() => {}), 30e3);

await migrate();
server.listen(process.env.PORT || 4000, () => console.log('API on :' + (process.env.PORT || 4000)));
