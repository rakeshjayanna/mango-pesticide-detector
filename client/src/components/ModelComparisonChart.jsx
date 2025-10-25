import React, { useEffect, useState } from 'react';
import { Bar } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js';

ChartJS.register(CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend);

export default function ModelComparisonChart() {
  const [data, setData] = useState(null);
  const [error, setError] = useState('');

  useEffect(() => {
    let mounted = true;
    fetch('/api/models/comparison')
      .then(async (res) => {
        const ct = res.headers.get('content-type') || '';
        const payload = ct.includes('application/json') ? await res.json() : { error: await res.text() };
        if (!res.ok) throw new Error(payload?.error || 'Failed to load model comparison');
        if (mounted) setData(payload);
      })
      .catch((e) => {
        if (mounted) setError(e.message);
      });
    return () => { mounted = false; };
  }, []);

  if (error) {
    return (
      <div className="card border-red-100 bg-red-50 p-4 text-red-700">
        <p className="font-medium">Model comparison unavailable</p>
        <p className="text-sm">{error}</p>
      </div>
    );
  }

  if (!data) return null;

  const acc = {
    cnn: (data.models?.cnn?.accuracy || 0) * 100,
    svm: (data.models?.svm?.accuracy || 0) * 100,
    random_forest: (data.models?.random_forest?.accuracy || 0) * 100,
  };

  const best = data.best?.name;

  const chartData = {
    labels: ['CNN', 'SVM', 'Random Forest'],
    datasets: [
      {
        label: 'Accuracy (%)',
        data: [acc.cnn, acc.svm, acc.random_forest],
        backgroundColor: ['#f59e0b', '#60a5fa', '#34d399'],
        borderRadius: 6,
      },
    ],
  };

  const options = {
    responsive: true,
    plugins: {
      legend: { position: 'top' },
      title: { display: true, text: 'Model Accuracy Comparison' },
      tooltip: { callbacks: { label: (ctx) => `${ctx.dataset.label}: ${ctx.raw.toFixed(2)}%` } },
    },
    scales: {
      y: { beginAtZero: true, max: 100, ticks: { callback: (v) => `${v}%` } },
    },
  };

  return (
    <div className="card p-6 bg-white/70 shadow-lg ring-1 ring-amber-100/60">
      <div className="flex items-center justify-between mb-4">
        <div>
          <h3 className="text-lg font-semibold text-gray-800">Model comparison</h3>
          <p className="text-sm text-gray-500">Higher is better. Using the best model automatically for detection.</p>
        </div>
        {best && (
          <span className="inline-flex items-center gap-2 rounded-full bg-emerald-100 px-3 py-1 text-sm font-medium text-emerald-800">
            <span className="h-2 w-2 rounded-full bg-emerald-500"></span>
            Best: {best.replace('_', ' ')}
          </span>
        )}
      </div>
      <Bar data={chartData} options={options} height={120} />
    </div>
  );
}
