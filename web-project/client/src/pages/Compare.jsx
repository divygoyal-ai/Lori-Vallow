import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { api, money } from '../api';
import { useStore } from '../store';

const rows = [
  ['Price', (c) => money(c.price), (c) => -c.price],
  ['Year', (c) => c.year, (c) => c.year],
  ['Engine', (c) => c.specs.engine],
  ['Power', (c) => c.specs.power_hp + ' hp', (c) => c.specs.power_hp],
  ['Torque', (c) => c.specs.torque_nm + ' Nm', (c) => c.specs.torque_nm],
  ['0–100 km/h', (c) => c.specs.zero_to_100 + 's', (c) => -c.specs.zero_to_100],
  ['Top speed', (c) => c.specs.top_speed_kmh + ' km/h', (c) => c.specs.top_speed_kmh],
  ['Drivetrain', (c) => c.specs.drivetrain],
  ['Weight', (c) => c.specs.weight_kg + ' kg', (c) => -c.specs.weight_kg],
];

export default function Compare() {
  const { compare, toggleCompare } = useStore();
  const [cars, setCars] = useState([]);
  const [all, setAll] = useState([]);
  const [color, setColor] = useState({});
  useEffect(() => { api('/cars').then(setAll); }, []);
  useEffect(() => { setCars(compare.map((s) => all.find((c) => c.slug === s)).filter(Boolean)); }, [compare, all]);

  return (
    <div className="page wrap">
      <div className="eyebrow">Compare</div><h1 style={{ fontSize: 'clamp(2.4rem,5vw,4rem)', marginBottom: 30 }}>Side by side</h1>
      {cars.length < 3 && (
        <select style={{ maxWidth: 320, marginBottom: 30 }} value="" onChange={(e) => e.target.value && toggleCompare(e.target.value)}>
          <option value="">+ Add a car (up to 3)</option>
          {all.filter((c) => !compare.includes(c.slug)).map((c) => <option key={c.id} value={c.slug}>{c.brand} {c.model}</option>)}
        </select>
      )}
      {cars.length === 0 ? <p className="mute">Pick cars to compare, or press ⇄ on any car card. Visit the <Link to="/showroom" className="gold">showroom</Link>.</p> : (
        <div style={{ overflowX: 'auto' }}>
          <table className="specs">
            <thead><tr><th />{cars.map((c) => (
              <th key={c.id}>
                <div className="mute" style={{ fontSize: 11, letterSpacing: '.2em', fontFamily: 'Inter' }}>{c.brand.toUpperCase()}</div>
                <Link to={`/car/${c.slug}`}>{c.model}</Link>
                <div className="row" style={{ marginTop: 10 }}>{c.colors.map((col) => (
                  <span key={col.name} title={col.name} className={'swatch' + ((color[c.slug] ?? c.colors[0].name) === col.name ? ' on' : '')} style={{ background: col.hex, width: 20, height: 20 }} onClick={() => setColor({ ...color, [c.slug]: col.name })} />
                ))}</div>
                <div className="mute" style={{ fontSize: 12, fontFamily: 'Inter', fontWeight: 300 }}>{color[c.slug] ?? c.colors[0].name}</div>
                <button className="btn sm" style={{ marginTop: 10 }} onClick={() => toggleCompare(c.slug)}>Remove</button>
              </th>))}</tr></thead>
            <tbody>{rows.map(([label, fmt, score]) => {
              const best = score && cars.length > 1 ? Math.max(...cars.map(score)) : null;
              return <tr key={label}><td>{label}</td>{cars.map((c) => <td key={c.id} className={score && score(c) === best ? 'best' : ''}>{fmt(c)}</td>)}</tr>;
            })}</tbody>
          </table>
          <p className="mute" style={{ fontSize: 12, marginTop: 12 }}>Gold marks the best value in each row.</p>
        </div>
      )}
    </div>
  );
}
