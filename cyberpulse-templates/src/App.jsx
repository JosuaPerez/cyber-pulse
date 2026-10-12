import { useState } from 'react';
import PostInstagram from './PostInstagram';

function leerPostDesdeUrl(search) {
  const params = new URLSearchParams(search);
  const type = params.get('type') || 'cover';
  let parsedSummary = type === 'tip_content' ? {} : [];

  if (params.get('summary')) {
    try {
      parsedSummary = JSON.parse(params.get('summary'));
    } catch (error) {
      console.error('Error al decodificar viñetas:', error);
    }
  }

  return {
    type,
    familia: params.get('familia') || 'alerta',
    level: params.get('level') || 'critical',
    category: params.get('category') || 'CYBERPULSE',
    title: params.get('title') || 'Error: Sin título',
    description: params.get('description') || '',
    summary: parsedSummary,
    currentSlide: Number.parseInt(params.get('currentSlide'), 10) || 1,
    totalSlides: Number.parseInt(params.get('totalSlides'), 10) || 5,
  };
}

function App() {
  const [postData] = useState(() => leerPostDesdeUrl(window.location.search));

  return (
    <div className="flex items-center justify-center min-h-screen bg-black">
      <PostInstagram {...postData} />
    </div>
  );
}

export default App;
