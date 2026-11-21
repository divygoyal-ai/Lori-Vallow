import jwt from 'jsonwebtoken';
import bcrypt from 'bcryptjs';
import { OAuth2Client } from 'google-auth-library';
import { Router } from 'express';
import { q } from './db.js';

const secret = () => process.env.JWT_SECRET || 'dev-secret';
const google = new OAuth2Client(process.env.GOOGLE_CLIENT_ID);
export const sign = (u) => jwt.sign({ id: u.id, role: u.role }, secret(), { expiresIn: '7d' });
const pub = (u) => ({ id: u.id, email: u.email, name: u.name, avatar: u.avatar, role: u.role });

export function requireAuth(req, res, next) {
  const h = req.headers.authorization || '';
  try { req.user = jwt.verify(h.replace('Bearer ', ''), secret()); next(); }
  catch { res.status(401).json({ error: 'Login required' }); }
}
export const requireAdmin = [requireAuth, (req, res, next) =>
  req.user.role === 'admin' ? next() : res.status(403).json({ error: 'Admin only' })];

async function verifyCaptcha(token) {
  if (!token) return false;
  const r = await fetch('https://challenges.cloudflare.com/turnstile/v0/siteverify', {
    method: 'POST',
    body: new URLSearchParams({ secret: process.env.TURNSTILE_SECRET, response: token }),
  }).catch(() => null);
  return !!(r && (await r.json()).success);
}

export const authRouter = Router();

authRouter.post('/register', async (req, res) => {
  const { email, password, name, captcha } = req.body;
  if (!email || !password || password.length < 8 || !name) return res.status(400).json({ error: 'Name, email and 8+ char password required' });
  if (!(await verifyCaptcha(captcha))) return res.status(400).json({ error: 'Captcha failed' });
  try {
    const hash = await bcrypt.hash(password, 10);
    const { rows } = await q('insert into users (email,name,password_hash) values ($1,$2,$3) returning *', [email.toLowerCase(), name, hash]);
    res.json({ token: sign(rows[0]), user: pub(rows[0]) });
  } catch { res.status(409).json({ error: 'Email already registered' }); }
});

authRouter.post('/login', async (req, res) => {
  const { email, password, captcha } = req.body;
  if (!(await verifyCaptcha(captcha))) return res.status(400).json({ error: 'Captcha failed' });
  const { rows } = await q('select * from users where email=$1', [(email || '').toLowerCase()]);
  const u = rows[0];
  if (!u || !u.password_hash || !(await bcrypt.compare(password || '', u.password_hash))) return res.status(401).json({ error: 'Invalid credentials' });
  res.json({ token: sign(u), user: pub(u) });
});

authRouter.post('/google', async (req, res) => {
  try {
    const ticket = await google.verifyIdToken({ idToken: req.body.credential, audience: process.env.GOOGLE_CLIENT_ID });
    const p = ticket.getPayload();
    const { rows } = await q(
      `insert into users (email,name,google_id,avatar) values ($1,$2,$3,$4)
       on conflict (email) do update set google_id=excluded.google_id, avatar=excluded.avatar returning *`,
      [p.email.toLowerCase(), p.name, p.sub, p.picture]);
    res.json({ token: sign(rows[0]), user: pub(rows[0]) });
  } catch { res.status(401).json({ error: 'Google sign-in failed (is GOOGLE_CLIENT_ID set?)' }); }
});

authRouter.get('/me', requireAuth, async (req, res) => {
  const { rows } = await q('select * from users where id=$1', [req.user.id]);
  rows[0] ? res.json(pub(rows[0])) : res.status(404).json({ error: 'Not found' });
});
