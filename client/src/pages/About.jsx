import React from 'react';

export default function About() {
  return (
    <div className="card p-6">
      <h2 className="text-2xl font-semibold text-mango-700">About</h2>
      <p className="mt-2 text-gray-700">
        This app demonstrates a simple computer vision workflow: a TensorFlow/Keras model trained to classify
        mango images as organic or pesticide-treated. The React frontend uploads an image to a Flask backend,
        which loads a saved model and returns a prediction and confidence.
      </p>
      <ul className="mt-4 list-disc pl-6 text-gray-700">
        <li>Frontend: React + Tailwind CSS</li>
        <li>Backend: Flask + TensorFlow</li>
        <li>Model: CNN trained on two classes (organic, pesticide)</li>
      </ul>
    </div>
  );
}
