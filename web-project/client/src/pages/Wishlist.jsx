import { Navigate } from 'react-router-dom';
import { useFetch } from '../hooks';
import { useStore } from '../store';
import CarCard from '../components/CarCard';

export default function Wishlist() {
  const { user, wishlist } = useStore();
  const [cars] = useFetch('/wishlist', [wishlist.length]);
  if (!localStorage.getItem('token')) return <Navigate to="/login" />;
  return (
    <div className="page wrap"><div className="eyebrow">{user?.name}</div><h1 style={{ fontSize: 'clamp(2.4rem,5vw,4rem)', marginBottom: 30 }}>Your wishlist</h1>
      <div className="grid">{cars?.map((c, i) => <CarCard key={c.id} car={c} i={i} />)}</div>
      {cars?.length === 0 && <p className="mute">Nothing saved yet.</p>}
    </div>
  );
}
