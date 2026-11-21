import { motion } from 'framer-motion';
import { useFetch } from '../hooks';

export default function Celebrities() {
  const [list] = useFetch('/celebrities');
  return (
    <div className="page wrap">
      <div className="eyebrow">Celebrity Garage</div><h1 style={{ fontSize: 'clamp(2.4rem,5vw,4rem)' }}>Icons & their cars</h1>
      <p className="mute" style={{ margin: '12px 0 40px', maxWidth: 560 }}>Only publicly documented ownership is listed, each with a source link.</p>
      <div className="grid">{list?.map((p, i) => (
        <motion.div key={p.id} className="card" style={{ padding: 28 }} initial={{ opacity: 0, y: 30 }} whileInView={{ opacity: 1, y: 0 }} viewport={{ once: true }} transition={{ delay: i * 0.08 }}>
          <div className="eyebrow">{p.profession}</div><h3 style={{ fontSize: 32 }}>{p.name}</h3>
          <p className="mute" style={{ margin: '10px 0 18px' }}>{p.bio}</p>
          {p.cars.map((c) => <div key={c.car} style={{ borderTop: '1px solid var(--line)', padding: '12px 0' }}>
            <div className="gold">{c.car}</div><div className="mute" style={{ fontSize: 12 }}>{c.note} · <a href={c.source} target="_blank" rel="noreferrer" style={{ textDecoration: 'underline' }}>source</a></div></div>)}
        </motion.div>))}</div>
    </div>
  );
}
