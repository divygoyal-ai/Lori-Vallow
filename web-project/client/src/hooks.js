import { useEffect, useState } from 'react';
import { api } from './api';

export function useFetch(path, deps = []) {
  const [data, setData] = useState(null);
  const [error, setError] = useState(null);
  useEffect(() => { setData(null); api(path).then(setData).catch(setError); }, [path, ...deps]); // eslint-disable-line
  return [data, error, setData];
}
export function useToast() {
  const [t, setT] = useState('');
  useEffect(() => { if (t) { const id = setTimeout(() => setT(''), 2600); return () => clearTimeout(id); } }, [t]);
  return [t, setT];
}
export function useCountdown(endsAt) {
  const [now, setNow] = useState(Date.now());
  useEffect(() => { const id = setInterval(() => setNow(Date.now()), 1000); return () => clearInterval(id); }, []);
  const ms = Math.max(0, new Date(endsAt) - now);
  const d = Math.floor(ms / 864e5), h = Math.floor(ms / 36e5) % 24, m = Math.floor(ms / 6e4) % 60, s = Math.floor(ms / 1e3) % 60;
  return { ms, text: ms ? `${d ? d + 'd ' : ''}${String(h).padStart(2, '0')}:${String(m).padStart(2, '0')}:${String(s).padStart(2, '0')}` : 'Ended' };
}
