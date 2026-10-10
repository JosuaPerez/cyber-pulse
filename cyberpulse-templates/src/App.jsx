import React, { useEffect, useState } from 'react';
import PostInstagram from './PostInstagram';

function App() {
  const [postData, setPostData] = useState(null);

  useEffect(() => {
    // Leemos la URL exacta que Playwright está visitando
    const params = new URLSearchParams(window.location.search);
    
    // Decodificamos las viñetas del JSON
    let parsedSummary = [];
    if (params.get('summary')) {
      try {
        parsedSummary = JSON.parse(params.get('summary'));
      } catch (error) {
        console.error("Error al decodificar viñetas:", error);
      }
    }

    // Guardamos los datos asegurándonos de extraer el 'type' correcto
    setPostData({
      type: params.get('type') || 'cover',
      familia: params.get('familia') || 'alerta',
      level: params.get('level') || 'critical',
      category: params.get('category') || 'CYBERPULSE',
      title: params.get('title') || 'Error: Sin título',
      description: params.get('description') || '',
      summary: parsedSummary,
      currentSlide: parseInt(params.get('currentSlide')) || 1,
      totalSlides: parseInt(params.get('totalSlides')) || 5
    });
  }, []);

  // No renderizar hasta que tengamos los datos de la URL
  if (!postData) return null;

  return (
    <div className="flex items-center justify-center min-h-screen bg-black">
      <PostInstagram {...postData} />
    </div>
  );
}

export default App;