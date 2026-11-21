import { useEffect, useState } from 'react';
import { Link, useParams } from 'react-router-dom';
import { useFetch, useCountdown, useToast } from '../hooks';
import { api, socket, token, money } from '../api';
import { useStore } from '../store';

function Tile({ a }) {
  const { text } = useCountdown(a.ends_at);
  return (
    <Link to={`/auctions/${a.id}`} className="card" style={{ padding: 28, display: 'block' }}>
      <div className="eyebrow">{a.year}</div><h3 style={{ fontSize: 30 }}>{a.brand} {a.model}</h3>
      <div className="big">{money(a.current_bid)}</div><div className="mute">{a.bid_count} bids · {text}</div>
    </Link>
  );
}
export function Auctions() {
  const [list] = useFetch('/auctions');
  return (
    <div className="page wrap">
      <div className="eyebrow">Live</div><h1 style={{ fontSize: 'clamp(2.4rem,5vw,4rem)', marginBottom: 30 }}>Auctions</h1>
      <div className="grid">{list?.map((a) => <Tile key={a.id} a={a} />)}</div>
      {list?.length === 0 && <p className="mute">No live auctions right now.</p>}
    </div>
  );
}

export function AuctionRoom() {
  const { id } = useParams();
  const [a, err, setA] = useFetch('/auctions/' + id);
  const [amount, setAmount] = useState('');
  const [toast, setToast] = useToast();
  const user = useStore((s) => s.user);
  const { text, ms } = useCountdown(a?.ends_at);

  useEffect(() => {
    socket.emit('join', id);
    const onBid = (b) => b.auctionId == id && setA((prev) => prev && ({
      ...prev, current_bid: b.amount, ends_at: b.endsAt, bid_count: prev.bid_count + 1,
      bids: [{ amount: b.amount, name: b.name, created_at: b.at }, ...prev.bids].slice(0, 20),
    }));
    socket.on('bid', onBid);
    return () => socket.off('bid', onBid);
  }, [id, setA]);

  if (err) return <div className="page wrap">Auction not found.</div>;
  if (!a) return <div className="page wrap mute">Loading…</div>;
  const min = Number(a.current_bid) + (a.bid_count ? Number(a.min_increment) : 0);

  function bid(value) {
    if (!user) return setToast('Sign in to bid');
    socket.emit('bid', { auctionId: a.id, amount: value, token: token() }, (r) => setToast(r.ok ? 'Bid placed' : r.error));
  }
  return (
    <div className="page wrap">
      <Link to="/auctions" className="mute">← All auctions</Link>
      <div className="split" style={{ marginTop: 20 }}>
        <div><div className="eyebrow">{a.year} · Lot #{a.id}</div><h1 style={{ fontSize: 60 }}>{a.brand}<br />{a.model}</h1>
          <Link to={`/car/${a.slug}`} className="btn" style={{ marginTop: 24 }}>View in 3D</Link></div>
        <div className="panel">
          <div className="mute" style={{ fontSize: 12, letterSpacing: '.2em' }}>CURRENT BID</div>
          <div className="big" style={{ fontSize: 56 }}>{money(a.current_bid)}</div>
          <div className="row" style={{ justifyContent: 'space-between', margin: '8px 0 22px' }}>
            <span className="mute">{a.bid_count} bids</span><span className={ms < 120e3 ? '' : 'gold'} style={{ color: ms < 120e3 && ms ? 'var(--red)' : undefined }}>{text}</span>
          </div>
          {ms > 0 && <>
            <div className="row"><input type="number" placeholder={`Min ${min}`} value={amount} onChange={(e) => setAmount(e.target.value)} style={{ flex: 1 }} />
              <button className="btn solid" onClick={() => bid(Number(amount))}>Bid</button></div>
            <button className="btn sm" style={{ marginTop: 10 }} onClick={() => bid(min)}>Quick bid {money(min)}</button>
            <p className="mute" style={{ fontSize: 11, marginTop: 10 }}>Bids in the final 2 minutes extend the auction by 2 minutes.</p>
          </>}
          <div className="bidlist" style={{ marginTop: 22 }}>{a.bids.map((b, i) => <div key={i}><span>{b.name}</span><span className={i === 0 ? 'gold' : ''}>{money(b.amount)}</span></div>)}</div>
        </div>
      </div>
      {toast && <div className="toast">{toast}</div>}
    </div>
  );
}
