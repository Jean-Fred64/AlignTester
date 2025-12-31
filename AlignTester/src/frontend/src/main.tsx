import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App.tsx'
import './index.css'
import { TranslationProvider } from './i18n/useTranslation'

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <TranslationProvider>
      <App />
    </TranslationProvider>
  </React.StrictMode>,
)

