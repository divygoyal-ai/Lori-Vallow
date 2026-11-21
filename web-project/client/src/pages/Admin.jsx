import { useState } from 'react';
import { Navigate } from 'react-router-dom';
import { api, money } from '../api';
import { useFetch, useToast } from '../hooks';
import { useStore } from '../store';

const blank = { slug: '', brand: '', model: '', year: 2025, price: 0, category: 'Supercar', description: '', model_url: '', colors: [{ name: 'Black', hex: '#111111' }], specs: { engine: '', power_hp: 0, torque_nm: 0, zero_to_100: 0, top_speed_kmh: 0, drivetrain: 'AWD', weight_kg: 0 } };

export default function Admin() {
  const user = useStore((s) => s.user);
  const [tab, setTab] = useState('overview');
  const [n, setN] = useState(0);
  const [stats] = useFetch('/admin/stats', [n]);
  const [cars] = useFetch('/cars', [n]);
  const [users] = useFetch('/admin/users', [n]);
  const [viewings] = useFetch('/admin/viewings', [n]);
  const [toast, setToast] = useToast();
  const [form, setForm] = useState(blank);
  const [auc, setAuc] = useState({ carId: '', startingBid: '', minIncrement: 5000, hours: 24 });

  if (!localStorage.getItem('token')) return <Navigate to="/login" />;
  if (user && user.role !== 'admin') return <div className="page wrap">Admin access only.</div>;

  const run = async (fn, msg) => { try { await fn(); setToast(msg); setN((x) => x + 1); } catch (e) { setToast(e.message); } };
  const save = (e) => { e.preventDefault(); run(() => api('/admin/cars', { method: 'POST', body: { ...form, year: +form.year, price: +form.price, model_url: form.model_url || null } }).then(() => setForm(blank)), 'Car added'); };
  const f = (k) => ({ value: form[k], onChange: (e) => setForm({ ...form, [k]: e.target.value }) });
  const sp = (k) => ({ value: form.specs[k], onChange: (e) => setForm({ ...form, specs: { ...form.specs, [k]: isNaN(e.target.value) || e.target.value === '' ? e.target.value : +e.target.value } }) });

  return (
    <div className="page wrap">
      <div className="eyebrow">Admin</div><h1 style={{ fontSize: 48, marginBottom: 24 }}>Control room</h1>
      <div className="row" style={{ marginBottom: 30 }}>{['overview', 'cars', 'auctions', 'viewings', 'users'].map((t) => <button key={t} className={'btn sm' + (tab === t ? ' solid' : '')} onClick={() => setTab(t)}>{t}</button>)}</div>

      {tab === 'overview' && stats && <>
        <div className="grid" style={{ gridTemplateColumns: 'repeat(auto-fill,minmax(180px,1fr))' }}>
          {[['Users', stats.users], ['Cars', stats.cars], ['Live auctions', stats.liveAuctions], ['Total bids', stats.bids], ['Viewing requests', stats.viewings]].map(([l, v]) => <div key={l} className="panel"><div className="big">{v}</div><div className="mute">{l}</div></div>)}
        </div>
        <h3 style={{ margin: '36px 0 12px' }}>Most wishlisted</h3>
        {stats.topWishlisted.length ? stats.topWishlisted.map((c) => <div key={c.model} className="mute">{c.brand} {c.model} — {c.n}</div>) : <p className="mute">No wishlist activity yet.</p>}
      </>}

      {tab === 'cars' && <div className="split">
        <table className="specs"><tbody>{cars?.map((c) => <tr key={c.id}><td style={{ width: 'auto' }}>{c.brand} {c.model}</td><td>{money(c.price)}</td>
          <td><button className="btn sm" onClick={() => confirm('Delete ' + c.model + '?') && run(() => api('/admin/cars/' + c.id, { method: 'DELETE' }), 'Deleted')}>Delete</button></td></tr>)}</tbody></table>
        <form className="panel" onSubmit={save} style={{ display: 'grid', gap: 10 }}>
          <div className="serif" style={{ fontSize: 24 }}>Add car</div>
          <input placeholder="slug (e.g. ferrari-296)" {...f('slug')} required /><input placeholder="Brand" {...f('brand')} required /><input placeholder="Model" {...f('model')} required />
          <div className="row"><input type="number" placeholder="Year" {...f('year')} /><input type="number" placeholder="Price" {...f('price')} /></div>
          <input placeholder="Category" {...f('category')} /><textarea placeholder="Description" {...f('description')} />
          <input placeholder="GLB model URL (optional, licensed)" {...f('model_url')} />
          <input placeholder="Engine" {...sp('engine')} />
          <div className="row"><input type="number" placeholder="hp" {...sp('power_hp')} /><input type="number" placeholder="Nm" {...sp('torque_nm')} /></div>
          <div className="row"><input type="number" step="0.1" placeholder="0-100 s" {...sp('zero_to_100')} /><input type="number" placeholder="km/h" {...sp('top_speed_kmh')} /></div>
          <button className="btn solid">Add car</button>
        </form></div>}

      {tab === 'auctions' && <form className="panel" style={{ maxWidth: 460, display: 'grid', gap: 10 }} onSubmit={(e) => { e.preventDefault(); run(() => api('/admin/auctions', { method: 'POST', body: { carId: +auc.carId, startingBid: +auc.startingBid, minIncrement: +auc.minIncrement, endsAt: new Date(Date.now() + auc.hours * 36e5) } }), 'Auction started'); }}>
        <div className="serif" style={{ fontSize: 24 }}>Start an auction</div>
        <select value={auc.carId} onChange={(e) => setAuc({ ...auc, carId: e.target.value })} required><option value="">Select car</option>{cars?.map((c) => <option key={c.id} value={c.id}>{c.brand} {c.model}</option>)}</select>
        <input type="number" placeholder="Starting bid" value={auc.startingBid} onChange={(e) => setAuc({ ...auc, startingBid: e.target.value })} required />
        <input type="number" placeholder="Min increment" value={auc.minIncrement} onChange={(e) => setAuc({ ...auc, minIncrement: e.target.value })} />
        <input type="number" placeholder="Duration (hours)" value={auc.hours} onChange={(e) => setAuc({ ...auc, hours: e.target.value })} />
        <button className="btn solid">Start</button></form>}

      {tab === 'viewings' && <table className="specs"><tbody>{viewings?.map((v) => <tr key={v.id}><td style={{ width: 'auto' }}>{v.brand} {v.model}</td><td>{v.email}</td><td>{v.preferred_date?.slice(0, 10)}</td></tr>)}</tbody></table>}
      {tab === 'users' && <table className="specs"><tbody>{users?.map((u) => <tr key={u.id}><td style={{ width: 'auto' }}>{u.name}</td><td>{u.email}</td><td>{u.role}</td></tr>)}</tbody></table>}
      {toast && <div className="toast">{toast}</div>}
    </div>
  );
}
