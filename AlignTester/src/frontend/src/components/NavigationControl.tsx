import { useState, useCallback } from 'react';
import axios from 'axios';
import { useTranslation } from '../i18n/useTranslation';

interface NavigationControlProps {
  alignAvailable: boolean;
  manualState: any;
  currentPosition: { track: number; head: number };
  onPositionChange?: (position: { track: number; head: number }) => void;
  onStateChange?: () => void;
}

export function NavigationControl({ alignAvailable, manualState, currentPosition, onPositionChange, onStateChange }: NavigationControlProps) {
  const [isReading, setIsReading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const { t } = useTranslation();

  const fetchState = useCallback(async () => {
    try {
      await axios.get('http://localhost:8000/api/manual/state');
      if (onStateChange) {
        onStateChange();
      }
    } catch (err) {
      console.error('Error fetching manual state:', err);
    }
  }, [onStateChange]);

  const handleMove = useCallback(async (delta: number) => {
    try {
      setError(null);
      setIsReading(true);
      // Si le mode n'est pas démarré, utiliser seek directement avec la position calculée
      if (!manualState?.is_running) {
        const newTrack = Math.max(0, Math.min(83, currentPosition.track + delta));
        await axios.post('http://localhost:8000/api/manual/seek', {
          track: newTrack,
          head: currentPosition.head
        });
      } else {
        await axios.post('http://localhost:8000/api/manual/move', { delta });
      }
      await fetchState();
      // La position sera mise à jour via fetchState qui récupère l'état du backend
    } catch (err: any) {
      setError(err.response?.data?.detail || t('errorMovingTrack'));
    } finally {
      setIsReading(false);
    }
  }, [fetchState, t, manualState, currentPosition]);

  const handleJump = useCallback(async (trackNumber: number) => {
    try {
      setError(null);
      setIsReading(true);
      // Si le mode n'est pas démarré, utiliser seek directement avec la position calculée
      if (!manualState?.is_running) {
        const newTrack = trackNumber * 10;
        await axios.post('http://localhost:8000/api/manual/seek', {
          track: newTrack,
          head: currentPosition.head
        });
      } else {
        await axios.post('http://localhost:8000/api/manual/jump', { track_number: trackNumber });
      }
      await fetchState();
      // La position sera mise à jour via fetchState qui récupère l'état du backend
    } catch (err: any) {
      setError(err.response?.data?.detail || t('errorJumpingTrack'));
    } finally {
      setIsReading(false);
    }
  }, [fetchState, t, manualState, currentPosition]);

  const handleHead = useCallback(async (head: number) => {
    try {
      setError(null);
      setIsReading(true);
      if (manualState?.is_running) {
        await axios.post('http://localhost:8000/api/manual/head', { head });
      } else {
        // Si le mode n'est pas démarré, utiliser seek directement
        await axios.post('http://localhost:8000/api/manual/seek', { 
          track: currentPosition.track, 
          head: head 
        });
      }
      await fetchState();
      // La position sera mise à jour via fetchState qui récupère l'état du backend
    } catch (err: any) {
      setError(err.response?.data?.detail || t('errorChangingHead'));
    } finally {
      setIsReading(false);
    }
  }, [fetchState, t, manualState, currentPosition]);

  const handleRecal = useCallback(async () => {
    try {
      setError(null);
      setIsReading(true);
      if (manualState?.is_running) {
        // Si le mode est démarré, utiliser l'endpoint recal
        await axios.post('http://localhost:8000/api/manual/recal');
      } else {
        // Si le mode n'est pas démarré, utiliser seek directement vers track 0
        await axios.post('http://localhost:8000/api/manual/seek', {
          track: 0,
          head: 0
        });
        // Mettre à jour la position localement
        if (onPositionChange) {
          onPositionChange({ track: 0, head: 0 });
        }
      }
      await fetchState();
    } catch (err: any) {
      setError(err.response?.data?.detail || t('errorRecalibrating'));
    } finally {
      setIsReading(false);
    }
  }, [fetchState, t, manualState, onPositionChange]);

  return (
    <div className="bg-gray-800 rounded-lg p-2">
      <div className="flex items-center justify-between mb-1">
        <h3 className="text-sm font-semibold">{t('navigation')}</h3>
        {isReading && (
          <div className="flex items-center gap-2 text-blue-400">
            <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-400"></div>
            <span className="text-xs">{t('reading')}</span>
          </div>
        )}
      </div>

      {error && (
        <div className="bg-red-900/30 border border-red-700 rounded p-2 mb-2">
          <p className="text-xs text-red-400">{error}</p>
        </div>
      )}

      <div className="space-y-2">
        {/* Boutons +/- */}
        <div className="flex gap-2">
          <button
            onClick={() => handleMove(-5)}
            disabled={isReading || !alignAvailable}
            className="flex-1 bg-gray-600 hover:bg-gray-500 text-white font-semibold py-1.5 px-3 rounded text-sm disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            title={t('moveBackFiveTracks')}
          >
            ← -5
          </button>
          <button
            onClick={() => handleMove(-1)}
            disabled={isReading || !alignAvailable}
            className="flex-1 bg-gray-600 hover:bg-gray-500 text-white font-semibold py-1.5 px-3 rounded text-sm disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            title={t('moveBackOneTrack')}
          >
            ← -1
          </button>
          <button
            onClick={() => handleMove(1)}
            disabled={isReading || !alignAvailable}
            className="flex-1 bg-gray-600 hover:bg-gray-500 text-white font-semibold py-1.5 px-3 rounded text-sm disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            title={t('moveForwardOneTrack')}
          >
            +1 →
          </button>
          <button
            onClick={() => handleMove(5)}
            disabled={isReading || !alignAvailable}
            className="flex-1 bg-gray-600 hover:bg-gray-500 text-white font-semibold py-1.5 px-3 rounded text-sm disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            title={t('moveForwardFiveTracks')}
          >
            +5 →
          </button>
        </div>

        {/* Boutons de saut rapide */}
        <div>
          <label className="block text-xs text-gray-400 mb-1">{t('quickJump')}</label>
          <div className="grid grid-cols-4 gap-1.5">
            {[1, 2, 3, 4, 5, 6, 7, 8].map((num) => (
              <button
                key={num}
                onClick={() => handleJump(num)}
                disabled={isReading || !alignAvailable}
                className="bg-gray-600 hover:bg-gray-500 text-white font-semibold py-1.5 px-2 rounded text-xs disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                title={`${t('goToTrack')} ${num * 10}`}
              >
                {num * 10}
              </button>
            ))}
          </div>
        </div>

        {/* Contrôles spéciaux */}
        <div className="flex gap-2 pt-2 border-t border-gray-600">
          <button
            onClick={() => handleHead((manualState?.current_head ?? currentPosition.head) === 0 ? 1 : 0)}
            disabled={isReading || !alignAvailable}
            className="flex-1 bg-purple-600 hover:bg-purple-500 text-white font-semibold py-1.5 px-3 rounded text-sm disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            title={t('changeHead')}
          >
            {t('head')} {(manualState?.current_head ?? currentPosition.head) === 0 ? '1' : '0'} (H)
          </button>
          <button
            onClick={handleRecal}
            disabled={isReading || !alignAvailable}
            className="flex-1 bg-orange-600 hover:bg-orange-500 text-white font-semibold py-1.5 px-3 rounded text-sm disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            title={t('recalibrateTooltip')}
          >
            {t('recalibrate')} (R)
          </button>
        </div>

      </div>
    </div>
  );
}

