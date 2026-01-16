import React from 'react';
import ReactDOM from 'react-dom/client';
import * as DjangoBridge from '@django-bridge/react';

import HTMLPageView from './views/HTMLPage';

const config = new DjangoBridge.Config();

config.addView('HTMLPage', HTMLPageView);

const rootElement = document.getElementById('root')!;
const initialResponse = JSON.parse(
  document.getElementById('initial-response')!.textContent!,
);

ReactDOM.createRoot(rootElement).render(
  <React.StrictMode>
    <DjangoBridge.App config={config} initialResponse={initialResponse} />
  </React.StrictMode>,
);
