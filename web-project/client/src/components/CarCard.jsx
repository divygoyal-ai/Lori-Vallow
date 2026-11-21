import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import { useStore } from '../store';
import { money } from '../api';

export default function CarCard({ car, i = 0, onToast }) {
  const { wishlist, toggleWish, compare, toggleCompare, user } = useStore();
  const on = wishlist.includes(car.id);
  const c0 = car.colors?.[0]?.hex || '#888';
  return (
    <motion.div className="card" initial={{ opacity: 0, y: 30 }} whileInView={{ opacity: 1, y: 0 }} viewport={{ once: true }} transition={{ delay: (i % 3) * 0.08 }}>
      <Link to={`/car/${car.slug}`}>
        <div className="thumb" style={{ background: `radial-gradient(circle at 50% 75%, ${c0}55, #0b0b0d 70%)` }}>
          <div className="serif" style={{ position: 'absolute', inset: 0, display: 'grid', placeItems: 'center', fontSize: 64, color: '#ffffff12', letterSpacing: '.1em' }}>{car.brand.toUpperCase()}</div>
          <span className="chip" style={{ position: 'absolute', top: 14, left: 14 }}>{car.category}</span>
        </div>
        <div className="body">
          <div className="mute" style={{ fontSize: 12, letterSpacing: '.2em' }}>{car.brand.toUpperCase()} · {car.year}</div>
          <h3 style={{ fontSize: 28 }}>{car.model}</h3>
          <div className="row" style={{ justifyContent: 'space-between', marginTop: 10 }}>
            <span className="gold">{money(car.price)}</span>
            <span className="mute" style={{ fontSize: 12 }}>{car.specs.power_hp} hp · {car.specs.zero_to_100}s</span>
          </div>
        </div>
      </Link>
      <div className="row" style={{ padding: '0 22px 20px' }}>
        <button className={'icon' + (on ? ' on' : '')} title="Wishlist" onClick={async () => { if (!user) return onToast?.('Sign in to save cars'); await toggleWish(car.id); }}>{on ? '♥' : '♡'}</button>
        <button className={'icon' + (compare.includes(car.slug) ? ' on' : '')} title="Compare" onClick={() => toggleCompare(car.slug)}>⇄</button>
        <div className="row" style={{ marginLeft: 'auto', gap: 6 }}>{car.colors.slice(0, 4).map((c) => <span key={c.name} title={c.name} style={{ width: 12, height: 12, borderRadius: '50%', background: c.hex, border: '1px solid #444' }} />)}</div>
      </div>
    </motion.div>
  );
}
