import { useEffect, useState } from 'react';
import { NavLink, Link, Outlet, useLocation } from 'react-router-dom';
import Lenis from 'lenis';
import { useStore } from '../store';
import Concierge from './Concierge';

export default function Layout() {
  const { user, logout, wishlist, compare, init } = useStore();
  const { pathname } = useLocation();
  const [cursor, setCursor] = useState({ x: -50, y: -50, big: false });

  useEffect(() => { init(); }, [init]);
  useEffect(() => {
    const lenis = new Lenis({ lerp: 0.09 });
    let raf; const loop = (t) => { lenis.raf(t); raf = requestAnimationFrame(loop); };
    raf = requestAnimationFrame(loop);
    return () => { cancelAnimationFrame(raf); lenis.destroy(); };
  }, []);
  useEffect(() => { window.scrollTo(0, 0); }, [pathname]);
  useEffect(() => {
    const move = (e) => setCursor({ x: e.clientX, y: e.clientY, big: !!e.target.closest?.('a,button,.card,canvas') });
    window.addEventListener('mousemove', move);
    return () => window.removeEventListener('mousemove', move);
  }, []);

  return (
    <>
      <div className={'cursor' + (cursor.big ? ' big' : '')} style={{ left: cursor.x - (cursor.big ? 27 : 5), top: cursor.y - (cursor.big ? 27 : 5) }} />
      <header className="nav">
        <Link to="/" className="logo">MAISON<span className="gold">·</span>AUTO</Link>
        <nav>
          <NavLink to="/showroom">Showroom</NavLink>
          <NavLink to="/auctions">Auctions</NavLink>
          <NavLink to="/celebrity-garage">Celebrity Garage</NavLink>
          <NavLink to="/compare">Compare{compare.length ? ` (${compare.length})` : ''}</NavLink>
          {user && <NavLink to="/wishlist">Wishlist ({wishlist.length})</NavLink>}
          {user?.role === 'admin' && <NavLink to="/admin">Admin</NavLink>}
          {user ? <a href="#" onClick={(e) => { e.preventDefault(); logout(); }}>Sign out</a> : <NavLink to="/login">Sign in</NavLink>}
        </nav>
      </header>
      <Outlet />
      <footer className="wrap mute" style={{ padding: '60px 28px', borderTop: '1px solid var(--line)', fontSize: 12 }}>
        © MAISON AUTO · Demo project. Car names and trademarks belong to their respective owners.
      </footer>
      <Concierge />
    </>
  );
}
