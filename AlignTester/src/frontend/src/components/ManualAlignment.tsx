import { useState, useEffect, useCallback, useRef } from 'react';
import axios from 'axios';
import { useWebSocket } from '../hooks/useWebSocket';
import { useTranslation } from '../i18n/useTranslation';

interface ManualAlignmentProps {
  alignAvailable: boolean;
  selectedFormat?: string;
  onFormatChange?: (format: string) => void;
  onStateChange?: (state: ManualAlignmentState | null) => void;
  onLiveReadingsChange?: (readings: LiveReading[]) => void;
  currentPosition?: { track: number; head: number };
}

interface AlignmentModeConfig {
  reads: number;
  delay_ms: number;
  timeout: number;
  estimated_latency_ms: number;
}

interface ManualAlignmentState {
  is_running: boolean;
  current_track: number;
  current_head: number;
  auto_analyze: boolean;
  num_reads: number;
  format_type: string;
  diskdefs_path: string | null;
  alignment_mode?: string;  // "direct", "fine_tune", "high_precision"
  alignment_mode_config?: AlignmentModeConfig;
  last_reading: ManualReading | null;
  total_readings: number;
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

interface ManualReading {
  track: number;
  head: number;
  percentage: number;
  sectors_detected: number;
  sectors_expected: number;
  quality: string;
  calculation_details?: {
    scores_raw?: {
      sector?: number;
      quality?: number;
      azimuth?: number;
      asymmetry?: number;
    };
    scores_penalized?: {
      sector?: number;
      quality?: number;
      azimuth?: number;
      asymmetry?: number;
    };
    weights?: {
      sector?: number;
      quality?: number;
      azimuth?: number;
      asymmetry?: number;
    };
    confidence_factors?: {
      sector?: number;
      quality?: number;
      azimuth?: number;
      asymmetry?: number;
    };
    num_readings?: number;
    has_quality?: boolean;
    has_azimuth?: boolean;
    has_asymmetry?: boolean;
  };
  indicator: {
    percentage: number;
    quality: string;
    distance_from_ideal?: number;
    direction?: string;
    bars: string;
    status: string;
    sectors_ratio: string;
    recommendation?: string;
    // Propriétés pour Mode Direct
    symbol?: string;
    color?: string;
    message?: string;
  };
}

interface ReadingTiming {
  elapsed_ms: number;
  timestamp: string;
  flux_transitions?: number;
  time_per_rev_ms?: number;
}

interface LiveReading {
  reading_number: number;
  track: number;
  head: number;
  sectors_detected: number;
  sectors_expected: number;
  percentage: number;
  timing?: ReadingTiming;
  timestamp: number;  // Timestamp JS pour calculer la latence
}

export function ManualAlignment({ alignAvailable, selectedFormat: propSelectedFormat, onFormatChange, onStateChange, onLiveReadingsChange, currentPosition }: ManualAlignmentProps) {
  const [state, setState] = useState<ManualAlignmentState | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [isReading, setIsReading] = useState(false);
  const [analyzing, setAnalyzing] = useState(false);
  const [formats, setFormats] = useState<DiskFormat[]>([]);
  // Utiliser le format passé en prop ou un état local
  const [localFormat, setLocalFormat] = useState<string>(propSelectedFormat || "ibm.1440");
  const selectedFormat = propSelectedFormat || localFormat;
  // Historique des lectures en temps réel (pour affichage des timings)
  const [liveReadings, setLiveReadings] = useState<LiveReading[]>([]);
  // Ref pour éviter les dépendances dans les callbacks et optimiser les performances
  const readingCounterRef = useRef(0);
  
  // Transmettre les lectures en temps réel au parent
  useEffect(() => {
    if (onLiveReadingsChange) {
      onLiveReadingsChange(liveReadings);
    }
  }, [liveReadings, onLiveReadingsChange]);
  
  // Synchroniser avec le format passé en prop
  useEffect(() => {
    if (propSelectedFormat && propSelectedFormat !== localFormat) {
      setLocalFormat(propSelectedFormat);
    }
  }, [propSelectedFormat, localFormat]);
  const { lastMessage } = useWebSocket('ws://localhost:8000/ws');
  const { t } = useTranslation();

  const fetchState = useCallback(async () => {
    try {
      const response = await axios.get<ManualAlignmentState>('http://localhost:8000/api/manual/state');
      setState(response.data);
      if (onStateChange) {
        onStateChange(response.data);
      }
    } catch (err) {
      console.error('Error fetching manual state:', err);
    }
  }, [onStateChange]);

  useEffect(() => {
    fetchState();
    const interval = setInterval(fetchState, 1000);
    return () => clearInterval(interval);
  }, [fetchState]);

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

  // Synchroniser le format sélectionné avec l'état du backend
  useEffect(() => {
    if (state?.format_type && state.format_type !== selectedFormat) {
      // Le backend a un format différent, le synchroniser avec le format partagé
      if (onFormatChange) {
        onFormatChange(state.format_type);
      }
      setLocalFormat(state.format_type);
    }
  }, [state?.format_type, selectedFormat, onFormatChange]);
  
  // Synchroniser le format partagé avec le backend quand le format partagé change
  // Utiliser un debounce pour éviter les appels multiples
  useEffect(() => {
    if (!propSelectedFormat) return;
    
    // Mettre à jour le format local immédiatement
    if (propSelectedFormat !== localFormat) {
      setLocalFormat(propSelectedFormat);
    }
    
    // Si le format partagé est différent du format du backend, synchroniser avec le backend
    if (state && propSelectedFormat !== state.format_type) {
      // Attendre un peu pour éviter les appels multiples lors du changement d'onglet
      const timeoutId = setTimeout(() => {
        // Vérifier à nouveau avant d'appeler (éviter les appels obsolètes)
        if (propSelectedFormat !== state.format_type) {
          handleFormatChange(propSelectedFormat).catch(err => {
            console.error('Error synchronizing format:', err);
          });
        }
      }, 300); // Debounce de 300ms pour laisser le temps au backend de répondre
      
      return () => clearTimeout(timeoutId);
    }
  }, [propSelectedFormat]); // Ne dépendre que de propSelectedFormat pour éviter les boucles

  // Écouter les messages WebSocket pour les mises à jour en temps réel
  useEffect(() => {
    // Écouter aussi les messages de reset global
    if (lastMessage && lastMessage.type === 'alignment_reset') {
      // Réinitialiser les données affichées
      fetchState();
    }
    
    if (lastMessage && lastMessage.type === 'manual_alignment_update') {
      const data = lastMessage.data;
      
      if (data.type === 'started' || data.type === 'seek' || data.type === 'recalibrated' || data.type === 'format_changed') {
        if (data.state && Object.keys(data.state).length > 0) {
          setState(prevState => {
            // Fusionner avec l'état précédent pour éviter de perdre des données
            const newState = prevState ? { ...prevState, ...data.state } : data.state;
            if (onStateChange) {
              onStateChange(newState);
            }
            return newState;
          });
          // Synchroniser le format si changé
          if (data.type === 'format_changed' && data.format_type && onFormatChange) {
            onFormatChange(data.format_type);
          }
        }
      } else if (data.type === 'data_reset') {
        // Réinitialiser les données affichées
        if (data.state && Object.keys(data.state).length > 0) {
          setState(prevState => {
            const newState = prevState ? { ...prevState, ...data.state } : data.state;
            if (onStateChange) {
              onStateChange(newState);
            }
            return newState;
          });
        }
      } else if (data.type === 'mode_changed') {
        // Mode d'alignement changé
        // Réinitialiser l'état de lecture lors du changement de mode pour éviter le blocage
        setIsReading(false);
        setAnalyzing(false);
        
        if (data.state && Object.keys(data.state).length > 0) {
          setState(prevState => {
            const newState = prevState ? { ...prevState, ...data.state } : data.state;
            if (onStateChange) {
              onStateChange(newState);
            }
            return newState;
          });
        }
      } else if (data.type === 'direct_reading_complete') {
        // Mode Direct ACTIVÉ - Notification unique après lecture complète (problème de saturation résolu)
        // ✅ Amélioration : Un seul message par lecture (au lieu de 2-10+ messages)
        setIsReading(false);
        
        // Traiter la lecture complète pour le mode Direct
        if (data.reading && data.state?.alignment_mode === 'direct') {
          // Mettre à jour l'état avec la dernière lecture
          if (data.state && Object.keys(data.state).length > 0) {
            setState(prevState => {
              const newState = prevState ? { ...prevState, ...data.state } : data.state;
              if (onStateChange) {
                onStateChange(newState);
              }
              return newState;
            });
          }
        } else if (data.state && Object.keys(data.state).length > 0) {
          // Mettre à jour l'état même si pas de reading (pour compatibilité)
          setState(prevState => {
            const newState = prevState ? { ...prevState, ...data.state } : data.state;
            if (onStateChange) {
              onStateChange(newState);
            }
            return newState;
          });
        }
      } else if (data.type === 'direct_reading') {
        // ⚠️ Ce type ne devrait plus être utilisé (amélioration appliquée)
        // Garder pour compatibilité avec anciennes versions, mais ignorer silencieusement
        console.debug('[ManualAlignment] Message direct_reading ignoré (devrait être direct_reading_complete)');
      } else if (data.type === 'reading') {
        // Lecture en cours (flux continu - autres modes : Ajustage Fin, Grande Précision)
        setIsReading(true);
        
        // Ajouter à l'historique des lectures en temps réel pour les autres modes
        if (state?.alignment_mode && state.alignment_mode !== 'direct') {
          const now = Date.now();
          readingCounterRef.current += 1;
          const newCounter = readingCounterRef.current;
          
          // Extraire les données depuis parsed ou reading
          const parsed = data.parsed || {};
          const reading = data.reading || {};
          
          setLiveReadings(prevReadings => {
            const newReading: LiveReading = {
              reading_number: newCounter,
              track: parsed.track || reading.track || state?.current_track || 0,
              head: reading.head || state?.current_head || 0,
              sectors_detected: parsed.sectors_detected || reading.sectors_detected || 0,
              sectors_expected: parsed.sectors_expected || reading.sectors_expected || 18,
              percentage: parsed.percentage || reading.percentage || 0,
              timing: data.timing,
              timestamp: now
            };
            
            // Garder seulement les 20 dernières lectures pour l'affichage
            return [...prevReadings, newReading].slice(-20);
          });
        }
        
        if (data.state && Object.keys(data.state).length > 0) {
          setState(prevState => {
            const newState = prevState ? { ...prevState, ...data.state } : data.state;
            if (onStateChange) {
              onStateChange(newState);
            }
            return newState;
          });
        }
      } else if (data.type === 'reading_complete') {
        // Lecture terminée (le flux continue)
        setIsReading(false);
        
        // Mettre à jour la dernière lecture avec les timings complets et les données de reading
        if (state?.alignment_mode && state.alignment_mode !== 'direct') {
          setLiveReadings(prevReadings => {
            if (prevReadings.length > 0) {
              const updated = [...prevReadings];
              const lastReading = updated[updated.length - 1];
              updated[updated.length - 1] = {
                ...lastReading,
                // Mettre à jour avec les données complètes de reading_complete
                track: data.reading?.track || lastReading.track,
                head: data.reading?.head || lastReading.head,
                sectors_detected: data.reading?.sectors_detected || lastReading.sectors_detected,
                sectors_expected: data.reading?.sectors_expected || lastReading.sectors_expected,
                percentage: data.reading?.percentage || lastReading.percentage,
                timing: data.timing || lastReading.timing
              };
              return updated;
            }
            return prevReadings;
          });
        }
        
        if (data.state && Object.keys(data.state).length > 0) {
          setState(prevState => {
            const newState = prevState ? { ...prevState, ...data.state } : data.state;
            if (onStateChange) {
              onStateChange(newState);
            }
            return newState;
          });
        }
      } else if (data.type === 'reading_error') {
        // Erreur lors d'une lecture (le flux continue)
        setIsReading(false);
        if (data.state && Object.keys(data.state).length > 0) {
          setState(prevState => {
            const newState = prevState ? { ...prevState, ...data.state } : data.state;
            if (onStateChange) {
              onStateChange(newState);
            }
            return newState;
          });
        }
      } else if (data.type === 'analysis_reading' || data.type === 'analysis_complete') {
        // Analyse en cours (bouton Analyser)
        if (data.type === 'analysis_reading') {
          setAnalyzing(true);
        } else {
          setAnalyzing(false);
        }
        if (data.state && Object.keys(data.state).length > 0) {
          setState(prevState => {
            const newState = prevState ? { ...prevState, ...data.state } : data.state;
            if (onStateChange) {
              onStateChange(newState);
            }
            return newState;
          });
        }
      } else if (data.type === 'stopped') {
        setIsReading(false);
        setAnalyzing(false);
        // Ne pas réinitialiser l'historique à l'arrêt, garder pour analyse
        if (data.state && Object.keys(data.state).length > 0) {
          setState(prevState => {
            const newState = prevState ? { ...prevState, ...data.state } : data.state;
            if (onStateChange) {
              onStateChange(newState);
            }
            return newState;
          });
        }
      } else if (data.type === 'started') {
        // Réinitialiser l'historique au démarrage
        setLiveReadings([]);
        readingCounterRef.current = 0; // Réinitialiser aussi la ref
        setIsReading(false); // Réinitialiser aussi l'état de lecture
        if (data.state && Object.keys(data.state).length > 0) {
          setState(prevState => {
            // Fusionner avec l'état précédent pour éviter de perdre des données
            const newState = prevState ? { ...prevState, ...data.state } : data.state;
            if (onStateChange) {
              onStateChange(newState);
            }
            return newState;
          });
        }
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
      await axios.post('http://localhost:8000/api/manual/start', {
        initial_track: 0,
        initial_head: 0
      });
      await fetchState();
    } catch (err: any) {
      setError(err.response?.data?.detail || t('errorStartingManualMode'));
    } finally {
      setLoading(false);
    }
  };

  const handleStop = async () => {
    try {
      // Réinitialiser immédiatement les états de lecture pour éviter le blocage de l'interface
      setIsReading(false);
      setAnalyzing(false);
      
      await axios.post('http://localhost:8000/api/manual/stop');
      await fetchState();
    } catch (err: any) {
      setError(err.response?.data?.detail || t('errorStoppingManualMode'));
      // En cas d'erreur, réinitialiser quand même les états pour permettre de réessayer
      setIsReading(false);
      setAnalyzing(false);
    }
  };

  const handleMove = useCallback(async (delta: number) => {
    try {
      await axios.post('http://localhost:8000/api/manual/move', { delta });
      await fetchState();
    } catch (err: any) {
      setError(err.response?.data?.detail || t('errorMovingTrack'));
    }
  }, [fetchState, t]);

  const handleJump = useCallback(async (trackNumber: number) => {
    try {
      await axios.post('http://localhost:8000/api/manual/jump', { track_number: trackNumber });
      await fetchState();
    } catch (err: any) {
      setError(err.response?.data?.detail || t('errorJumpingTrack'));
    }
  }, [fetchState, t]);

  const handleHead = useCallback(async (head: number) => {
    try {
      await axios.post('http://localhost:8000/api/manual/head', { head });
      await fetchState();
    } catch (err: any) {
      setError(err.response?.data?.detail || t('errorChangingHead'));
    }
  }, [fetchState, t]);

  const handleRecal = useCallback(async () => {
    try {
      if (state?.is_running) {
        // Si le mode est démarré, utiliser l'endpoint recal
        await axios.post('http://localhost:8000/api/manual/recal');
      } else {
        // Si le mode n'est pas démarré, utiliser seek directement vers track 0
        await axios.post('http://localhost:8000/api/manual/seek', {
          track: 0,
          head: 0
        });
      }
      await fetchState();
    } catch (err: any) {
      setError(err.response?.data?.detail || t('errorRecalibrating'));
    }
  }, [fetchState, t, state]);

  const handleAnalyze = useCallback(async () => {
    if (!alignAvailable) {
      setError(t('alignCommandNotAvailable') || "La commande align n'est pas disponible");
      return;
    }
    
    try {
      setAnalyzing(true);
      setError(null);
      
      // Mettre à jour le format avant d'analyser
      try {
        await axios.post('http://localhost:8000/api/manual/settings', {
          format_type: selectedFormat
        });
      } catch (settingsErr: any) {
        // Si la mise à jour du format échoue, continuer quand même
        console.warn('Error updating format:', settingsErr);
      }
      
      // Lancer l'analyse (avec un body vide pour que FastAPI accepte)
      const response = await axios.post('http://localhost:8000/api/manual/analyze', {});
      
      // Rafraîchir l'état pour voir les résultats
      await fetchState();
      
      // Afficher un message de succès si disponible
      if (response.data && response.data.reading) {
        console.log('Analysis completed:', response.data.reading);
      }
    } catch (err: any) {
      const errorMsg = err.response?.data?.detail || err.message || t('errorAnalyzing');
      const errorData = err.response?.data;
      
      // Afficher les détails de l'erreur si disponibles
      let fullErrorMsg = errorMsg;
      if (errorData) {
        if (errorData.raw_output) {
          fullErrorMsg += `\n\nSortie brute:\n${errorData.raw_output}`;
        }
        if (errorData.command) {
          fullErrorMsg += `\n\nCommande exécutée: ${errorData.command}`;
        }
        if (errorData.hint) {
          fullErrorMsg += `\n\n💡 ${errorData.hint}`;
        }
      }
      
      setError(fullErrorMsg);
      console.error('Error analyzing track:', err);
      console.error('Full error details:', errorData);
    } finally {
      setAnalyzing(false);
    }
  }, [selectedFormat, fetchState, t, alignAvailable]);

  const handleFormatChange = useCallback(async (format: string) => {
    setLocalFormat(format);
    // Notifier le parent du changement
    if (onFormatChange) {
      onFormatChange(format);
    }
    try {
      // Mettre à jour le format dans les settings
      await axios.post('http://localhost:8000/api/manual/settings', {
        format_type: format
      });
      // Rafraîchir l'état pour s'assurer que le format est bien mis à jour
      await fetchState();
      // Le flux continu de lecture utilisera automatiquement le nouveau format
      // car il lit self.state.format_type à chaque itération
    } catch (err: any) {
      setError(err.response?.data?.detail || t('errorChangingFormat'));
      // En cas d'erreur, restaurer l'ancien format
      if (state?.format_type) {
        setLocalFormat(state.format_type);
        if (onFormatChange) {
          onFormatChange(state.format_type);
        }
      }
    }
  }, [fetchState, state?.format_type, onFormatChange]);

  const handleModeChange = useCallback(async (mode: string) => {
    try {
      // Réinitialiser l'état de lecture lors du changement de mode pour éviter le blocage
      setIsReading(false);
      setAnalyzing(false);
      
      await axios.post('http://localhost:8000/api/manual/settings', {
        alignment_mode: mode
      });
      await fetchState();
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Erreur lors du changement de mode');
      // En cas d'erreur, réinitialiser quand même l'état pour permettre de réessayer
      setIsReading(false);
      setAnalyzing(false);
    }
  }, [fetchState]);

  // Refs pour les handlers (évite les dépendances circulaires)
  const handlersRef = useRef({ handleMove, handleJump, handleHead, handleRecal, handleAnalyze });
  handlersRef.current = { handleMove, handleJump, handleHead, handleRecal, handleAnalyze };

  // Stocker les handlers de démarrage/arrêt dans une ref pour éviter les problèmes de dépendances
  const startStopRef = useRef({ handleStart, handleStop });
  startStopRef.current = { handleStart, handleStop };

  // Gestion des touches clavier
  useEffect(() => {
    const handleKeyPress = async (e: KeyboardEvent) => {
      // Ignorer si on est dans un input ou select
      const target = e.target as HTMLElement;
      if (target.tagName === 'INPUT' || target.tagName === 'SELECT' || target.tagName === 'TEXTAREA') return;

      // Touche Espace : démarrer/arrêter le mode manuel
      if (e.key === ' ' || e.key === 'Spacebar') {
        e.preventDefault();
        if (state?.is_running) {
          await startStopRef.current.handleStop();
        } else {
          await startStopRef.current.handleStart();
        }
        return;
      }

      // Les touches de navigation fonctionnent même si le mode n'est pas démarré
      const handlers = handlersRef.current;
      switch (e.key) {
        case '+':
        case '=':
          e.preventDefault();
          await handlers.handleMove(1);
          break;
        case '-':
        case '_':
          e.preventDefault();
          await handlers.handleMove(-1);
          break;
        case '1':
        case '2':
        case '3':
        case '4':
        case '5':
        case '6':
        case '7':
        case '8':
          e.preventDefault();
          await handlers.handleJump(parseInt(e.key));
          break;
        case 'h':
        case 'H':
          e.preventDefault();
          // Head nécessite que le mode soit démarré
          if (state?.is_running && state) {
            await handlers.handleHead(state.current_head === 0 ? 1 : 0);
          }
          break;
        case 'r':
        case 'R':
          e.preventDefault();
          await handlers.handleRecal();
          break;
        case 'a':
        case 'A':
          e.preventDefault();
          await handlers.handleAnalyze();
          break;
      }
    };

    window.addEventListener('keydown', handleKeyPress);
    return () => window.removeEventListener('keydown', handleKeyPress);
  }, [state?.is_running]);


  return (
    <div className="bg-gray-800 rounded-lg p-4">
      <h2 className="text-xl font-semibold mb-3">{t('manualAlignmentMode')}</h2>

      {error && (
        <div className="bg-red-900 border border-red-700 text-red-200 px-3 py-2 rounded mb-3 text-sm">
          <div className="flex items-start gap-2">
            <svg className="w-5 h-5 text-red-400 flex-shrink-0 mt-0.5" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
            </svg>
            <div className="flex-1">
              <p className="font-semibold mb-2">{t('errorAnalyzing')}</p>
              <pre className="text-xs whitespace-pre-wrap break-words bg-red-950/50 p-2 rounded mt-2 overflow-auto max-h-96">
                {error}
              </pre>
            </div>
            <button
              onClick={() => setError(null)}
              className="text-red-400 hover:text-red-300 flex-shrink-0"
              title={t('close')}
            >
              <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clipRule="evenodd" />
              </svg>
            </button>
          </div>
        </div>
      )}

      <div className="grid md:grid-cols-2 gap-2 mb-2">
    {/* Sélection du format - Toujours visible pour permettre la configuration */}
    <div className="bg-gray-700 rounded-lg p-2">
      <h3 className="text-sm font-semibold mb-1">{t('diskFormat')}</h3>
      <div className="space-y-2">
        <div>
          <label className="block text-sm text-gray-400 mb-2">
            {t('format')}
          </label>
          <select
            value={selectedFormat}
            onChange={(e) => handleFormatChange(e.target.value)}
            disabled={analyzing || isReading}
            className="w-full bg-gray-800 text-white px-4 py-2 rounded focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-50"
          >
            {formats.length > 0 ? (
              formats.map((fmt) => {
                // Afficher le nom avec capacité si disponible
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
            ) : (
              <>
                <option value="ibm.1440">IBM 1.44MB (80 cyls, 2 heads)</option>
                <option value="ibm.1200">IBM 1.2MB (80 cyls, 2 heads)</option>
                <option value="ibm.720">IBM 720KB (80 cyls, 2 heads)</option>
                <option value="ibm.360">IBM 360KB (40 cyls, 2 heads)</option>
              </>
            )}
          </select>
        </div>
        
        {/* Détails du format sélectionné - Affichage compact */}
        {(() => {
          try {
            const selectedFormatData = formats.find(f => f.name === selectedFormat);
            if (!selectedFormatData) return null;
            
            const formatDetails = [];
            if (selectedFormatData.cyls) formatDetails.push({ label: t('tracks'), value: selectedFormatData.cyls });
            if (selectedFormatData.heads) formatDetails.push({ label: t('heads'), value: selectedFormatData.heads });
            if (selectedFormatData.secs) formatDetails.push({ label: t('sectorsPerTrack'), value: selectedFormatData.secs });
            if (selectedFormatData.bps) formatDetails.push({ label: t('bytesPerSector'), value: selectedFormatData.bps });
            if (selectedFormatData.rate) {
              try {
                const rateValue = parseInt(selectedFormatData.rate);
                if (!isNaN(rateValue)) {
                  let rateLabel = `${selectedFormatData.rate} kbps`;
                  if (rateValue === 250) rateLabel += ' (DD)';
                  else if (rateValue === 500) rateLabel += ' (HD)';
                  else if (rateValue === 1000) rateLabel += ' (ED)';
                  formatDetails.push({ label: t('dataRate'), value: rateLabel });
                }
              } catch (e) {
                // Ignorer les erreurs de parsing
              }
            }
            if (selectedFormatData.track_format) {
              try {
                // Convertir le format en nom lisible
                let formatType = selectedFormatData.track_format;
                
                // Vérifier que formatType est une string avant d'utiliser .includes()
                if (typeof formatType === 'string') {
                  // Formats IBM
                  if (formatType === 'ibm.mfm' || formatType.includes('ibm.mfm')) formatType = 'MFM (IBM)';
                  else if (formatType === 'ibm.fm' || formatType.includes('ibm.fm')) formatType = 'FM (IBM)';
                  else if (formatType === 'ibm.scan' || formatType.includes('ibm.scan')) formatType = 'Scan (IBM)';
                  
                  // Formats Apple II
                  else if (formatType === 'apple2.gcr' || formatType.includes('apple2.gcr')) formatType = 'GCR (Apple II)';
                  
                  // Formats Commodore
                  else if (formatType === 'c64.gcr' || formatType.includes('c64.gcr')) formatType = 'GCR (Commodore)';
                  
                  // Formats Amiga
                  else if (formatType === 'amiga.amigados' || formatType.includes('amiga.amigados')) formatType = 'AmigaDOS';
                  
                  // Formats Mac
                  else if (formatType.includes('mac.gcr')) formatType = 'GCR (Mac)';
                  
                  // Formats HP
                  else if (formatType.includes('hp.mmfm')) formatType = 'MMFM (HP)';
                  
                  // Formats DEC
                  else if (formatType.includes('dec.rx02')) formatType = 'RX02 (DEC)';
                  
                  // Formats spécifiques
                  else if (formatType === 'micropolis') formatType = 'Micropolis';
                  else if (formatType === 'northstar') formatType = 'Northstar';
                  else if (formatType === 'datageneral') formatType = 'Data General';
                  else if (formatType === 'bitcell') formatType = 'Bitcell (Raw)';
                  
                  // Autres formats GCR
                  else if (formatType.includes('.gcr')) formatType = 'GCR';
                  
                  // Autres formats MFM/FM
                  else if (formatType.includes('mfm')) formatType = 'MFM';
                  else if (formatType.includes('fm')) formatType = 'FM';
                }
                
                formatDetails.push({ label: t('trackFormat'), value: formatType });
              } catch (e) {
                // Ignorer les erreurs de conversion de format
                console.error('Error converting format:', e);
              }
            }
            
            if (formatDetails.length === 0) return null;
            
            return (
              <div className="bg-gray-800 rounded p-3 border border-gray-600">
                <div className="text-xs text-gray-400 mb-2">{t('formatDetails')}</div>
                <div className="grid grid-cols-2 gap-2 text-xs">
                  {formatDetails.map((detail, idx) => (
                    <div key={idx} className="flex justify-between">
                      <span className="text-gray-500">{detail.label}:</span>
                      <span className="text-gray-300 font-mono">{detail.value}</span>
                    </div>
                  ))}
                </div>
              </div>
            );
          } catch (error) {
            // En cas d'erreur, ne rien afficher pour ne pas bloquer le rendu
            console.error('Error displaying format details:', error);
            return null;
          }
        })()}
        
        <div className="text-xs text-gray-400">
          {t('selectFormatTip')}
        </div>
      </div>
    </div>

    {/* Sélection du mode d'alignement */}
    <div className="bg-gray-700 rounded-lg p-2">
      <h3 className="text-sm font-semibold mb-1">{t('manualAlignmentMode')}</h3>
      <div className="space-y-1">
          <div>
            <label className="block text-sm text-gray-400 mb-2">
              Mode actif
            </label>
            <div className="grid grid-cols-1 gap-2">
              {/* Mode Direct - ACTIVÉ (problème de performance résolu) */}
              <button
                onClick={() => handleModeChange('direct')}
                disabled={analyzing || isReading}
                className={`flex items-center justify-between p-2 rounded border-2 transition-all ${
                  state?.alignment_mode === 'direct'
                    ? 'border-blue-500 bg-blue-900/30'
                    : 'border-gray-600 bg-gray-800 hover:border-gray-500'
                } ${analyzing || isReading ? 'opacity-50 cursor-not-allowed' : ''}`}
                title="Mode Direct - Latence minimale (~150-200ms), précision basique. Optimisé pour le réglage en temps réel."
              >
                <div className="flex items-center gap-2">
                  <span className="text-lg">⚡</span>
                  <div className="text-left">
                    <div className={`font-semibold text-sm ${
                      state?.alignment_mode === 'direct' ? 'text-blue-300' : 'text-gray-300'
                    }`}>Mode Direct</div>
                    <div className="text-xs text-gray-400">Réglage rapide</div>
                  </div>
                </div>
                <div className="text-right">
                  <div className={`text-xs font-mono ${
                    state?.alignment_mode === 'direct' ? 'text-blue-300' : 'text-gray-400'
                  }`}>
                    ~150-200ms
                  </div>
                  <div className="text-xs text-gray-400">{t('latency')}</div>
                </div>
              </button>

              {/* Mode Ajustage Fin */}
              <button
                onClick={() => handleModeChange('fine_tune')}
                disabled={analyzing || isReading}
                className={`flex items-center justify-between p-2 rounded border-2 transition-all ${
                  state?.alignment_mode === 'fine_tune'
                    ? 'border-blue-500 bg-blue-900/30'
                    : 'border-gray-600 bg-gray-800 hover:border-gray-500'
                } disabled:opacity-50 disabled:cursor-not-allowed`}
              >
                <div className="flex items-center gap-2">
                  <span className="text-lg">🎯</span>
                  <div className="text-left">
                    <div className="font-semibold text-white text-sm">{t('fineTuneMode')}</div>
                    <div className="text-xs text-gray-400">{t('fineTuneDescription')}</div>
                  </div>
                </div>
                <div className="text-right">
                  <div className="text-xs font-mono text-blue-400">
                    ~500-700ms
                  </div>
                  <div className="text-xs text-gray-500">{t('latency')}</div>
                </div>
              </button>

              {/* Mode Grande Précision */}
              <button
                onClick={() => handleModeChange('high_precision')}
                disabled={analyzing || isReading}
                className={`flex items-center justify-between p-2 rounded border-2 transition-all ${
                  state?.alignment_mode === 'high_precision'
                    ? 'border-blue-500 bg-blue-900/30'
                    : 'border-gray-600 bg-gray-800 hover:border-gray-500'
                } disabled:opacity-50 disabled:cursor-not-allowed`}
              >
                <div className="flex items-center gap-2">
                  <span className="text-lg">🔬</span>
                  <div className="text-left">
                    <div className="font-semibold text-white text-sm">{t('highPrecisionMode')}</div>
                    <div className="text-xs text-gray-400">{t('highPrecisionDescription')}</div>
                  </div>
                </div>
                <div className="text-right">
                  <div className="text-xs font-mono text-blue-400">
                    ~2-3s
                  </div>
                  <div className="text-xs text-gray-500">{t('perTrack')}</div>
                </div>
              </button>
            </div>
          </div>

          {/* Informations du mode actif */}
          {state?.alignment_mode_config && (
            <div className="bg-gray-800 rounded p-2 border border-gray-600">
              <div className="text-xs text-gray-400 mb-1">{t('activeModeConfiguration')}</div>
              <div className="grid grid-cols-2 gap-1 text-xs">
                <div className="flex justify-between">
                  <span className="text-gray-500">{t('reads')}</span>
                  <span className="text-gray-300 font-mono">{state.alignment_mode_config.reads}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-500">{t('delay')}</span>
                  <span className="text-gray-300 font-mono">{state.alignment_mode_config.delay_ms}ms</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-500">{t('timeout')}</span>
                  <span className="text-gray-300 font-mono">{state.alignment_mode_config.timeout}s</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-500">{t('estimatedLatency')}</span>
                  <span className="text-blue-400 font-mono font-semibold">
                    {state.alignment_mode_config.estimated_latency_ms}ms
                  </span>
                </div>
              </div>
            </div>
          )}

          <div className="text-xs text-gray-400">
            {t('directModeTip')}
          </div>
        </div>
      </div>
    </div>

    {/* Affichage en temps réel pour le Mode Direct - Simple et efficace - Version compacte */}
    {state && state.is_running && state.alignment_mode === 'direct' && (
      <div className="bg-gray-700 rounded-lg p-2 mb-2 border-2 border-blue-500">
        <div className="flex items-center justify-between mb-2">
          <h3 className="text-sm font-semibold text-blue-400">
            ⚡ Mode Direct
          </h3>
          <div className="flex items-center gap-2">
            <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse"></div>
            <span className="text-xs text-gray-400">Actif</span>
          </div>
        </div>
        
        {state.last_reading ? (
          <>
            {/* Dernière lecture - Affichage principal compact */}
            <div className="bg-blue-900/30 border-2 border-blue-500 rounded-lg p-2">
              <div className="flex items-center justify-between mb-2">
                <div className="flex items-center gap-3">
                  <div>
                    <div className="text-xs text-gray-400">{t('track')}</div>
                    <div className="text-base font-bold text-white">
                      T{state.last_reading.track}.{state.last_reading.head}
                    </div>
                  </div>
                  <div>
                    <div className="text-xs text-gray-400">{t('sectors')}</div>
                    <div className="text-sm font-mono text-white">
                      {state.last_reading.sectors_detected}/{state.last_reading.sectors_expected}
                    </div>
                  </div>
                </div>
                <div className="text-right">
                  <div className="text-xs text-gray-400">{t('percentage').replace(':', '')}</div>
                  <div className={`text-3xl font-bold ${
                    state.last_reading.percentage >= 99 ? 'text-green-400' :
                    state.last_reading.percentage >= 95 ? 'text-blue-400' :
                    state.last_reading.percentage >= 90 ? 'text-yellow-400' :
                    'text-red-400'
                  }`}>
                    {state.last_reading.percentage.toFixed(1)}%
                  </div>
                </div>
              </div>
              
              {/* Indicateur visuel et qualité - Ligne compacte */}
              <div className="flex items-center justify-between pt-2 border-t border-blue-600">
                {state.last_reading.indicator && state.last_reading.indicator.bars && (
                  <div className="flex items-center gap-2 flex-1">
                    <div className="font-mono text-sm text-blue-300">
                      {state.last_reading.indicator.bars}
                    </div>
                    {state.last_reading.indicator.symbol && (
                      <div className={`text-lg ${
                        state.last_reading.indicator.color === 'green' ? 'text-green-400' :
                        state.last_reading.indicator.color === 'blue' ? 'text-blue-400' :
                        state.last_reading.indicator.color === 'yellow' ? 'text-yellow-400' :
                        'text-red-400'
                      }`}>
                        {state.last_reading.indicator.symbol}
                      </div>
                    )}
                  </div>
                )}
                <span className={`text-xs font-semibold ${
                  state.last_reading.quality === 'PERFECT' || state.last_reading.quality === 'Perfect' ? 'text-green-400' :
                  state.last_reading.quality === 'GOOD' || state.last_reading.quality === 'Good' ? 'text-blue-400' :
                  state.last_reading.quality === 'AVERAGE' || state.last_reading.quality === 'Average' ? 'text-yellow-400' :
                  'text-red-400'
                }`}>
                  {state.last_reading.quality}
                </span>
              </div>
              
              {/* Détails du calcul multi-critères */}
              {state.last_reading.calculation_details && (
                <div className="mt-3 pt-3 border-t border-blue-600">
                  <div className="text-xs font-semibold mb-2 text-blue-300">{t('calculationDetails')}</div>
                  
                  {state.last_reading.calculation_details.scores_raw && (
                    <div className="mb-2">
                      <div className="text-xs font-semibold mb-1 text-gray-400">{t('scoresRaw')}:</div>
                      <div className="grid grid-cols-4 gap-2 text-xs">
                        <div><span className="text-gray-500">{t('sector')}:</span> {state.last_reading.calculation_details.scores_raw.sector?.toFixed(2)}%</div>
                        <div><span className="text-gray-500">{t('quality')}:</span> {state.last_reading.calculation_details.scores_raw.quality?.toFixed(2)}%</div>
                        <div><span className="text-gray-500">{t('azimuth')}:</span> {state.last_reading.calculation_details.scores_raw.azimuth?.toFixed(2)}%</div>
                        <div><span className="text-gray-500">{t('asymmetry')}:</span> {state.last_reading.calculation_details.scores_raw.asymmetry?.toFixed(2)}%</div>
                      </div>
                    </div>
                  )}
                  
                  {state.last_reading.calculation_details.scores_penalized && (
                    <div className="mb-2">
                      <div className="text-xs font-semibold mb-1 text-gray-400">{t('scoresPenalized')}:</div>
                      <div className="grid grid-cols-4 gap-2 text-xs">
                        <div><span className="text-gray-500">{t('sector')}:</span> {state.last_reading.calculation_details.scores_penalized.sector?.toFixed(2)}%</div>
                        <div><span className="text-gray-500">{t('quality')}:</span> {state.last_reading.calculation_details.scores_penalized.quality?.toFixed(2)}%</div>
                        <div><span className="text-gray-500">{t('azimuth')}:</span> {state.last_reading.calculation_details.scores_penalized.azimuth?.toFixed(2)}%</div>
                        <div><span className="text-gray-500">{t('asymmetry')}:</span> {state.last_reading.calculation_details.scores_penalized.asymmetry?.toFixed(2)}%</div>
                      </div>
                    </div>
                  )}
                  
                  {state.last_reading.calculation_details.weights && (
                    <div className="mb-2">
                      <div className="text-xs font-semibold mb-1 text-gray-400">{t('weights')}:</div>
                      <div className="grid grid-cols-4 gap-2 text-xs">
                        <div><span className="text-gray-500">{t('sector')}:</span> {(state.last_reading.calculation_details.weights.sector! * 100).toFixed(1)}%</div>
                        <div><span className="text-gray-500">{t('quality')}:</span> {(state.last_reading.calculation_details.weights.quality! * 100).toFixed(1)}%</div>
                        <div><span className="text-gray-500">{t('azimuth')}:</span> {(state.last_reading.calculation_details.weights.azimuth! * 100).toFixed(1)}%</div>
                        <div><span className="text-gray-500">{t('asymmetry')}:</span> {(state.last_reading.calculation_details.weights.asymmetry! * 100).toFixed(1)}%</div>
                      </div>
                    </div>
                  )}
                  
                  {state.last_reading.calculation_details.confidence_factors && (
                    <div className="mb-2">
                      <div className="text-xs font-semibold mb-1 text-gray-400">{t('confidenceFactors')}:</div>
                      <div className="grid grid-cols-4 gap-2 text-xs">
                        <div><span className="text-gray-500">{t('sector')}:</span> {(state.last_reading.calculation_details.confidence_factors.sector! * 100).toFixed(1)}%</div>
                        <div><span className="text-gray-500">{t('quality')}:</span> {(state.last_reading.calculation_details.confidence_factors.quality! * 100).toFixed(1)}%</div>
                        <div><span className="text-gray-500">{t('azimuth')}:</span> {(state.last_reading.calculation_details.confidence_factors.azimuth! * 100).toFixed(1)}%</div>
                        <div><span className="text-gray-500">{t('asymmetry')}:</span> {(state.last_reading.calculation_details.confidence_factors.asymmetry! * 100).toFixed(1)}%</div>
                      </div>
                    </div>
                  )}
                  
                  {state.last_reading.calculation_details.num_readings !== undefined && (
                    <div className="text-xs text-gray-400">
                      {t('numReadings')}: {state.last_reading.calculation_details.num_readings}
                    </div>
                  )}
                </div>
              )}
            </div>
          </>
        ) : (
          /* En attente de la première lecture - Version compacte */
          <div className="bg-blue-900/30 border-2 border-blue-500 rounded-lg p-3 text-center">
            <div className="animate-pulse text-blue-400 text-sm">
              En attente... T{state.current_track}.{state.current_head}
            </div>
          </div>
        )}
      </div>
    )}

    {/* Affichage en temps réel des timings (Ajustage Fin et Grande Précision uniquement) - Placé juste après Mode d'Alignement */}
    {/* Pas de timings en mode Direct - affichage simplifié uniquement */}
    {state && state.is_running && state.alignment_mode && state.alignment_mode !== 'direct' && (
        <div className="bg-gray-700 rounded-lg p-3 mb-3 border-2 border-blue-500">
              <div className="flex items-center justify-between mb-2">
                <h3 className="text-base font-semibold text-blue-400">
                  📊 {t('timings')} ({state.alignment_mode === 'fine_tune' ? t('fineTuneMode') : t('highPrecisionMode')})
                </h3>
            <div className="flex items-center gap-2">
              <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse"></div>
              <span className="text-xs text-gray-400">
                {liveReadings.length} {liveReadings.length > 1 ? t('readingsCount') : t('readingCount')}
              </span>
            </div>
          </div>
          
          {/* Dernière lecture - Affichage simplifié et visible */}
          {liveReadings.length > 0 ? (() => {
            const lastReading = liveReadings[liveReadings.length - 1];
            const prevReading = liveReadings.length > 1 ? liveReadings[liveReadings.length - 2] : null;
            const latency = prevReading ? lastReading.timestamp - prevReading.timestamp : null;
            
            return (
              <div className="bg-blue-900/30 border-2 border-blue-500 rounded-lg p-3 mb-3">
                <div className="flex items-center justify-between mb-2">
                  <div className="flex items-center gap-2">
                    <span className="text-lg font-bold text-blue-400">#{lastReading.reading_number}</span>
                    <div>
                      <div className="text-xs text-gray-400">{t('track')}</div>
                      <div className="text-base font-bold text-white">
                        T{lastReading.track}.{lastReading.head}
                      </div>
                    </div>
                    <div>
                      <div className="text-xs text-gray-400">{t('sectors')}</div>
                      <div className="text-sm font-mono text-white">
                        {lastReading.sectors_detected}/{lastReading.sectors_expected}
                      </div>
                    </div>
                  </div>
                  <div className="text-right">
                    <div className="text-xs text-gray-400 mb-0.5">{t('percentage').replace(':', '')}</div>
                    <div className={`text-2xl font-bold ${
                      lastReading.percentage >= 99 ? 'text-green-400' :
                      lastReading.percentage >= 97 ? 'text-blue-400' :
                      lastReading.percentage >= 95 ? 'text-yellow-400' :
                      'text-red-400'
                    }`}>
                      {lastReading.percentage.toFixed(1)}%
                    </div>
                  </div>
                </div>
                
                <div className="grid grid-cols-2 gap-2 pt-2 border-t border-blue-600">
                  <div>
                    <div className="text-xs text-gray-400 mb-0.5">{t('duration')}</div>
                    <div className="text-sm font-mono font-bold text-blue-400">
                      {lastReading.timing && lastReading.timing.elapsed_ms !== undefined 
                        ? `${lastReading.timing.elapsed_ms.toFixed(0)}ms`
                        : '...'}
                    </div>
                  </div>
                  {latency !== null ? (
                    <div>
                      <div className="text-xs text-gray-400 mb-0.5">{t('latency')}</div>
                      <div className={`text-sm font-mono font-bold ${
                        latency < 200 ? 'text-green-400' :
                        latency < 300 ? 'text-blue-400' :
                        latency < 500 ? 'text-yellow-400' :
                        'text-red-400'
                      }`}>
                        {latency.toFixed(0)}ms
                      </div>
                    </div>
                  ) : (
                    <div>
                      <div className="text-xs text-gray-400 mb-0.5">{t('latency')}</div>
                      <div className="text-sm font-mono text-gray-500">...</div>
                    </div>
                  )}
                  {/* Flux transitions - Toujours affiché en mode Fine Tune et High Precision */}
                  <div 
                    className="cursor-help"
                    title="Nombre de transitions magnétiques détectées lors de la lecture. Indique la densité de données sur la piste. Plus il y a de transitions, plus la piste contient de données. Valeur typique: ~200 000-250 000 pour une piste formatée."
                  >
                    <div className="text-xs text-gray-400 mb-0.5">{t('fluxTransitions')}</div>
                    <div className="text-xs font-mono text-blue-300">
                      {lastReading.timing && lastReading.timing.flux_transitions !== undefined && lastReading.timing.flux_transitions !== null
                        ? lastReading.timing.flux_transitions.toLocaleString()
                        : <span className="text-gray-500">N/A</span>}
                    </div>
                  </div>
                  {/* Temps/révolution - Toujours affiché en mode Fine Tune et High Precision */}
                  <div
                    className="cursor-help"
                    title="Temps pour une révolution complète de la disquette. Indique la vitesse de rotation du disque. Valeurs typiques: ~200ms (300 RPM) ou ~167ms (360 RPM). Si cette valeur varie beaucoup entre lectures, cela peut indiquer un problème mécanique."
                  >
                    <div className="text-xs text-gray-400 mb-0.5">{t('tempsPerRev')}</div>
                    <div className="text-xs font-mono text-blue-300">
                      {lastReading.timing && lastReading.timing.time_per_rev_ms !== undefined && lastReading.timing.time_per_rev_ms !== null
                        ? `${lastReading.timing.time_per_rev_ms.toFixed(1)}ms`
                        : <span className="text-gray-500">N/A</span>}
                    </div>
                  </div>
                </div>
                
                {/* Détails du calcul multi-critères pour les modes Fine Tune et High Precision */}
                {state.last_reading && state.last_reading.calculation_details && (
                  <div className="mt-3 pt-3 border-t border-blue-600">
                    <div className="text-xs font-semibold mb-2 text-blue-300">{t('calculationDetails')}</div>
                    
                    {state.last_reading.calculation_details.scores_raw && (
                      <div className="mb-2">
                        <div className="text-xs font-semibold mb-1 text-gray-400">{t('scoresRaw')}:</div>
                        <div className="grid grid-cols-4 gap-2 text-xs">
                          <div><span className="text-gray-500">{t('sector')}:</span> {state.last_reading.calculation_details.scores_raw.sector?.toFixed(2)}%</div>
                          <div><span className="text-gray-500">{t('quality')}:</span> {state.last_reading.calculation_details.scores_raw.quality?.toFixed(2)}%</div>
                          <div><span className="text-gray-500">{t('azimuth')}:</span> {state.last_reading.calculation_details.scores_raw.azimuth?.toFixed(2)}%</div>
                          <div><span className="text-gray-500">{t('asymmetry')}:</span> {state.last_reading.calculation_details.scores_raw.asymmetry?.toFixed(2)}%</div>
                        </div>
                      </div>
                    )}
                    
                    {state.last_reading.calculation_details.scores_penalized && (
                      <div className="mb-2">
                        <div className="text-xs font-semibold mb-1 text-gray-400">{t('scoresPenalized')}:</div>
                        <div className="grid grid-cols-4 gap-2 text-xs">
                          <div><span className="text-gray-500">{t('sector')}:</span> {state.last_reading.calculation_details.scores_penalized.sector?.toFixed(2)}%</div>
                          <div><span className="text-gray-500">{t('quality')}:</span> {state.last_reading.calculation_details.scores_penalized.quality?.toFixed(2)}%</div>
                          <div><span className="text-gray-500">{t('azimuth')}:</span> {state.last_reading.calculation_details.scores_penalized.azimuth?.toFixed(2)}%</div>
                          <div><span className="text-gray-500">{t('asymmetry')}:</span> {state.last_reading.calculation_details.scores_penalized.asymmetry?.toFixed(2)}%</div>
                        </div>
                      </div>
                    )}
                    
                    {state.last_reading.calculation_details.weights && (
                      <div className="mb-2">
                        <div className="text-xs font-semibold mb-1 text-gray-400">{t('weights')}:</div>
                        <div className="grid grid-cols-4 gap-2 text-xs">
                          <div><span className="text-gray-500">{t('sector')}:</span> {(state.last_reading.calculation_details.weights.sector! * 100).toFixed(1)}%</div>
                          <div><span className="text-gray-500">{t('quality')}:</span> {(state.last_reading.calculation_details.weights.quality! * 100).toFixed(1)}%</div>
                          <div><span className="text-gray-500">{t('azimuth')}:</span> {(state.last_reading.calculation_details.weights.azimuth! * 100).toFixed(1)}%</div>
                          <div><span className="text-gray-500">{t('asymmetry')}:</span> {(state.last_reading.calculation_details.weights.asymmetry! * 100).toFixed(1)}%</div>
                        </div>
                      </div>
                    )}
                    
                    {state.last_reading.calculation_details.confidence_factors && (
                      <div className="mb-2">
                        <div className="text-xs font-semibold mb-1 text-gray-400">{t('confidenceFactors')}:</div>
                        <div className="grid grid-cols-4 gap-2 text-xs">
                          <div><span className="text-gray-500">{t('sector')}:</span> {(state.last_reading.calculation_details.confidence_factors.sector! * 100).toFixed(1)}%</div>
                          <div><span className="text-gray-500">{t('quality')}:</span> {(state.last_reading.calculation_details.confidence_factors.quality! * 100).toFixed(1)}%</div>
                          <div><span className="text-gray-500">{t('azimuth')}:</span> {(state.last_reading.calculation_details.confidence_factors.azimuth! * 100).toFixed(1)}%</div>
                          <div><span className="text-gray-500">{t('asymmetry')}:</span> {(state.last_reading.calculation_details.confidence_factors.asymmetry! * 100).toFixed(1)}%</div>
                        </div>
                      </div>
                    )}
                    
                    {state.last_reading.calculation_details.num_readings !== undefined && (
                      <div className="text-xs text-gray-400">
                        {t('numReadings')}: {state.last_reading.calculation_details.num_readings}
                      </div>
                    )}
                  </div>
                )}
              </div>
            );
          })() : (
            <div className="bg-gray-800 rounded p-4 text-center text-gray-400">
              <div className="animate-pulse">{t('waitingForFirstReading')}</div>
            </div>
          )}
          
          {/* Historique des dernières lectures */}
          {liveReadings.length > 1 && (
            <div className="space-y-1 max-h-48 overflow-y-auto">
              <div className="text-xs text-gray-400 mb-1">Historique ({Math.min(liveReadings.length, 10)} dernières)</div>
              {liveReadings.slice(-10).reverse().map((reading, idx) => {
                const nextIdx = idx + 1;
                const nextReading = nextIdx < Math.min(liveReadings.length, 10) 
                  ? liveReadings[Math.min(liveReadings.length, 10) - 1 - nextIdx] 
                  : null;
                const latency = nextReading ? nextReading.timestamp - reading.timestamp : null;
                
                return (
                  <div 
                    key={reading.reading_number} 
                    className="bg-gray-800 rounded p-1.5 border border-gray-600 text-xs"
                  >
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-1.5">
                        <span className="font-mono text-gray-500 text-xs">#{reading.reading_number}</span>
                        <span className="text-white text-xs">T{reading.track}.{reading.head}</span>
                        <span className="text-gray-400 text-xs">
                          {reading.sectors_detected}/{reading.sectors_expected}
                        </span>
                        <span className={`font-bold text-xs ${
                          reading.percentage >= 99 ? 'text-green-400' :
                          reading.percentage >= 97 ? 'text-blue-400' :
                          reading.percentage >= 95 ? 'text-yellow-400' :
                          'text-red-400'
                        }`}>
                          {reading.percentage.toFixed(1)}%
                        </span>
                      </div>
                      <div className="flex items-center gap-2 text-gray-400">
                        {reading.timing && reading.timing.elapsed_ms !== undefined && (
                          <span className="font-mono text-blue-400 text-xs">
                            {reading.timing.elapsed_ms.toFixed(0)}ms
                          </span>
                        )}
                        {latency !== null && (
                          <span className={`font-mono text-xs ${
                            latency < 200 ? 'text-green-400' :
                            latency < 300 ? 'text-blue-400' :
                            'text-yellow-400'
                          }`}>
                            +{latency.toFixed(0)}ms
                          </span>
                        )}
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          )}
          
          {/* Statistiques des timings */}
          {liveReadings.length > 1 && (
            <div className="mt-2 pt-2 border-t border-gray-600">
              <div className="grid grid-cols-3 gap-2 text-xs">
                {(() => {
                  const timings = liveReadings
                    .filter(r => r.timing && r.timing.elapsed_ms !== undefined)
                    .map(r => r.timing!.elapsed_ms);
                  const latencies = liveReadings
                    .slice(1)
                    .map((r, i) => r.timestamp - liveReadings[i].timestamp);
                  
                  const avgTiming = timings.length > 0 
                    ? timings.reduce((a, b) => a + b, 0) / timings.length 
                    : 0;
                  const avgLatency = latencies.length > 0
                    ? latencies.reduce((a, b) => a + b, 0) / latencies.length
                    : 0;
                  
                  return (
                    <>
                      <div>
                        <span className="text-gray-500">{t('averageDuration')}</span>{' '}
                        <span className="text-blue-400 font-mono font-semibold">
                          {avgTiming.toFixed(1)}ms
                        </span>
                      </div>
                      <div>
                        <span className="text-gray-500">{t('averageLatency')}</span>{' '}
                        <span className="text-green-400 font-mono font-semibold">
                          {avgLatency.toFixed(1)}ms
                        </span>
                      </div>
                      <div>
                        <span className="text-gray-500">{t('reads')}</span>{' '}
                        <span className="text-gray-300 font-mono font-semibold">
                          {liveReadings.length}
                        </span>
                      </div>
                    </>
                  );
                })()}
              </div>
            </div>
          )}
        </div>
      )}

      {/* Bouton Analyse - TOUJOURS ACCESSIBLE */}
      <div className="bg-gray-700 rounded-lg p-2 mb-2 border-2 border-green-600/30">
        <div className="flex items-center justify-between mb-1">
          <h3 className="text-sm font-semibold text-green-400">{t('analyze')}</h3>
          {analyzing && (
            <div className="flex items-center gap-2 text-green-400">
              <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-green-400"></div>
              <span className="text-sm">{t('analyzing')}</span>
            </div>
          )}
        </div>
        
        {/* Format sélectionné */}
        <div className="mb-1 text-xs text-gray-300">
          {t('analyzeUsesFormat')}: <strong className="text-white">{selectedFormat}</strong>
        </div>
        
        <div className="space-y-1">
          <button
            onClick={handleAnalyze}
            disabled={analyzing || !alignAvailable}
            className="w-full bg-green-600 hover:bg-green-500 text-white font-semibold py-1.5 px-3 rounded disabled:opacity-50 disabled:cursor-not-allowed transition-all relative group text-sm"
            title={!alignAvailable ? t('alignCommandNotAvailable') : t('analyze')}
          >
            {analyzing ? (
              <span className="flex items-center justify-center gap-2">
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                {t('analyzing')}
              </span>
            ) : (
              <span>
                {t('analyze')}{' '}
                {state?.is_running 
                  ? `(T${state.current_track ?? 0}.${state.current_head ?? 0})`
                  : currentPosition
                  ? `(T${currentPosition.track}.${currentPosition.head})`
                  : '(T0.0)'}
              </span>
            )}
            {/* Tooltip avec explication détaillée */}
            <div className="absolute bottom-full left-0 mb-2 w-80 p-3 bg-gray-800 text-white text-xs rounded shadow-lg opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none z-50 border border-gray-700">
              <div className="font-semibold mb-2">{t('analyzeWhatItDoes')}</div>
              <ul className="space-y-1 list-disc list-inside text-gray-300">
                <li>
                  {t('analyzeReadsTrack')}{' '}
                  {state?.is_running 
                    ? `${t('currentTrack')} (T${state.current_track ?? 0}.${state.current_head ?? 0})`
                    : currentPosition
                    ? `${t('currentTrack')} (T${currentPosition.track}.${currentPosition.head})`
                    : t('defaultTrack')}{' '}
                  {t('analyzeSeveralTimes')}
                </li>
                <li>{t('analyzeCalculatesAlignment')}</li>
                <li>{t('analyzeDetectsFormatting')}</li>
                <li>{t('analyzeChecksLimits')}</li>
                <li>{t('analyzeCalculatesConsistency')}</li>
              </ul>
            </div>
          </button>
          
          {!alignAvailable && (
            <div className="bg-red-900/30 border border-red-700 rounded p-2">
              <p className="text-xs text-red-400">
                ⚠️ {t('alignCommandNotAvailable')}
              </p>
            </div>
          )}
          
          
          {alignAvailable && state?.is_running && (
            <div className="bg-blue-900/30 border border-blue-700 rounded p-1.5">
              <p className="text-xs text-blue-400">
                ✅ {t('manualModeActive')} <strong>T{state.current_track ?? 0}.{state.current_head ?? 0}</strong> {t('withFormat')} <strong>{selectedFormat}</strong>
              </p>
            </div>
          )}
        </div>
      </div>

      {(!state || (!state.is_running && !state.last_reading)) ? (
        <div className="space-y-4">
          <p className="text-gray-400">
            {t('manualModeDescription')}
          </p>
          <button
            onClick={handleStart}
            disabled={!alignAvailable || loading}
            className="w-full bg-blue-600 hover:bg-blue-700 text-white font-semibold py-2 px-4 rounded disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {loading ? t('startingManualMode') : t('startManualMode')}
          </button>
        </div>
      ) : (
        <div className="space-y-6">
          {/* Message d'arrêt si le mode est arrêté mais qu'il y a des données */}
          {state && !state.is_running && state.last_reading && (
            <div className="bg-yellow-900/30 border border-yellow-700 rounded-lg p-4">
              <div className="flex items-center gap-2 text-yellow-400">
                <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
                </svg>
                <span className="font-semibold">{t('manualModeStopped')}</span>
              </div>
              <p className="text-yellow-300/80 text-sm mt-2">
                {t('manualModeStoppedInfo')}
              </p>
            </div>
          )}



          {/* Bouton d'arrêt ou de démarrage */}
          {state?.is_running ? (
            <button
              onClick={handleStop}
              className="w-full bg-red-600 hover:bg-red-700 text-white font-semibold py-2 px-4 rounded"
            >
              {t('stopManualMode')}
            </button>
          ) : state && state.last_reading ? (
            <button
              onClick={handleStart}
              disabled={!alignAvailable || loading}
              className="w-full bg-blue-600 hover:bg-blue-700 text-white font-semibold py-2 px-4 rounded disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {loading ? t('startingManualMode') : t('restartManualMode')}
            </button>
          ) : null}

        </div>
      )}
    </div>
  );
}

