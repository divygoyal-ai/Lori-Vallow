import { useEffect, useRef, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { GoogleLogin } from '@react-oauth/google';
import { api } from '../api';
import { useStore } from '../store';

const SITEKEY = import.meta.env.VITE_TURNSTILE_SITEKEY || '1x00000000000000000000AA';

function Turnstile({ onToken }) {
  const ref = useRef();
  useEffect(() => {
    const render = () => window.turnstile?.render(ref.current, { sitekey: SITEKEY, theme: 'dark', callback: onToken });
    if (window.turnstile) { render(); return; }
    const s = document.createElement('script');
    s.src = 'https://challenges.cloudflare.com/turnstile/v0/api.js?render=explicit';
    s.async = true; s.onload = render; document.head.appendChild(s);
  }, []); // eslint-disable-line
  return <div ref={ref} />;
}

export default function Login() {
  const [mode, setMode] = useState('login');
  const [f, setF] = useState({ name: '', email: '', password: '' });
  const [captcha, setCaptcha] = useState('');
  const [err, setErr] = useState('');
  const login = useStore((s) => s.login);
  const nav = useNavigate();
  const set = (k) => (e) => setF({ ...f, [k]: e.target.value });

  async function submit(e) {
    e.preventDefault(); setErr('');
    try { login(await api('/auth/' + (mode === 'login' ? 'login' : 'register'), { method: 'POST', body: { ...f, captcha } })); nav('/'); }
    catch (e) { setErr(e.message); window.turnstile?.reset(); setCaptcha(''); }
  }
  async function google(r) {
    try { login(await api('/auth/google', { method: 'POST', body: { credential: r.credential } })); nav('/'); } catch (e) { setErr(e.message); }
  }
  return (
    <div className="page wrap" style={{ display: 'grid', placeItems: 'center' }}>
      <form className="panel" onSubmit={submit} style={{ width: 420, display: 'grid', gap: 14 }}>
        <div className="eyebrow">Members</div><h2>{mode === 'login' ? 'Welcome back' : 'Join Maison Auto'}</h2>
        {mode === 'register' && <input placeholder="Full name" value={f.name} onChange={set('name')} required />}
        <input type="email" placeholder="Email" value={f.email} onChange={set('email')} required />
        <input type="password" placeholder="Password (8+ characters)" value={f.password} onChange={set('password')} minLength={8} required />
        <Turnstile onToken={setCaptcha} />
        {err && <div style={{ color: 'var(--red)', fontSize: 13 }}>{err}</div>}
        <button className="btn solid" disabled={!captcha}>{mode === 'login' ? 'Sign in' : 'Create account'}</button>
        <div className="mute" style={{ textAlign: 'center', fontSize: 12 }}>or</div>
        <div style={{ display: 'grid', placeItems: 'center' }}><GoogleLogin theme="filled_black" onSuccess={google} onError={() => setErr('Google sign-in failed')} /></div>
        <a href="#" className="mute" style={{ textAlign: 'center', fontSize: 13 }} onClick={(e) => { e.preventDefault(); setMode(mode === 'login' ? 'register' : 'login'); }}>
          {mode === 'login' ? 'New here? Create an account' : 'Have an account? Sign in'}</a>
      </form>
    </div>
  );
}
