import { Routes, Route } from 'react-router-dom';
import Layout from './components/Layout';
import Home from './pages/Home';
import Showroom from './pages/Showroom';
import CarDetail from './pages/CarDetail';
import Compare from './pages/Compare';
import { Auctions, AuctionRoom } from './pages/Auctions';
import Celebrities from './pages/Celebrities';
import Login from './pages/Login';
import Wishlist from './pages/Wishlist';
import Admin from './pages/Admin';

export default function App() {
  return (
    <Routes>
      <Route element={<Layout />}>
        <Route index element={<Home />} />
        <Route path="showroom" element={<Showroom />} />
        <Route path="car/:slug" element={<CarDetail />} />
        <Route path="compare" element={<Compare />} />
        <Route path="auctions" element={<Auctions />} />
        <Route path="auctions/:id" element={<AuctionRoom />} />
        <Route path="celebrity-garage" element={<Celebrities />} />
        <Route path="login" element={<Login />} />
        <Route path="wishlist" element={<Wishlist />} />
        <Route path="admin" element={<Admin />} />
      </Route>
    </Routes>
  );
}
