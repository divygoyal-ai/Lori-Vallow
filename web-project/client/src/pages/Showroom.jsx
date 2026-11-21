import { useState } from 'react';
import { useFetch, useToast } from '../hooks';
import CarCard from '../components/CarCard';

export default function Showroom() {
  const [search, setSearch] = useState('');
  const [category, setCategory] = useState('');
  const [sort, setSort] = useState('');
  const [toast, setToast] = useToast();
  const qs = new URLSearchParams({ ...(search && { search }), ...(category && { category }), ...(sort && { sort }) });
  const [cars] = useFetch('/cars?' + qs, []);
  return (
    <div className="page wrap">
      <div className="eyebrow">Showroom</div><h1 style={{ fontSize: 'clamp(2.4rem,5vw,4rem)', marginBottom: 30 }}>The collection</h1>
      <div className="row" style={{ marginBottom: 36 }}>
        <input style={{ maxWidth: 280 }} placeholder="Search brand or model" value={search} onChange={(e) => setSearch(e.target.value)} />
        <select style={{ maxWidth: 200 }} value={category} onChange={(e) => setCategory(e.target.value)}>
          <option value="">All categories</option>{['Hypercar', 'Supercar', 'Sports', 'Luxury', 'Grand Tourer'].map((c) => <option key={c}>{c}</option>)}
        </select>
        <select style={{ maxWidth: 200 }} value={sort} onChange={(e) => setSort(e.target.value)}>
          <option value="">Featured</option><option value="price_asc">Price ↑</option><option value="price_desc">Price ↓</option><option value="power">Most powerful</option>
        </select>
      </div>
      <div className="grid">{cars?.map((c, i) => <CarCard key={c.id} car={c} i={i} onToast={setToast} />)}</div>
      {cars?.length === 0 && <p className="mute">No cars match your filters.</p>}
      {toast && <div className="toast">{toast}</div>}
    </div>
  );
}
