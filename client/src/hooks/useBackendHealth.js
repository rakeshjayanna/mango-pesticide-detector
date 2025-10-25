import { useEffect, useState } from 'react';

export default function useBackendHealth(intervalMs = 5000) {
  const [online, setOnline] = useState(false);
  const [modelPresent, setModelPresent] = useState(false);
  const [checking, setChecking] = useState(true);

  async function check() {
    try {
      const res = await fetch('/api/health', { headers: { Accept: 'application/json' } });
      if (!res.ok) throw new Error('bad status');
      const data = await res.json();
      setOnline(true);
      setModelPresent(Boolean(data?.model_present));
    } catch (e) {
      setOnline(false);
      setModelPresent(false);
    } finally {
      setChecking(false);
    }
  }

  useEffect(() => {
    check();
    const id = setInterval(check, intervalMs);
    return () => clearInterval(id);
  }, [intervalMs]);

  return { online, modelPresent, checking };
}
