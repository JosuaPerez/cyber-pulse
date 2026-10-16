import { useState } from 'react';
import PostInstagram from './PostInstagram';
import AlertPreview from './AlertPreview';
import DailyAlert from './DailyAlert';
import AlertSeriesPreview from './AlertSeriesPreview';
import RealAlertPreview from './RealAlertPreview';

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
    alertVariant: params.get('alertVariant') || 'clasica',
    sourceName: params.get('sourceName') || '',
    sourceUrl: params.get('sourceUrl') || '',
    sourceDate: params.get('sourceDate') || '',
    preparedOn: params.get('preparedOn') || '',
    supportVisual: params.get('supportVisual') || '{}',
    editorialData: params.get('editorialData') || '{}',
    exploitation: params.get('exploitation') || 'desconocido',
    cves: params.get('cves') || '[]',
  };
}

function App() {
  const [postData] = useState(() => leerPostDesdeUrl(window.location.search));
  const params = new URLSearchParams(window.location.search);

  if (params.get('preview') === 'alerts') {
    return <AlertPreview variant={params.get('variant') || 'update'} />;
  }
  if (params.get('preview') === 'alerts-series') {
    return <AlertSeriesPreview variant={params.get('variant')} slide={params.get('slide')} />;
  }
  if (params.get('preview') === 'real-alerts') {
    return <RealAlertPreview variant={params.get('variant')} slide={params.get('slide')} />;
  }
  if (postData.familia === 'alerta' && ['editorial', 'clara'].includes(postData.alertVariant)) {
    return <DailyAlert {...postData} layout={postData.alertVariant === 'clara' ? 'update' : 'editorial'} />;
  }

  return (
    <div className="flex items-center justify-center min-h-screen bg-black">
      <PostInstagram {...postData} />
    </div>
  );
}

export default App;
