import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import CarViewer from '../components/CarViewer';
import CarCard from '../components/CarCard';
import { useFetch, useToast, useCountdown } from '../hooks';
import { money } from '../api';

function AuctionTile({ a }) {
  const { text } = useCountdown(a.ends_at);
  return (
    <Link to={`/auctions/${a.id}`} className="card" style={{ padding: 22, display: 'block' }}>
      <div className="eyebrow">Live now</div>
      <h3 style={{ fontSize: 26 }}>{a.brand} {a.model}</h3>
      <div className="big">{money(a.current_bid)}</div>
      <div className="mute">{a.bid_count} bids · ends in {text}</div>
    </Link>
  );
}

export default function Home() {
  const [cars] = useFetch('/cars');
  const [auctions] = useFetch('/auctions');
  const [toast, setToast] = useToast();
  const brands = cars ? [...new Set(cars.map((c) => c.brand))] : [];
  const word = (t, d = 0) => t.split(' ').map((w, i) => (
    <motion.span key={i} style={{ display: 'inline-block', marginRight: '.25em' }} initial={{ y: 60, opacity: 0 }} animate={{ y: 0, opacity: 1 }} transition={{ delay: d + i * 0.12, duration: 0.9, ease: [0.2, 0.8, 0.2, 1] }}>{w}</motion.span>
  ));
  return (
    <>
      <section className="hero">
        <CarViewer hero color="#b30000" />
        <div className="copy">
          <div className="eyebrow">The virtual showroom for collectors</div>
          <h1>{word('Own the', 0.2)}<br />{word('extraordinary', 0.5)}</h1>
          <p className="mute" style={{ margin: '20px 0 30px', maxWidth: 460 }}>Walk around, step inside and configure the world’s most coveted automobiles — then bid on them live.</p>
          <div className="row"><Link to="/showroom" className="btn solid">Enter showroom</Link><Link to="/auctions" className="btn">Live auctions</Link></div>
        </div>
      </section>

      <div className="marquee"><div>{[...brands, ...brands, ...brands, ...brands].map((b, i) => <span key={i} style={{ margin: '0 40px' }}>{b} <span className="gold">✦</span></span>)}</div></div>

      <section className="section wrap">
        <div className="eyebrow">Featured</div><h2 style={{ marginBottom: 40 }}>Curated this week</h2>
        <div className="grid">{cars?.filter((c) => c.featured).slice(0, 3).map((c, i) => <CarCard key={c.id} car={c} i={i} onToast={setToast} />)}</div>
      </section>

      {auctions?.length > 0 && (
        <section className="section wrap" style={{ paddingTop: 0 }}>
          <div className="eyebrow">Bidding</div><h2 style={{ marginBottom: 40 }}>Auctions closing soon</h2>
          <div className="grid">{auctions.map((a) => <AuctionTile key={a.id} a={a} />)}</div>
        </section>
      )}

      <section className="section wrap">
        <div className="split">
          <div><div className="eyebrow">Celebrity Garage</div><h2>What the icons drive</h2>
            <p className="mute" style={{ margin: '16px 0 28px' }}>Publicly documented cars owned by athletes, artists and collectors, each with its source.</p>
            <Link to="/celebrity-garage" className="btn">Explore garages</Link></div>
          <div className="panel"><div className="serif" style={{ fontSize: 28 }}>Compare any three cars</div><p className="mute" style={{ margin: '12px 0 20px' }}>Specs, colours and performance side by side.</p><Link to="/compare" className="btn sm">Open compare</Link></div>
        </div>
      </section>
      {toast && <div className="toast">{toast}</div>}
    </>
  );
}
