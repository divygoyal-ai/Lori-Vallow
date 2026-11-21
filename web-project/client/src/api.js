import { io } from 'socket.io-client';

export const token = () => localStorage.getItem('token');
export async function api(path, { method = 'GET', body } = {}) {
  const res = await fetch('/api' + path, {
    method,
    headers: { 'Content-Type': 'application/json', ...(token() && { Authorization: 'Bearer ' + token() }) },
    body: body && JSON.stringify(body),
  });
  const data = await res.json().catch(() => ({}));
  if (!res.ok) throw new Error(data.error || 'Request failed');
  return data;
}
export const socket = io({ autoConnect: true });
export const money = (n) => '$' + Number(n).toLocaleString('en-US');
