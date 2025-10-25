import React from 'react';
import Upload from '../components/Upload';

export default function Home() {
  return (
    <div className="space-y-6">
      <div className="text-center">
        <h1 className="text-3xl md:text-4xl font-bold tracking-tight text-mango-700">Check your mango for pesticides</h1>
        <p className="mt-2 text-gray-600">Upload a photo and we’ll predict whether it’s organic or pesticide-treated.</p>
      </div>
      <Upload />
    </div>
  );
}
