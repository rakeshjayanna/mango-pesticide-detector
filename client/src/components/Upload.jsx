import React, { useState, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import useBackendHealth from '../hooks/useBackendHealth';

export default function Upload() {
  const navigate = useNavigate();
  const { online, modelPresent, checking } = useBackendHealth(7000);
  const [file, setFile] = useState(null);
  const [preview, setPreview] = useState('');
  const [result, setResult] = useState(null);
  const [fullCompare, setFullCompare] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [dragActive, setDragActive] = useState(false);
  const inputRef = useRef(null);

  const MAX_BYTES = 5 * 1024 * 1024; // 5MB
  const ACCEPTED_TYPES = ['image/jpeg', 'image/png', 'image/webp'];

  const validateFile = (f) => {
    if (!f) return 'No file selected';
    if (!ACCEPTED_TYPES.includes(f.type)) return 'Only JPG, PNG, or WEBP images are allowed.';
    if (f.size > MAX_BYTES) return 'File is too large (max 5MB).';
    return '';
  };

  const applyFile = (f) => {
    setResult(null);
    setError('');
    const err = validateFile(f);
    if (err) {
      setFile(null);
      setPreview('');
      setError(err);
      return;
    }
    setFile(f);
    if (f) {
      const url = URL.createObjectURL(f);
      setPreview(url);
    } else {
      setPreview('');
    }
  };

  const onFileChange = (e) => {
    const f = e.target.files?.[0];
    applyFile(f || null);
  };

  const onDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      applyFile(e.dataTransfer.files[0]);
    }
  };

  const onDragOver = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(true);
  };

  const onDragLeave = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
  };

  const onSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setResult(null);
    if (!file) {
      setError('Please select an image first.');
      return;
    }
    const form = new FormData();
    form.append('image', file);
    setLoading(true);
    try {
      const res = await fetch('/api/detect', { method: 'POST', body: form, headers: { 'Accept': 'application/json' } });
      const contentType = res.headers.get('content-type') || '';
      let data;
      if (contentType.includes('application/json')) {
        data = await res.json();
      } else {
        const text = await res.text();
        throw new Error(text?.slice(0, 200) || 'Non-JSON response from server');
      }
      if (!res.ok) throw new Error(data?.error || 'Request failed');
      setResult({ label: data.label, confidence: data.confidence, model_used: data.model_used });
      if (data.models && data.selection) {
        const comparePayload = { models: data.models, selection: data.selection, final: { label: data.label, confidence: data.confidence } };
        setFullCompare(comparePayload);
        try { sessionStorage.setItem('lastCompare', JSON.stringify(comparePayload)); } catch {}
      }
    } catch (err) {
      setError((err && err.message) ? err.message : 'Request failed');
    } finally {
      setLoading(false);
    }
  };

  const reset = () => {
    setFile(null);
    setPreview('');
    setResult(null);
    setError('');
    if (inputRef.current) inputRef.current.value = '';
  };

  return (
    <section>
      <motion.form
        onSubmit={onSubmit}
        className="card p-6 bg-gradient-to-br from-white to-amber-50 shadow-xl ring-1 ring-amber-100/60"
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.4, ease: 'easeOut' }}
      >
        <div className="flex flex-col gap-4 md:flex-row">
          <div className="flex-1">
            <label className="block text-sm font-medium text-gray-700 mb-2">Upload Mango Image</label>
            <div className="flex items-center gap-3">
              <input
                ref={inputRef}
                className="block w-full text-sm text-gray-700 file:mr-4 file:rounded-md file:border-0 file:bg-mango-100 file:px-4 file:py-2 file:text-mango-700 hover:file:bg-mango-200"
                type="file"
                accept="image/*"
                onChange={onFileChange}
              />
              {file && (
                <button type="button" className="btn-secondary" onClick={reset}>
                  Clear
                </button>
              )}
            </div>
            <p className="mt-2 text-xs text-gray-500">Supported formats: JPG, PNG. Max size depends on server limits.</p>
          </div>
          <div className="w-full md:w-64">
            <div
              className={`aspect-square overflow-hidden rounded-xl border  bg-white shadow-inner flex items-center justify-center ${dragActive ? 'border-mango-500 ring-2 ring-mango-300' : 'border-amber-100'}`}
              onDrop={onDrop}
              onDragOver={onDragOver}
              onDragLeave={onDragLeave}
            >
              <AnimatePresence mode="wait">
                {preview ? (
                  <motion.img
                    key={preview}
                    src={preview}
                    alt="Preview"
                    className="h-full w-full object-cover"
                    initial={{ opacity: 0, scale: 0.98 }}
                    animate={{ opacity: 1, scale: 1 }}
                    exit={{ opacity: 0, scale: 0.98 }}
                    transition={{ duration: 0.25 }}
                  />
                ) : (
                  <motion.div
                    key="empty"
                    className="flex h-full w-full items-center justify-center text-gray-500 p-4 text-center"
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    exit={{ opacity: 0 }}
                  >
                    <div>
                      <p className="font-medium">Drag & drop an image here</p>
                      <p className="text-xs text-gray-400">or use the file picker • JPG/PNG/WEBP • max 5MB</p>
                    </div>
                  </motion.div>
                )}
              </AnimatePresence>
            </div>
          </div>
        </div>

        <div className="mt-6 flex items-center gap-3">
          <motion.button
            type="submit"
            disabled={loading || !online || checking}
            whileHover={!loading ? { scale: 1.02 } : undefined}
            whileTap={!loading ? { scale: 0.98 } : undefined}
            className="btn-primary shadow-md shadow-amber-200/60"
          >
            {loading ? (
              <span className="inline-flex items-center gap-2">
                <span className="inline-block h-4 w-4 animate-spin rounded-full border-2 border-white border-t-transparent"></span>
                Detecting...
              </span>
            ) : (
              (checking ? 'Checking API…' : (!online ? 'API offline' : 'Detect Pesticide'))
            )}
          </motion.button>
          {result && (
            <button type="button" className="btn-secondary" onClick={reset}>
              Try another image
            </button>
          )}
          {fullCompare && (
            <button
              type="button"
              className="btn-secondary"
              onClick={() => navigate('/compare', { state: { compareResult: fullCompare } })}
            >
              View comparison chart
            </button>
          )}
        </div>
      </motion.form>

      {error && (
        <div className="mt-4 card border-red-100 bg-red-50 p-4 text-red-700">
          <p className="font-medium">Error</p>
          <p className="text-sm">{error}</p>
        </div>
      )}

      {!error && !loading && !checking && online && !modelPresent && (
        <div className="mt-4 card border-amber-200 bg-amber-50 p-4 text-amber-800">
          <p className="font-medium">Model not found</p>
          <p className="text-sm">Train the model to create <code>server/model/mango_model.h5</code> before running detection.</p>
        </div>
      )}

      <AnimatePresence>
        {result && !error && (
          <motion.div
            key="result"
            className="mt-4 card p-6 bg-gradient-to-br from-white to-amber-50 shadow-xl ring-1 ring-amber-100/60"
            initial={{ opacity: 0, y: 8, scale: 0.98 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: -8, scale: 0.98 }}
            transition={{ duration: 0.3 }}
          >
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm uppercase tracking-wide text-gray-500">Prediction</p>
                <p className="text-2xl font-semibold capitalize">{result.label || 'Unknown'}</p>
              </div>
              <div className="text-right">
                <p className="text-sm uppercase tracking-wide text-gray-500">Confidence</p>
                <p className="text-2xl font-semibold text-mango-700">{typeof result.confidence === 'number' ? `${result.confidence}%` : '—'}</p>
              </div>
            </div>
            {result.model_used && (
              <p className="mt-2 text-xs text-gray-500">Model used: {String(result.model_used).replace('_',' ')}</p>
            )}
          </motion.div>
        )}
      </AnimatePresence>
    </section>
  );
}
