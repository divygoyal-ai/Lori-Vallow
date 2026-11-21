import { useState } from 'react';
import { useParams } from 'react-router-dom';
import CarViewer from '../components/CarViewer';
import { useFetch, useToast } from '../hooks';
import { useStore } from '../store';
import { api, money } from '../api';

export default function CarDetail() {
  const { slug } = useParams();
  const [car, err] = useFetch('/cars/' + slug);
  const [ci, setCi] = useState(0);
  const [view, setView] = useState('exterior');
  const [doors, setDoors] = useState(false);
  const [lights, setLights] = useState(false);
  const [date, setDate] = useState('');
  const [toast, setToast] = useToast();
  const { user, wishlist, toggleWish, compare, toggleCompare } = useStore();

  if (err) return <div className="page wrap">Car not found.</div>;
  if (!car) return <div className="page wrap mute">Loading…</div>;
  const color = car.colors[ci];
  const s = car.specs;

  async function book() {
    if (!user) return setToast('Sign in to book a viewing');
    try { await api('/viewings', { method: 'POST', body: { carId: car.id, date } }); setToast('Viewing requested — we will confirm by email'); }
    catch (e) { setToast(e.message); }
  }
  return (
    <div className="page wrap">
      <div className="split">
        <div>
          <div className="viewer"><CarViewer color={color?.hex} modelUrl={car.model_url} view={view} doorsOpen={doors} lights={lights} />
            <div className="tools">
              <button className={'btn sm' + (view === 'exterior' ? ' solid' : '')} onClick={() => setView('exterior')}>Exterior 360°</button>
              <button className={'btn sm' + (view === 'interior' ? ' solid' : '')} onClick={() => setView('interior')}>Interior</button>
              <button className={'btn sm' + (doors ? ' solid' : '')} onClick={() => setDoors(!doors)}>Doors</button>
              <button className={'btn sm' + (lights ? ' solid' : '')} onClick={() => setLights(!lights)}>Lights</button>
            </div>
          </div>
          <p className="mute" style={{ fontSize: 12, marginTop: 10 }}>Drag to rotate · scroll to zoom. {car.model_url ? '' : 'Stylised placeholder model — upload a licensed GLB in Admin for the real car.'}</p>
        </div>
        <div>
          <div className="eyebrow">{car.brand} · {car.year}</div>
          <h1 style={{ fontSize: 56 }}>{car.model}</h1>
          <div className="big">{money(car.price)}</div>
          <p className="mute" style={{ margin: '16px 0 24px' }}>{car.description}</p>
          <div className="mute" style={{ fontSize: 12, letterSpacing: '.15em', marginBottom: 10 }}>COLOUR — {color?.name.toUpperCase()}</div>
          <div className="row" style={{ marginBottom: 28 }}>{car.colors.map((c, i) => <span key={c.name} title={c.name} className={'swatch' + (i === ci ? ' on' : '')} style={{ background: c.hex }} onClick={() => setCi(i)} />)}</div>
          <div className="row" style={{ marginBottom: 28 }}>
            <button className={'btn' + (wishlist.includes(car.id) ? ' solid' : '')} onClick={async () => { if (!user) return setToast('Sign in to save cars'); await toggleWish(car.id); }}>{wishlist.includes(car.id) ? '♥ Saved' : '♡ Wishlist'}</button>
            <button className={'btn' + (compare.includes(car.slug) ? ' solid' : '')} onClick={() => toggleCompare(car.slug)}>⇄ Compare</button>
          </div>
          <table className="specs"><tbody>
            <tr><td>Engine</td><td>{s.engine}</td></tr><tr><td>Power</td><td>{s.power_hp} hp</td></tr><tr><td>Torque</td><td>{s.torque_nm} Nm</td></tr>
            <tr><td>0–100 km/h</td><td>{s.zero_to_100}s</td></tr><tr><td>Top speed</td><td>{s.top_speed_kmh} km/h</td></tr><tr><td>Drivetrain</td><td>{s.drivetrain}</td></tr>
          </tbody></table>
          <div className="panel" style={{ marginTop: 28 }}>
            <div className="serif" style={{ fontSize: 24, marginBottom: 12 }}>Book a private viewing</div>
            <div className="row"><input type="date" value={date} onChange={(e) => setDate(e.target.value)} style={{ flex: 1 }} /><button className="btn solid" onClick={book}>Request</button></div>
          </div>
        </div>
      </div>
      {toast && <div className="toast">{toast}</div>}
    </div>
  );
}
