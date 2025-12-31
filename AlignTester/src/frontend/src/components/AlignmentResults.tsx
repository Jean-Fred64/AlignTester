import { useEffect, useState } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, BarChart, Bar } from 'recharts';
import { useWebSocket } from '../hooks/useWebSocket';
import axios from 'axios';
import { useTranslation } from '../i18n/useTranslation';

interface AlignmentValue {
  track: string;
  percentage: number;
  base?: number;
  bands?: number[];
  sectors_detected?: number;
  sectors_expected?: number;
  flux_transitions?: number;
  time_per_rev?: number;
  format_type?: string;
  consistency?: number;
  stability?: number;
  positioning_status?: string;
  azimuth_score?: number;
  azimuth_status?: string;
  azimuth_cv?: number;
  asymmetry_score?: number;
  asymmetry_status?: string;
  asymmetry_percent?: number;
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
  line_number?: number;
}

interface AlignmentResultsProps {
  status: string;
}

interface AlignmentStatus {
  status: string;
  statistics?: any;
}

export function AlignmentResults({ status }: AlignmentResultsProps) {
  const [values, setValues] = useState<AlignmentValue[]>([]);
  const [statistics, setStatistics] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);
  const { lastMessage } = useWebSocket('ws://localhost:8000/ws');
  const { t } = useTranslation();
  
  // Récupérer les statistiques depuis l'API si disponibles
  useEffect(() => {
    const fetchStatistics = async () => {
      try {
        const response = await axios.get<AlignmentStatus>('http://localhost:8000/api/status');
        if (response.data.statistics) {
          setStatistics(response.data.statistics);
        }
      } catch (err) {
        // Ignorer les erreurs silencieusement
        console.error('Error fetching statistics:', err);
      }
    };
    
    if (status === 'completed') {
      fetchStatistics();
    }
  }, [status]);

  useEffect(() => {
    try {
      if (lastMessage) {
        if (lastMessage.type === 'alignment_reset') {
          // Réinitialiser les données affichées
          setValues([]);
          setStatistics(null);
          setError(null);
        } else if (lastMessage.type === 'alignment_update' && lastMessage.data?.type === 'value') {
          const newValue = lastMessage.data.value;
          if (newValue && typeof newValue === 'object') {
            setValues((prev) => [...prev, newValue]);
            setError(null);
          }
        } else if (lastMessage.type === 'alignment_complete') {
          const stats = lastMessage.results?.statistics;
          if (stats) {
            setStatistics(stats);
            setError(null);
          }
        }
      }
    } catch (err: any) {
      console.error('Error processing WebSocket message:', err);
      setError(err.message || 'Error processing data');
    }
  }, [lastMessage]);

  // Réinitialiser les valeurs quand un nouvel alignement démarre
  useEffect(() => {
    if (status === 'idle') {
      setValues([]);
      setStatistics(null);
    } else if (status === 'running' && values.length === 0) {
      // Réinitialiser au début d'un nouvel alignement
      setValues([]);
      setStatistics(null);
    }
  }, [status]);

  if (values.length === 0 && !statistics) {
    return (
      <div className="bg-gray-800 rounded-lg p-4">
        <h2 className="text-xl font-semibold mb-3">{t('alignmentResults')}</h2>
        <p className="text-gray-400 text-sm">{t('noDataAvailable')}</p>
      </div>
    );
  }

  // Préparer les données pour le graphique
  const chartData = values
    .filter(value => value && typeof value.percentage === 'number' && !isNaN(value.percentage))
    .map((value, index) => ({
      index: index + 1,
      track: value.track || `${index + 1}`,
      percentage: value.percentage,
      name: value.track || `#${index + 1}`
    }));

  // Données pour le graphique en barres par tranche de pourcentage
  const qualityRanges = [
    { range: t('perfectRange'), count: 0, fill: '#10b981' },
    { range: t('goodRange'), count: 0, fill: '#3b82f6' },
    { range: t('averageRange'), count: 0, fill: '#f59e0b' },
    { range: t('poorRange'), count: 0, fill: '#ef4444' }
  ];

  values.forEach(value => {
    if (value && typeof value.percentage === 'number' && !isNaN(value.percentage)) {
      if (value.percentage >= 99) {
        qualityRanges[0].count++;
      } else if (value.percentage >= 97) {
        qualityRanges[1].count++;
      } else if (value.percentage >= 96) {
        qualityRanges[2].count++;
      } else {
        qualityRanges[3].count++;
      }
    }
  });

  // Gestion des erreurs
  if (error) {
    return (
      <div className="bg-gray-800 rounded-lg p-4">
        <h2 className="text-xl font-semibold mb-3">{t('alignmentResults')}</h2>
        <div className="bg-red-900 border border-red-700 text-red-200 px-3 py-2 rounded text-sm">
          <p className="font-bold">{t('displayError')}</p>
          <p>{error}</p>
          <button 
            onClick={() => setError(null)}
            className="mt-2 px-4 py-2 bg-red-700 hover:bg-red-600 rounded"
          >
            {t('retry')}
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-gray-800 rounded-lg p-4 space-y-4">
      <h2 className="text-xl font-semibold mb-3">{t('alignmentResults')}</h2>

      {statistics && (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
          <div className="bg-gray-700 rounded p-3">
            <div className="text-xs text-gray-400">{t('average')}</div>
            <div className="text-xl font-bold text-white">
              {typeof statistics.average === 'number' ? statistics.average.toFixed(2) : statistics.average || '0.00'}%
            </div>
            <div className={`text-sm mt-1 ${
              statistics.quality === 'Perfect' ? 'text-green-400' :
              statistics.quality === 'Good' ? 'text-blue-400' :
              statistics.quality === 'Average' ? 'text-yellow-400' :
              'text-red-400'
            }`}>
              {statistics.quality || 'N/A'}
            </div>
          </div>

          <div className="bg-gray-700 rounded p-3">
            <div className="text-xs text-gray-400">{t('minimum')}</div>
            <div className="text-xl font-bold text-white">
              {typeof statistics.min === 'number' ? statistics.min.toFixed(2) : statistics.min || '0.00'}%
            </div>
          </div>

          <div className="bg-gray-700 rounded p-3">
            <div className="text-xs text-gray-400">{t('maximum')}</div>
            <div className="text-xl font-bold text-white">
              {typeof statistics.max === 'number' ? statistics.max.toFixed(2) : statistics.max || '0.00'}%
            </div>
          </div>

          <div className="bg-gray-700 rounded p-3">
            <div className="text-xs text-gray-400">{t('totalValues')}</div>
            <div className="text-xl font-bold text-white">{statistics.total_values || 0}</div>
          </div>

          <div className="bg-gray-700 rounded p-3">
            <div className="text-xs text-gray-400">{t('usedValues')}</div>
            <div className="text-xl font-bold text-white">{statistics.used_values || 0}</div>
          </div>

          {statistics.track_max && (
            <div className="bg-gray-700 rounded p-3">
              <div className="text-xs text-gray-400">{t('maxTrack')}</div>
              <div className="text-xl font-bold text-white">{statistics.track_max}</div>
            </div>
          )}
        </div>
      )}

      {/* Tableau détaillé avec feedback visuel */}
      {statistics && statistics.values && Array.isArray(statistics.values) && statistics.values.length > 0 && (
        <div>
          <h3 className="text-base font-semibold mb-2">{t('detailsByTrack')}</h3>
          <div className="overflow-x-auto">
            <table className="w-full border-collapse">
              <thead>
                <tr className="bg-gray-700">
                  <th className="border border-gray-600 px-4 py-2 text-left">{t('trackDetail')}</th>
                  <th className="border border-gray-600 px-4 py-2 text-center">{t('percentageDetail')}</th>
                  <th className="border border-gray-600 px-4 py-2 text-center">{t('sectorsDetail')}</th>
                  <th className="border border-gray-600 px-4 py-2 text-center">{t('consistency')}</th>
                  <th className="border border-gray-600 px-4 py-2 text-center">{t('stability')}</th>
                  <th className="border border-gray-600 px-4 py-2 text-center">{t('azimuth')}</th>
                  <th className="border border-gray-600 px-4 py-2 text-center">{t('asymmetry')}</th>
                  <th className="border border-gray-600 px-4 py-2 text-center">{t('positionDetail')}</th>
                  <th className="border border-gray-600 px-4 py-2 text-center">{t('status')}</th>
                </tr>
              </thead>
              <tbody>
                {statistics.values
                  .filter((value: any) => value && typeof value === 'object')
                  .map((value: AlignmentValue, index: number) => {
                  // Vérifier que value est valide
                  if (!value || typeof value.percentage !== 'number' || isNaN(value.percentage)) {
                    return null;
                  }

                  // Déterminer la couleur et l'icône selon le pourcentage
                  const getPercentageColor = (pct: number) => {
                    if (pct >= 99) return 'text-green-400';
                    if (pct >= 97) return 'text-blue-400';
                    if (pct >= 96) return 'text-yellow-400';
                    return 'text-red-400';
                  };

                  const getPercentageIcon = (pct: number) => {
                    if (pct >= 99) return '✓';
                    if (pct >= 97) return '○';
                    if (pct >= 96) return '⚠';
                    return '✗';
                  };

                  // Déterminer la couleur de cohérence
                  const getConsistencyColor = (consistency?: number) => {
                    if (!consistency) return 'text-gray-500';
                    if (consistency >= 90) return 'text-green-400';
                    if (consistency >= 70) return 'text-yellow-400';
                    return 'text-red-400';
                  };

                  // Déterminer la couleur de stabilité
                  const getStabilityColor = (stability?: number) => {
                    if (!stability) return 'text-gray-500';
                    if (stability >= 90) return 'text-green-400';
                    if (stability >= 70) return 'text-yellow-400';
                    return 'text-red-400';
                  };

                  // Déterminer l'icône de positionnement
                  const getPositioningIcon = (status?: string) => {
                    if (!status) return '○';
                    if (status === 'correct') return '✓';
                    if (status === 'unstable') return '↕';
                    return '✗';
                  };

                  const getPositioningColor = (status?: string) => {
                    if (!status) return 'text-gray-500';
                    if (status === 'correct') return 'text-green-400';
                    if (status === 'unstable') return 'text-yellow-400';
                    return 'text-red-400';
                  };

                  // Déterminer la couleur d'azimut
                  const getAzimuthColor = (status?: string, score?: number) => {
                    if (!status && !score) return 'text-gray-500';
                    if (status === 'excellent' || (score !== undefined && score >= 95)) return 'text-green-400';
                    if (status === 'good' || (score !== undefined && score >= 85)) return 'text-blue-400';
                    if (status === 'acceptable' || (score !== undefined && score >= 75)) return 'text-yellow-400';
                    return 'text-red-400';
                  };

                  // Déterminer la couleur d'asymétrie
                  const getAsymmetryColor = (status?: string, score?: number) => {
                    if (!status && !score) return 'text-gray-500';
                    if (status === 'excellent' || (score !== undefined && score >= 95)) return 'text-green-400';
                    if (status === 'good' || (score !== undefined && score >= 85)) return 'text-blue-400';
                    if (status === 'acceptable' || (score !== undefined && score >= 75)) return 'text-yellow-400';
                    return 'text-red-400';
                  };

                  return (
                    <tr key={index} className="hover:bg-gray-700">
                      <td className="border border-gray-600 px-4 py-2 font-mono">{value.track || `Track ${index + 1}`}</td>
                      <td className={`border border-gray-600 px-4 py-2 text-center font-bold ${getPercentageColor(value.percentage)}`}>
                        <span className="mr-2">{getPercentageIcon(value.percentage)}</span>
                        {typeof value.percentage === 'number' ? value.percentage.toFixed(2) : 'N/A'}%
                      </td>
                      <td className="border border-gray-600 px-4 py-2 text-center text-gray-300">
                        {value.sectors_detected !== undefined && value.sectors_expected !== undefined
                          ? `${value.sectors_detected}/${value.sectors_expected}`
                          : '-'}
                      </td>
                      <td className={`border border-gray-600 px-4 py-2 text-center ${getConsistencyColor(value.consistency)}`}>
                        {value.consistency !== undefined && typeof value.consistency === 'number' ? `${value.consistency.toFixed(1)}%` : '-'}
                      </td>
                      <td className={`border border-gray-600 px-4 py-2 text-center ${getStabilityColor(value.stability)}`}>
                        {value.stability !== undefined && typeof value.stability === 'number' ? `${value.stability.toFixed(1)}%` : '-'}
                      </td>
                      <td className={`border border-gray-600 px-4 py-2 text-center ${getAzimuthColor(value.azimuth_status, value.azimuth_score)}`}>
                        <div className="text-xs">
                          {value.azimuth_score !== undefined && typeof value.azimuth_score === 'number' ? `${value.azimuth_score.toFixed(1)}%` : '-'}
                        </div>
                        {value.azimuth_status && (
                          <div className="text-xs mt-1 text-gray-400">
                            {value.azimuth_status === 'excellent' ? t('excellent') :
                             value.azimuth_status === 'good' ? t('good') :
                             value.azimuth_status === 'acceptable' ? t('acceptable') :
                             value.azimuth_status === 'poor' ? t('poor') : '-'}
                          </div>
                        )}
                      </td>
                      <td className={`border border-gray-600 px-4 py-2 text-center ${getAsymmetryColor(value.asymmetry_status, value.asymmetry_score)}`}>
                        <div className="text-xs">
                          {value.asymmetry_score !== undefined && typeof value.asymmetry_score === 'number' ? `${value.asymmetry_score.toFixed(1)}%` : '-'}
                        </div>
                        {value.asymmetry_status && (
                          <div className="text-xs mt-1 text-gray-400">
                            {value.asymmetry_status === 'excellent' ? t('excellent') :
                             value.asymmetry_status === 'good' ? t('good') :
                             value.asymmetry_status === 'acceptable' ? t('acceptable') :
                             value.asymmetry_status === 'poor' ? t('poor') : '-'}
                          </div>
                        )}
                      </td>
                      <td className={`border border-gray-600 px-4 py-2 text-center ${getPositioningColor(value.positioning_status)}`}>
                        <span className="text-xl">{getPositioningIcon(value.positioning_status)}</span>
                        <div className="text-xs mt-1">
                          {value.positioning_status === 'correct' ? t('correct') :
                           value.positioning_status === 'unstable' ? t('unstable') :
                           value.positioning_status === 'poor' ? t('poor') : '-'}
                        </div>
                      </td>
                      <td className="border border-gray-600 px-4 py-2 text-center">
                        <div className="flex items-center justify-center gap-2">
                          {/* Indicateur visuel principal */}
                          <div className={`w-4 h-4 rounded-full ${
                            value.percentage >= 99 ? 'bg-green-500' :
                            value.percentage >= 97 ? 'bg-blue-500' :
                            value.percentage >= 96 ? 'bg-yellow-500' :
                            'bg-red-500'
                          }`} />
                          {/* Flèche de positionnement si instable */}
                          {value.positioning_status === 'unstable' && (
                            <span className="text-yellow-400 text-lg">↕</span>
                          )}
                          {value.positioning_status === 'poor' && (
                            <span className="text-red-400 text-lg">↓</span>
                          )}
                        </div>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {values.length > 0 && (
        <>
          <div>
            <h3 className="text-base font-semibold mb-2">{t('evolutionPercentage')}</h3>
            <ResponsiveContainer width="100%" height={250}>
              <LineChart data={chartData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                <XAxis 
                  dataKey="name" 
                  stroke="#9ca3af"
                  tick={{ fill: '#9ca3af' }}
                  angle={-45}
                  textAnchor="end"
                  height={80}
                />
                <YAxis 
                  stroke="#9ca3af"
                  tick={{ fill: '#9ca3af' }}
                  domain={[90, 100]}
                  label={{ value: `${t('percentage')} (%)`, angle: -90, position: 'insideLeft', fill: '#9ca3af' }}
                />
                <Tooltip 
                  contentStyle={{ backgroundColor: '#1f2937', border: '1px solid #374151', color: '#fff' }}
                />
                <Line 
                  type="monotone" 
                  dataKey="percentage" 
                  stroke="#3b82f6" 
                  strokeWidth={2}
                  dot={{ r: 3 }}
                  activeDot={{ r: 5 }}
                />
              </LineChart>
            </ResponsiveContainer>
          </div>

          <div>
            <h3 className="text-base font-semibold mb-2">{t('distributionByQuality')}</h3>
            <ResponsiveContainer width="100%" height={200}>
              <BarChart data={qualityRanges}>
                <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                <XAxis 
                  dataKey="range" 
                  stroke="#9ca3af"
                  tick={{ fill: '#9ca3af' }}
                  angle={-45}
                  textAnchor="end"
                  height={100}
                />
                <YAxis 
                  stroke="#9ca3af"
                  tick={{ fill: '#9ca3af' }}
                />
                <Tooltip 
                  contentStyle={{ backgroundColor: '#1f2937', border: '1px solid #374151', color: '#fff' }}
                />
                <Bar dataKey="count" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </>
      )}
    </div>
  );
}

