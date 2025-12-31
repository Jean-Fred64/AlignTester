import { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import { useWebSocket } from '../hooks/useWebSocket';
import { useTranslation } from '../i18n/useTranslation';

interface AlignmentControlProps {
  alignAvailable: boolean;
  onAlignmentStart: () => void;
  selectedFormat?: string;
  onFormatChange?: (format: string) => void;
}

interface AlignmentStatus {
  status: string;
  cylinders: number;
  retries: number;
  current_cylinder?: number;
  progress_percentage: number;
  values_count: number;
  statistics?: any;
  error_message?: string;
}

interface DiskFormat {
  name: string;
  display_name: string;
  cyls: string | null;
  heads: string | null;
  secs?: string | null;
  bps?: string | null;
  gap3?: string | null;
  rate?: string | null;
  rpm?: string | null;
  track_format?: string | null;
  capacity_kb?: number | null;
}

export function AlignmentControl({ alignAvailable, onAlignmentStart, selectedFormat: propSelectedFormat, onFormatChange }: AlignmentControlProps) {
  const [cylinders, setCylinders] = useState(80);
  const [retries, setRetries] = useState(3);
  // Utiliser le format passé en prop ou un état local
  const [localFormat, setLocalFormat] = useState<string>(propSelectedFormat || "ibm.1440");
  const selectedFormat = propSelectedFormat || localFormat;
  const [formats, setFormats] = useState<DiskFormat[]>([]);
  
  // Synchroniser avec le format passé en prop
  useEffect(() => {
    if (propSelectedFormat && propSelectedFormat !== localFormat) {
      setLocalFormat(propSelectedFormat);
    }
  }, [propSelectedFormat]);
  
  const handleFormatChange = (format: string) => {
    setLocalFormat(format);
    if (onFormatChange) {
      onFormatChange(format);
    }
  };
  const [status, setStatus] = useState<AlignmentStatus | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const { lastMessage } = useWebSocket('ws://localhost:8000/ws');
  const { t } = useTranslation();

  const fetchStatus = async () => {
    try {
      const response = await axios.get<AlignmentStatus>('http://localhost:8000/api/status');
      setStatus(response.data);
    } catch (err) {
      console.error('Error fetching status:', err);
    }
  };

  useEffect(() => {
    fetchStatus();
    const interval = setInterval(fetchStatus, 1000); // Rafraîchir toutes les secondes
    return () => clearInterval(interval);
  }, []);

  // Charger les formats disponibles
  useEffect(() => {
    const fetchFormats = async () => {
      try {
        const response = await axios.get<{success: boolean, formats: DiskFormat[]}>('http://localhost:8000/api/manual/formats');
        if (response.data.success) {
          setFormats(response.data.formats);
        }
      } catch (err) {
        console.error('Error fetching formats:', err);
      }
    };
    fetchFormats();
  }, []);

  // Écouter les messages WebSocket pour les mises à jour en temps réel
  useEffect(() => {
    if (lastMessage) {
      if (lastMessage.type === 'alignment_started') {
        fetchStatus();
      } else if (lastMessage.type === 'alignment_complete' || lastMessage.type === 'alignment_cancelled' || lastMessage.type === 'alignment_error') {
        fetchStatus();
      }
    }
  }, [lastMessage]);

  const handleStart = async () => {
    if (!alignAvailable) {
      setError(t('alignCommandNotAvailable'));
      return;
    }

    try {
      setLoading(true);
      setError(null);
      await axios.post('http://localhost:8000/api/align', {
        cylinders,
        retries,
        format_type: selectedFormat
      });
      onAlignmentStart();
      await fetchStatus();
    } catch (err: any) {
      setError(err.response?.data?.detail || t('errorStartingAlignment'));
    } finally {
      setLoading(false);
    }
  };

  const handleCancel = async () => {
    try {
      await axios.post('http://localhost:8000/api/align/cancel');
      await fetchStatus();
    } catch (err: any) {
      setError(err.response?.data?.detail || t('errorCancelling'));
    }
  };

  const isRunning = status?.status === 'running';

  // Stocker les handlers dans une ref pour éviter les problèmes de dépendances
  const handlersRef = useRef({ handleStart, handleCancel });
  handlersRef.current = { handleStart, handleCancel };

  // Gestion de la touche Espace pour démarrer/arrêter
  useEffect(() => {
    const handleKeyPress = async (e: KeyboardEvent) => {
      // Ignorer si on est dans un input ou select
      const target = e.target as HTMLElement;
      if (target.tagName === 'INPUT' || target.tagName === 'SELECT' || target.tagName === 'TEXTAREA') return;

      // Touche Espace : démarrer/arrêter l'alignement automatique
      if (e.key === ' ' || e.key === 'Spacebar') {
        e.preventDefault();
        if (isRunning) {
          handlersRef.current.handleCancel();
        } else {
          handlersRef.current.handleStart();
        }
      }
    };

    window.addEventListener('keydown', handleKeyPress);
    return () => window.removeEventListener('keydown', handleKeyPress);
  }, [isRunning]);

  return (
    <div className="bg-gray-800 rounded-lg p-4">
      <h2 className="text-xl font-semibold mb-3">{t('alignmentTest')}</h2>

      {error && (
        <div className="bg-red-900 border border-red-700 text-red-200 px-3 py-2 rounded mb-3 text-sm">
          <p>{error}</p>
        </div>
      )}

      {status && status.status === 'running' && (
        <div className="bg-blue-900 border border-blue-700 text-blue-200 px-3 py-2 rounded mb-3 text-sm">
          <p className="font-bold mb-1">{t('alignmentInProgress')}</p>
          <div className="mb-2">
            <div className="flex justify-between text-sm mb-1">
              <span>{t('progress')}</span>
              <span>{status.progress_percentage.toFixed(1)}%</span>
            </div>
            <div className="w-full bg-gray-700 rounded-full h-2.5">
              <div 
                className="bg-blue-500 h-2.5 rounded-full transition-all duration-300"
                style={{ width: `${Math.min(status.progress_percentage, 100)}%` }}
              ></div>
            </div>
          </div>
          <div className="grid grid-cols-2 gap-2 text-sm mt-3">
            <div>
              <span className="text-gray-400">{t('valuesCollected')}</span>
              <span className="ml-2 font-semibold">{status.values_count}</span>
            </div>
            {status.current_cylinder !== null && status.current_cylinder !== undefined && (
              <div>
                <span className="text-gray-400">{t('currentCylinder')}</span>
                <span className="ml-2 font-semibold">{status.current_cylinder}</span>
              </div>
            )}
          </div>
        </div>
      )}

      {status && status.status === 'completed' && status.statistics && (
        <div className="bg-green-900 border border-green-700 text-green-200 px-3 py-2 rounded mb-3 text-sm">
          <p className="font-bold mb-1">{t('alignmentCompleted')}</p>
          <div className="grid grid-cols-2 gap-2 text-sm">
            <div>
              <span className="text-gray-400">{t('average')}</span>
              <span className="ml-2 font-semibold">{status.statistics.average}%</span>
            </div>
            <div>
              <span className="text-gray-400">{t('quality')}</span>
              <span className={`ml-2 font-semibold ${
                status.statistics.quality === 'Perfect' ? 'text-green-300' :
                status.statistics.quality === 'Good' ? 'text-blue-300' :
                status.statistics.quality === 'Average' ? 'text-yellow-300' :
                'text-red-300'
              }`}>
                {status.statistics.quality}
              </span>
            </div>
          </div>
        </div>
      )}

      {status && status.status === 'error' && status.error_message && (
        <div className="bg-red-900 border border-red-700 text-red-200 px-3 py-2 rounded mb-3 text-sm">
          <p className="font-bold">{t('error')}</p>
          <p>{status.error_message}</p>
        </div>
      )}

      {status && status.status === 'cancelled' && (
        <div className="bg-yellow-900 border border-yellow-700 text-yellow-200 px-3 py-2 rounded mb-3 text-sm">
          <p className="font-bold">{t('alignmentCancelled')}</p>
        </div>
      )}

      <div className="space-y-3">
        <div className="grid md:grid-cols-3 gap-3">
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-1">
              {t('diskFormat')}
            </label>
            <select
              value={selectedFormat}
              onChange={(e) => handleFormatChange(e.target.value)}
              disabled={isRunning || loading}
              className="w-full bg-gray-700 text-white px-4 py-2 rounded focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-50"
            >
              {formats.length === 0 ? (
                <option value="ibm.1440">IBM 1440 (1.44 MB) - {t('loadingFormats')}</option>
              ) : (
                formats.map((fmt) => {
                  // Afficher le nom avec capacité si disponible (même logique que mode manuel)
                  let display = fmt.display_name;
                  if (fmt.capacity_kb) {
                    const capacity = fmt.capacity_kb >= 1024 
                      ? `${(fmt.capacity_kb / 1024).toFixed(1)}MB`
                      : `${fmt.capacity_kb}KB`;
                    display += ` (${capacity})`;
                  } else if (fmt.cyls && fmt.heads) {
                    display += ` (${fmt.cyls} cyls, ${fmt.heads} heads)`;
                  }
                  return (
                    <option key={fmt.name} value={fmt.name}>
                      {display}
                    </option>
                  );
                })
              )}
            </select>
            <p className="text-xs text-gray-400 mt-1">
              {t('selectFormatTip')}
            </p>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">
              {t('numberOfCylinders')}
            </label>
            <input
              type="number"
              min="1"
              max="160"
              value={cylinders}
              onChange={(e) => setCylinders(parseInt(e.target.value) || 80)}
              disabled={isRunning || loading}
              className="w-full bg-gray-700 text-white px-4 py-2 rounded focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-50"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">
              {t('numberOfRetries')}
            </label>
            <input
              type="number"
              min="1"
              max="10"
              value={retries}
              onChange={(e) => setRetries(parseInt(e.target.value) || 3)}
              disabled={isRunning || loading}
              className="w-full bg-gray-700 text-white px-4 py-2 rounded focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-50"
            />
          </div>
        </div>

        <div className="space-y-4">
          <div className="flex gap-4">
            {!isRunning ? (
              <button
                onClick={handleStart}
                disabled={!alignAvailable || loading}
                className="flex-1 bg-blue-600 hover:bg-blue-700 text-white font-semibold py-2 px-4 rounded disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {loading ? t('starting') : t('startAlignment')}
              </button>
            ) : (
              <button
                onClick={handleCancel}
                className="flex-1 bg-red-600 hover:bg-red-700 text-white font-semibold py-2 px-4 rounded"
              >
                {t('cancelAlignment')}
              </button>
            )}
          </div>
          
          {/* Aide clavier */}
          <div className="bg-gray-700 rounded-lg p-2">
            <div className="text-xs text-gray-400 space-y-0.5">
              <div><kbd className="bg-gray-800 px-2 py-1 rounded">Espace</kbd> : {t('startStopShortcut')}</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

