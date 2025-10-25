import React from 'react';
import useBackendHealth from '../hooks/useBackendHealth';

export default function HealthBadge() {
  const { online, modelPresent, checking } = useBackendHealth(7000);

  const color = checking ? 'bg-gray-300' : online ? 'bg-green-500' : 'bg-red-500';
  const text = checking ? 'Checking…' : online ? (modelPresent ? 'API: Online • Model: OK' : 'API: Online • Model: Missing') : 'API: Offline';

  return (
    <div className={`hidden sm:flex items-center gap-2 px-3 py-1 rounded-full text-xs font-medium text-white ${color}`}
         title="Backend health">
      <span className="inline-block h-2 w-2 rounded-full bg-white/90"></span>
      <span>{text}</span>
    </div>
  );
}
