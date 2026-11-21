import { create } from 'zustand';
import { api } from './api';

export const useStore = create((set, get) => ({
  user: null,
  wishlist: [],
  compare: JSON.parse(localStorage.getItem('compare') || '[]'),
  async init() {
    if (!localStorage.getItem('token')) return;
    try { set({ user: await api('/auth/me') }); get().loadWishlist(); } catch { localStorage.removeItem('token'); }
  },
  async loadWishlist() { set({ wishlist: (await api('/wishlist')).map((c) => c.id) }); },
  login({ token, user }) { localStorage.setItem('token', token); set({ user }); get().loadWishlist(); },
  logout() { localStorage.removeItem('token'); set({ user: null, wishlist: [] }); },
  async toggleWish(id) {
    const has = get().wishlist.includes(id);
    set({ wishlist: has ? get().wishlist.filter((x) => x !== id) : [...get().wishlist, id] });
    try { await api('/wishlist/' + id, { method: has ? 'DELETE' : 'POST' }); }
    catch { get().loadWishlist(); return false; }
    return true;
  },
  toggleCompare(slug) {
    let c = get().compare;
    c = c.includes(slug) ? c.filter((x) => x !== slug) : [...c, slug].slice(-3);
    localStorage.setItem('compare', JSON.stringify(c));
    set({ compare: c });
  },
}));
