# MAISON·AUTO — Luxury Virtual Car Showroom

React (Vite) + three.js front end, Node/Express + PostgreSQL + Socket.IO back end.

## Features (vertical slice)
- Cinematic 3D homepage, smooth scroll, custom cursor, animated reveals
- 3D car viewer: orbit 360°, interior view, live colour swap, doors and lights toggles
- Showroom with search, filters and sorting
- Side-by-side comparison (up to 3 cars, per-car colours, best-value highlighting)
- Wishlist (per user, synced to the database)
- Live auctions: real-time bids over WebSockets, countdown, anti-sniping extension
- Celebrity Garage with a source link for every claim
- Auth: email/password (bcrypt + JWT), Google Sign-In, Cloudflare Turnstile captcha, rate limiting
- Admin panel: stats, add/delete cars, start auctions, view users and viewing requests
- AI concierge chatbot (Claude API, optional)

## Run locally
```bash
# 1. PostgreSQL: create a database and user (see server/.env.example for the URL)
createdb showroom

# 2. API
cd server && cp .env.example .env && npm install && npm run seed && npm run dev

# 3. Web app
cd client && cp .env.example .env && npm install && npm run dev   # http://localhost:5173
```
Seeded admin: `admin@showroom.test` / `admin1234` (change it before any deployment).

## Configuration
| Variable | Where | Purpose |
|---|---|---|
| `GOOGLE_CLIENT_ID` / `VITE_GOOGLE_CLIENT_ID` | server / client | Enables Google Sign-In |
| `TURNSTILE_SECRET` / `VITE_TURNSTILE_SITEKEY` | server / client | Captcha (defaults are Cloudflare's public test keys) |
| `ANTHROPIC_API_KEY` | server | Enables the concierge chatbot |
| `JWT_SECRET` | server | Set a long random value in production |

## 3D models
The car viewer uses a stylised procedural placeholder. For real cars, add a `.glb` URL per car
(Admin → Add car, or the `model_url` column). Materials named like `body`/`paint` get recoloured.
Check each model's licence on Sketchfab and show its attribution.

## Roadmap
Price-drop alerts, auto-bid, Stripe deposits, AR view, financing calculator, image uploads, email notifications.
