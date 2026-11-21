import { useState, useRef, useEffect } from 'react';
import { api } from '../api';

export default function Concierge() {
  const [open, setOpen] = useState(false);
  const [msgs, setMsgs] = useState([{ role: 'assistant', content: 'Welcome to Maison Auto. How may I assist your search today?' }]);
  const [text, setText] = useState('');
  const [busy, setBusy] = useState(false);
  const end = useRef();
  useEffect(() => { end.current?.scrollIntoView({ behavior: "smooth" }); }, [msgs]);

  async function send(e) {
    e.preventDefault();
    if (!text.trim() || busy) return;
    const next = [...msgs, { role: 'user', content: text }];
    setMsgs(next); setText(''); setBusy(true);
    try {
      const { reply } = await api('/concierge', { method: 'POST', body: { messages: next.slice(1) } });
      setMsgs([...next, { role: 'assistant', content: reply }]);
    } catch { setMsgs([...next, { role: 'assistant', content: 'Connection issue, please try again.' }]); }
    setBusy(false);
  }
  return (
    <div className="chat">
      {open && (
        <div className="win">
          <div style={{ padding: 14, borderBottom: '1px solid var(--line)' }} className="serif gold">Concierge</div>
          <div className="msgs">
            {msgs.map((m, i) => <div key={i} className={'msg ' + (m.role === 'user' ? 'u' : 'mute')}>{m.content}</div>)}
            {busy && <div className="mute">…</div>}<div ref={end} />
          </div>
          <form onSubmit={send} style={{ display: 'flex' }}><input value={text} onChange={(e) => setText(e.target.value)} placeholder="Ask about any car…" /><button className="btn sm solid">Send</button></form>
        </div>
      )}
      <button className="btn solid" onClick={() => setOpen(!open)}>{open ? 'Close' : 'Concierge'}</button>
    </div>
  );
}
