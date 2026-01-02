import { useState, useEffect, useRef } from 'react'
import axios from 'axios'
import { AlignmentControl } from './components/AlignmentControl'
import { AlignmentResults } from './components/AlignmentResults'
import { ManualAlignment } from './components/ManualAlignment'
import { NavigationControl } from './components/NavigationControl'
import { useSettings } from './hooks/useSettings'
import { useTranslation } from './i18n/useTranslation'

interface DeviceInfo {
  port: string | null
  model: string | null
  mcu: string | null
  firmware: string | null
  serial: string | null
  usb: string | null
  connected: boolean
}

interface GreaseweazleInfo {
  platform: string
  gw_path: string
  version: string | null
  align_available: boolean
  device: DeviceInfo | null
}

interface AlignmentStatus {
  status: string
}

interface DetectionResult {
  ports_detected: number
  ports_shown?: number
  ports: Array<{
    device: string
    description: string
    is_greaseweazle?: boolean
    manufacturer?: string
    product?: string
    vid?: string
    pid?: string
  }>
  greaseweazle_found: boolean
  connection: {
    connected: boolean
    port: string | null
    error: string | null
    last_port?: string | null
  }
  gw_path: string
  gw_available: boolean
  align_available: boolean
}

function App() {
  const [info, setInfo] = useState<GreaseweazleInfo | null>(null)
  const [status, setStatus] = useState<AlignmentStatus | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [detecting, setDetecting] = useState(false)
  const [detectionResult, setDetectionResult] = useState<DetectionResult | null>(null)
  const [portsExpanded, setPortsExpanded] = useState(false)
  const [infoExpanded, setInfoExpanded] = useState(false)
  const [activeTab, setActiveTab] = useState<'auto' | 'manual'>('auto')
  const [previousTab, setPreviousTab] = useState<'auto' | 'manual'>('auto')
  // État partagé pour le format entre les modes automatique et manuel
  const [sharedFormat, setSharedFormat] = useState<string>(() => {
    // Charger depuis localStorage ou utiliser la valeur par défaut
    const savedFormat = localStorage.getItem('alignTester_selectedFormat')
    return savedFormat || 'ibm.1440'
  })
  // État pour les données du mode manuel (position actuelle et dernière analyse)
  const [manualState, setManualState] = useState<any>(null)
  // État pour l'historique des lectures en mode manuel
  const [manualLiveReadings, setManualLiveReadings] = useState<any[]>([])
  // Position actuelle sauvegardée même sans mode démarré
  const [currentPosition, setCurrentPosition] = useState<{ track: number; head: number }>(() => {
    const saved = localStorage.getItem('alignTester_currentPosition')
    if (saved) {
      try {
        return JSON.parse(saved)
      } catch {
        return { track: 0, head: 0 }
      }
    }
    return { track: 0, head: 0 }
  })
  const { settings, saveLastPort } = useSettings()
  const { t, language, setLanguage } = useTranslation()
  const [selectedDrive, setSelectedDrive] = useState<string>('A')
  const [testingDrive, setTestingDrive] = useState(false)
  const [verifyingTrack0, setVerifyingTrack0] = useState(false)
  const [track0Result, setTrack0Result] = useState<any>(null)
  const [gwPath, setGwPath] = useState<string>('')
  const [gwPathInput, setGwPathInput] = useState<string>('')
  const [savingGwPath, setSavingGwPath] = useState(false)
  const [detectingGwPath, setDetectingGwPath] = useState(false)
  const [showDriveInfo, setShowDriveInfo] = useState(false)
  const fileInputRef = useRef<HTMLInputElement>(null)

  // Sauvegarder le format dans localStorage quand il change
  useEffect(() => {
    localStorage.setItem('alignTester_selectedFormat', sharedFormat)
  }, [sharedFormat])

  useEffect(() => {
    fetchInfo()
    fetchStatus()
    fetchDrive()
    fetchGwPath()
    const statusInterval = setInterval(fetchStatus, 2000) // Rafraîchir le statut toutes les 2 secondes
    return () => clearInterval(statusInterval)
  }, [])

  const fetchGwPath = async () => {
    try {
      const response = await axios.get('http://localhost:8000/api/settings/gw-path')
      if (response.data.success && response.data.gw_path) {
        setGwPath(response.data.gw_path)
        setGwPathInput(response.data.gw_path)
      } else if (info?.gw_path) {
        // Si pas de chemin sauvegardé, utiliser celui depuis info
        setGwPath(info.gw_path)
        setGwPathInput(info.gw_path)
      }
    } catch (err) {
      console.error('Error fetching gw path:', err)
      // Utiliser le chemin depuis info si disponible
      if (info?.gw_path) {
        setGwPath(info.gw_path)
        setGwPathInput(info.gw_path)
      }
    }
  }

  // Mettre à jour le chemin gw quand info change
  useEffect(() => {
    if (info?.gw_path && !gwPath) {
      setGwPath(info.gw_path)
      setGwPathInput(info.gw_path)
    }
  }, [info?.gw_path])

  const handleBrowseGwPath = () => {
    // Ouvrir le dialogue de sélection de fichier
    fileInputRef.current?.click()
  }

  const handleFileSelected = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0]
    if (file) {
      // Essayer d'obtenir le chemin complet si disponible
      // Dans certains contextes (Electron, ou certains navigateurs avec API filesystem),
      // on peut avoir accès au chemin complet via file.path ou d'autres propriétés
      let fullPath: string | null = null
      
      // Vérifier si file.path existe (Electron, certains environnements)
      if ((file as any).path) {
        fullPath = (file as any).path
      }
      
      // Si on a le chemin complet, l'utiliser directement
      if (fullPath) {
        setGwPathInput(fullPath)
        // Sauvegarder automatiquement si c'est un chemin valide
        handleSetGwPath()
      } else {
        // Sinon, utiliser le nom du fichier et demander le chemin complet
        const fileName = file.name
        
        // Si c'est gw.exe ou gw, on peut suggérer un chemin
        if (fileName === 'gw.exe' || fileName === 'gw') {
          // Mettre à jour l'input avec le nom du fichier
          // L'utilisateur devra compléter avec le chemin complet
          setGwPathInput(fileName)
          alert(t('gwPathFileSelected') + ' ' + fileName + '. ' + t('gwPathCompletePath'))
        } else {
          setGwPathInput(fileName)
        }
      }
    }
    
    // Réinitialiser l'input pour permettre de sélectionner le même fichier
    if (fileInputRef.current) {
      fileInputRef.current.value = ''
    }
  }

  const handleDetectGwPath = async () => {
    try {
      setDetectingGwPath(true)
      const response = await axios.post('http://localhost:8000/api/settings/gw-path/detect', {})
      
      if (response.data.success && response.data.found) {
        const detectedPath = response.data.gw_path
        setGwPath(detectedPath)
        setGwPathInput(detectedPath)
        alert(t('gwPathDetected') + ': ' + detectedPath)
        // Rafraîchir les infos pour mettre à jour l'affichage
        fetchInfo()
      } else {
        setError(response.data.error || response.data.message || t('gwPathDetectionFailed'))
        alert(response.data.message || t('gwPathDetectionFailed'))
      }
    } catch (err: any) {
      const errorMsg = err.response?.data?.detail || err.message || t('gwPathDetectionFailed')
      setError(errorMsg)
      alert(errorMsg)
    } finally {
      setDetectingGwPath(false)
    }
  }

  const handleSetGwPath = async () => {
    if (!gwPathInput.trim()) {
      setError(t('gwPathError'))
      return
    }

    try {
      setSavingGwPath(true)
      setError(null)
      const response = await axios.post('http://localhost:8000/api/settings/gw-path', { 
        gw_path: gwPathInput.trim() 
      })
      if (response.data.success) {
        setGwPath(gwPathInput.trim())
        // Rafraîchir les infos pour mettre à jour le chemin
        await fetchInfo()
        alert(t('gwPathSaved'))
      } else {
        setError(response.data.error || t('gwPathError'))
      }
    } catch (err: any) {
      if (err.response?.status === 400 && err.response?.data?.detail?.includes('n\'existe pas')) {
        setError(t('gwPathNotFound'))
      } else {
        setError(err.response?.data?.detail || err.message || t('gwPathError'))
      }
      console.error(err)
    } finally {
      setSavingGwPath(false)
    }
  }

  const fetchDrive = async () => {
    try {
      const response = await axios.get('http://localhost:8000/api/settings/drive')
      if (response.data.success) {
        setSelectedDrive(response.data.drive)
      }
    } catch (err) {
      console.error('Error fetching drive:', err)
    }
  }

  const handleDriveChange = async (drive: string) => {
    try {
      setError(null)
      const response = await axios.post('http://localhost:8000/api/settings/drive', { drive })
      if (response.data.success) {
        setSelectedDrive(drive)
      }
    } catch (err: any) {
      setError(err.response?.data?.detail || t('error'))
      console.error(err)
    }
  }

  const handleTestDrive = async () => {
    if (!info?.device?.connected) {
      setError(t('driveTestNotConnected'))
      return
    }

    try {
      setTestingDrive(true)
      setError(null)
      const response = await axios.post('http://localhost:8000/api/drive/test')
      if (response.data.success) {
        // Afficher un message de succès temporaire
        alert(t('driveTestSuccess'))
      } else {
        setError(response.data.error || t('driveTestError'))
      }
    } catch (err: any) {
      setError(err.response?.data?.detail || err.message || t('driveTestError'))
      console.error(err)
    } finally {
      setTestingDrive(false)
    }
  }

  const handleVerifyTrack0 = async () => {
    if (!info?.device?.connected) {
      setError(t('track0VerifyNotConnected'))
      return
    }

    try {
      setVerifyingTrack0(true)
      setError(null)
      setTrack0Result(null)
      // Envoyer le format sélectionné pour les lectures
      const response = await axios.post('http://localhost:8000/api/track0/verify', {
        format_type: sharedFormat || 'ibm.1440'
      })
      setTrack0Result(response.data)
      if (!response.data.sensor_ok) {
        // Afficher les avertissements si le capteur n'est pas OK
        if (response.data.warnings && response.data.warnings.length > 0) {
          console.warn('Avertissements Track 0:', response.data.warnings)
        }
      }
    } catch (err: any) {
      console.error('Erreur vérification Track 0:', err)
      setError(err.response?.data?.detail || err.message || t('track0VerifyError'))
    } finally {
      setVerifyingTrack0(false)
    }
  }

  // Arrêter les processus en cours lors d'un changement d'onglet et synchroniser le format
  useEffect(() => {
    const handleTabChange = async () => {
      // Si on change d'onglet, arrêter les processus en cours
      if (previousTab !== activeTab && previousTab !== 'auto' && previousTab !== 'manual') {
        // Premier rendu, initialiser previousTab
        setPreviousTab(activeTab)
        return
      }
      
      if (previousTab !== activeTab) {
        try {
          // Arrêter le mode manuel si on quitte l'onglet manuel
          if (previousTab === 'manual') {
            await axios.post('http://localhost:8000/api/manual/stop').catch(() => {
              // Ignorer les erreurs (peut-être déjà arrêté)
            })
          }
          // Annuler l'alignement automatique si on quitte l'onglet auto
          if (previousTab === 'auto') {
            await axios.post('http://localhost:8000/api/align/cancel').catch(() => {
              // Ignorer les erreurs (peut-être déjà arrêté)
            })
          }
          
          // Attendre un peu pour que les processus s'arrêtent avant de synchroniser
          await new Promise(resolve => setTimeout(resolve, 300))
          
          // Synchroniser le format quand on change d'onglet
          if (activeTab === 'manual') {
            // Quand on passe au mode manuel, mettre à jour le format du backend avec le format partagé
            // Utiliser un retry pour éviter les erreurs aléatoires
            let retryCount = 0;
            const maxRetries = 3;
            while (retryCount < maxRetries) {
              try {
                await axios.post('http://localhost:8000/api/manual/settings', {
                  format_type: sharedFormat
                }, {
                  timeout: 5000 // Timeout de 5 secondes
                })
                break; // Succès, sortir de la boucle
              } catch (err: any) {
                retryCount++;
                if (retryCount >= maxRetries) {
                  console.error('Error synchronizing format after', maxRetries, 'attempts:', err)
                } else {
                  // Attendre un peu avant de réessayer (backoff exponentiel)
                  await new Promise(resolve => setTimeout(resolve, 200 * Math.pow(2, retryCount)))
                }
              }
            }
          } else if (activeTab === 'auto') {
            // Quand on passe au mode automatique, récupérer le format du mode manuel et le synchroniser
            // Utiliser un retry pour éviter les erreurs aléatoires
            let retryCount = 0;
            const maxRetries = 3;
            while (retryCount < maxRetries) {
              try {
                const response = await axios.get('http://localhost:8000/api/manual/state', {
                  timeout: 5000 // Timeout de 5 secondes
                })
                if (response.data?.format_type && response.data.format_type !== sharedFormat) {
                  setSharedFormat(response.data.format_type)
                }
                break; // Succès, sortir de la boucle
              } catch (err: any) {
                retryCount++;
                if (retryCount >= maxRetries) {
                  console.error('Error fetching manual mode format after', maxRetries, 'attempts:', err)
                } else {
                  // Attendre un peu avant de réessayer (backoff exponentiel)
                  await new Promise(resolve => setTimeout(resolve, 200 * Math.pow(2, retryCount)))
                }
              }
            }
          }
        } catch (err) {
          // Ignorer les erreurs silencieusement
          console.error('Erreur lors de l\'arrêt des processus:', err)
        }
        setPreviousTab(activeTab)
      }
    }

    handleTabChange()
  }, [activeTab]) // Retirer sharedFormat des dépendances pour éviter les boucles

  const fetchInfo = async () => {
    try {
      setLoading(true)
      const response = await axios.get<GreaseweazleInfo>('http://localhost:8000/api/info')
      setInfo(response.data)
      setError(null)
    } catch (err) {
      setError(t('cannotConnectBackend'))
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  const fetchStatus = async () => {
    try {
      const response = await axios.get<AlignmentStatus>('http://localhost:8000/api/status')
      setStatus(response.data)
    } catch (err: any) {
      // Ignorer les erreurs de statut silencieusement si le backend n'est pas disponible
      if (err.code !== 'ERR_NETWORK' && err.response?.status !== 500) {
        console.error('Error fetching status:', err)
      }
    }
  }

  // Sauvegarder la position actuelle dans localStorage
  useEffect(() => {
    localStorage.setItem('alignTester_currentPosition', JSON.stringify(currentPosition))
  }, [currentPosition])

  // Récupérer l'état du mode manuel pour afficher position actuelle et dernière analyse à droite
  // Toujours récupérer l'état, même si le mode n'est pas démarré, pour permettre la navigation
  useEffect(() => {
    if (activeTab === 'manual') {
      const fetchManualState = async () => {
        try {
          const response = await axios.get('http://localhost:8000/api/manual/state')
          setManualState(response.data)
          // Sauvegarder la position actuelle depuis l'état du backend
          if (response.data && (response.data.current_track !== undefined || response.data.current_head !== undefined)) {
            setCurrentPosition({
              track: response.data.current_track ?? currentPosition.track,
              head: response.data.current_head ?? currentPosition.head
            })
          }
        } catch (err) {
          // Si le mode n'est pas démarré, utiliser la position sauvegardée
          setManualState({
            is_running: false,
            current_track: currentPosition.track,
            current_head: currentPosition.head,
            last_reading: null
          })
        }
      }
      fetchManualState()
      const interval = setInterval(fetchManualState, 1000)
      return () => clearInterval(interval)
    } else {
      setManualState(null)
    }
  }, [activeTab, currentPosition])

  const handleAlignmentStart = () => {
    fetchStatus()
  }

  const handleResetData = async () => {
    try {
      await axios.post('http://localhost:8000/api/align/reset')
      // Rafraîchir le statut pour mettre à jour l'interface
      await fetchStatus()
      setError(null)
    } catch (err: any) {
      setError(err.response?.data?.detail || t('errorResettingData'))
      console.error(err)
    }
  }

  const handleHardReset = async () => {
    if (!info?.align_available) {
      setError(t('alignCommandNotAvailable'))
      return
    }

    // Confirmation avant hard reset
    if (!window.confirm(t('confirmHardReset'))) {
      return
    }

    try {
      setLoading(true)
      setError(null)
      const response = await axios.post('http://localhost:8000/api/align/hard-reset')
      
      if (response.data.status === 'success') {
        // Rafraîchir les infos après reset
        await fetchInfo()
        setError(null)
        // Afficher un message de succès temporaire
        const successMsg = response.data.message || t('hardResetSuccess')
        alert(successMsg)
      } else {
        setError(response.data.message || t('hardResetError'))
      }
    } catch (err: any) {
      setError(err.response?.data?.detail || err.message || t('hardResetError'))
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  const handleDetect = async () => {
    try {
      setDetecting(true)
      setError(null)
      const response = await axios.get<DetectionResult>('http://localhost:8000/api/detect')
      setDetectionResult(response.data)
      
      // Sauvegarder le port si Greaseweazle est trouvé
      if (response.data.greaseweazle_found && response.data.connection.port) {
        await saveLastPort(response.data.connection.port)
      }
      
      // Rafraîchir les infos après détection
      await fetchInfo()
    } catch (err: any) {
      setError(err.response?.data?.detail || t('detectionError'))
      console.error(err)
    } finally {
      setDetecting(false)
    }
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-900 text-white flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-white mx-auto mb-4"></div>
          <p>{t('loading')}</p>
        </div>
      </div>
    )
  }

  return (
      <div className="min-h-screen bg-gray-900 text-white">
      <div className="container mx-auto px-4 py-4">
        {/* Header : Titre centré + Drapeaux */}
        <header className="mb-4 relative">
          <div className="text-center">
            <h1 className="text-3xl font-bold mb-1">{t('appTitle')}</h1>
            <p className="text-gray-400 text-sm">{t('appSubtitle')}</p>
          </div>
          <div className="absolute top-0 right-0 flex gap-2">
            <button
              onClick={() => setLanguage('fr')}
              className={`px-3 py-1 rounded text-lg transition-all ${
                language === 'fr' 
                  ? 'ring-2 ring-blue-500 ring-offset-2 ring-offset-gray-900' 
                  : 'opacity-70 hover:opacity-100'
              }`}
              title="Français"
            >
              🇫🇷
            </button>
            <button
              onClick={() => setLanguage('en')}
              className={`px-3 py-1 rounded text-lg transition-all ${
                language === 'en' 
                  ? 'ring-2 ring-blue-500 ring-offset-2 ring-offset-gray-900' 
                  : 'opacity-70 hover:opacity-100'
              }`}
              title="English"
            >
              🇬🇧
            </button>
          </div>
        </header>

        {/* Boutons Reset Data et Hard Reset sous les drapeaux */}
        <div className="flex gap-2 mb-4 justify-end">
          <button
            onClick={handleResetData}
            className="px-4 py-2 bg-yellow-600 hover:bg-yellow-700 text-white font-semibold rounded transition-colors relative group"
            title={t('resetDataTooltip')}
          >
            <span className="flex items-center gap-2">
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
              </svg>
              Reset Data
            </span>
            {/* Tooltip */}
            <div className="absolute bottom-full right-0 mb-2 w-64 p-2 bg-gray-800 text-white text-xs rounded shadow-lg opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none z-50">
              {t('resetDataTooltip')}
            </div>
          </button>
          <button
            onClick={handleHardReset}
            disabled={!info?.align_available}
            className="px-4 py-2 bg-red-600 hover:bg-red-700 disabled:bg-gray-600 disabled:cursor-not-allowed text-white font-semibold rounded transition-colors relative group"
            title={t('hardResetTooltip')}
          >
            <span className="flex items-center gap-2">
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
              </svg>
              HARD RESET
            </span>
            {/* Tooltip */}
            <div className="absolute bottom-full right-0 mb-2 w-64 p-2 bg-gray-800 text-white text-xs rounded shadow-lg opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none z-50">
              {t('hardResetTooltip')}
            </div>
          </button>
        </div>

        {error && (
          <div className="bg-red-900 border border-red-700 text-red-200 px-4 py-2 rounded mb-3 text-sm">
            <p className="font-bold">{t('error')}</p>
            <p>{error}</p>
          </div>
        )}

        {/* Informations Greaseweazle : Pleine largeur, compact */}
        {info && (
          <div className="bg-gray-800 rounded-lg p-3 mb-4">
            <div className="flex justify-between items-center mb-2">
              <button
                onClick={() => setInfoExpanded(!infoExpanded)}
                className="flex items-center gap-2 text-lg font-semibold hover:text-blue-400 transition-colors flex-1"
              >
                <span className={`transform transition-transform ${infoExpanded ? 'rotate-90' : ''}`}>
                  ▶
                </span>
                <h2>{t('greaseweazleInfo')}</h2>
                {/* Indication visuelle quand replié */}
                {!infoExpanded && info && (
                  <span className="ml-4 text-sm font-normal text-gray-400">
                    {info.device?.connected && info.device?.port ? (
                      <>
                        <span className="text-green-400 mr-1">●</span>
                        {t('greaseweazleDetectedOn')} <span className="font-mono text-blue-400">{info.device.port}</span>
                      </>
                    ) : info.align_available ? (
                      <span className="text-gray-500">{t('alignAvailable')}: {t('yes')}</span>
                    ) : null}
                  </span>
                )}
              </button>
              <button
                onClick={handleDetect}
                disabled={detecting}
                className="px-3 py-1.5 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-600 disabled:cursor-not-allowed rounded text-white text-sm font-medium transition-colors"
              >
                {detecting ? t('detecting') : t('detectButton')}
              </button>
            </div>
            
            {infoExpanded && (
              <div className="space-y-3 pt-2 border-t border-gray-700">
                {/* Configuration du chemin gw.exe */}
                <div className="border-b border-gray-700 pb-3 mb-3">
                  <h3 className="text-base font-semibold mb-2">{t('gwPathConfig')}</h3>
                  <div className="space-y-2">
                    <div className="text-xs text-gray-400 mb-1">
                      {t('currentGwPath')} <span className="font-mono text-blue-400">{gwPath || info.gw_path}</span>
                    </div>
                    <div className="flex gap-2">
                      <input
                        type="text"
                        value={gwPathInput}
                        onChange={(e) => setGwPathInput(e.target.value)}
                        placeholder={t('gwPathPlaceholder')}
                        className="flex-1 px-3 py-2 bg-gray-700 border border-gray-600 rounded text-white text-sm focus:outline-none focus:border-blue-500"
                        onKeyDown={(e) => {
                          if (e.key === 'Enter' && gwPathInput.trim()) {
                            handleSetGwPath()
                          }
                        }}
                      />
                      {/* Input file caché pour le sélecteur de fichier */}
                      <input
                        ref={fileInputRef}
                        type="file"
                        accept=".exe,.EXE"
                        style={{ display: 'none' }}
                        onChange={handleFileSelected}
                      />
                      <button
                        onClick={handleDetectGwPath}
                        disabled={detectingGwPath}
                        className="px-4 py-2 bg-green-600 hover:bg-green-700 disabled:bg-gray-600 disabled:cursor-not-allowed text-white font-medium rounded transition-colors text-sm"
                        title={t('gwPathDetect')}
                      >
                        {detectingGwPath ? t('saving') : t('gwPathDetect')}
                      </button>
                      <button
                        onClick={handleBrowseGwPath}
                        className="px-4 py-2 bg-gray-600 hover:bg-gray-700 text-white font-medium rounded transition-colors text-sm"
                        title={t('browseGwPath')}
                      >
                        {t('browseGwPath')}
                      </button>
                      <button
                        onClick={handleSetGwPath}
                        disabled={savingGwPath || !gwPathInput.trim()}
                        className="px-4 py-2 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-600 disabled:cursor-not-allowed text-white font-medium rounded transition-colors text-sm"
                      >
                        {savingGwPath ? t('saving') : t('setGwPath')}
                      </button>
                    </div>
                    <div className="text-xs text-gray-500 italic">
                      💡 {t('gwPathTip')}
                    </div>
                  </div>
                </div>
                
                <div className="grid grid-cols-1 md:grid-cols-2 gap-3 text-sm">
                <div className="flex justify-between">
                  <span className="text-gray-400">{t('platform')}</span>
                  <span className="font-mono">{info.platform}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-400">{t('gwPath')}</span>
                    <span className="font-mono text-xs">{info.gw_path}</span>
                </div>
                {info.version && (
                  <div className="flex justify-between">
                    <span className="text-gray-400">{t('hostToolsVersion')}</span>
                    <span className="font-mono">{info.version}</span>
                  </div>
                )}
                <div className="flex justify-between">
                  <span className="text-gray-400">{t('alignAvailable')}</span>
                  <span className={info.align_available ? "text-green-400" : "text-red-400"}>
                    {info.align_available ? `✓ ${t('yes')}` : `✗ ${t('no')}`}
                  </span>
                </div>
              </div>
              
              {info.device && (
                <>
                    <div className="border-t border-gray-700 pt-3">
                      <h3 className="text-base font-semibold mb-2">{t('deviceInfo')}</h3>
                    
                    {/* Afficher le dernier port sauvegardé */}
                    {settings.last_port && (
                        <div className="mb-2 p-2 bg-blue-900/20 border border-blue-700 rounded text-xs">
                          <div className="flex items-center gap-2">
                          <span className="text-blue-400">💾</span>
                          <span className="text-gray-300">{t('lastPortUsed')}</span>
                          <span className="font-mono text-blue-400">{settings.last_port}</span>
                        </div>
                      </div>
                    )}
                    
                      <div className={`p-2 rounded mb-2 text-sm ${info.device.connected ? 'bg-green-900/30 border border-green-700' : 'bg-yellow-900/30 border border-yellow-700'}`}>
                      <div className="flex items-center gap-2">
                        <span className={info.device.connected ? "text-green-400" : "text-yellow-400"}>
                          {info.device.connected ? "●" : "○"}
                        </span>
                        <span className="font-semibold">
                          {info.device.connected ? t('greaseweazleConnected') : t('greaseweazleNotDetected')}
                        </span>
                      </div>
                    </div>
                    {info.device.connected && (
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-2 text-sm">
                        {info.device.port && (
                          <div className="flex justify-between">
                            <span className="text-gray-400">{t('port')}</span>
                            <span className="font-mono text-blue-400">{info.device.port}</span>
                          </div>
                        )}
                        {info.device.model && (
                          <div className="flex justify-between">
                            <span className="text-gray-400">{t('model')}</span>
                            <span className="font-mono">{info.device.model}</span>
                          </div>
                        )}
                        {info.device.firmware && (
                          <div className="flex justify-between">
                            <span className="text-gray-400">{t('firmware')}</span>
                            <span className="font-mono">{info.device.firmware}</span>
                          </div>
                        )}
                        {info.device.mcu && (
                          <div className="flex justify-between">
                            <span className="text-gray-400">{t('mcu')}</span>
                              <span className="font-mono text-xs">{info.device.mcu}</span>
                          </div>
                        )}
                      </div>
                    )}
                    
                    {/* Sélection du lecteur */}
                    <div className="border-t border-gray-700 pt-3 mt-3">
                      <h3 className="text-base font-semibold mb-3">{t('driveSelection')}</h3>
                      {info.device && info.device.connected ? (
                        <>
                        
                        {/* Sélecteur PC/Shugart avec style toggle */}
                        <div className="mb-4">
                          <div className="flex items-center gap-2 mb-2">
                            <span className="text-sm text-gray-400">{t('driveTypePC')}</span>
                            <button
                              onClick={() => {
                                const isPC = selectedDrive === 'A' || selectedDrive === 'B'
                                if (isPC) {
                                  // Passer à Shugart
                                  handleDriveChange('0')
                                } else {
                                  // Passer à PC
                                  handleDriveChange('A')
                                }
                              }}
                              className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
                                (selectedDrive === '0' || selectedDrive === '1' || selectedDrive === '2' || selectedDrive === '3') ? 'bg-blue-600' : 'bg-gray-600'
                              }`}
                            >
                              <span
                                className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                                  (selectedDrive === '0' || selectedDrive === '1' || selectedDrive === '2' || selectedDrive === '3') ? 'translate-x-6' : 'translate-x-1'
                                }`}
                              />
                            </button>
                            <span className="text-sm text-gray-400">{t('driveTypeShugart')}</span>
                          </div>
                          
                          {/* Options PC */}
                          {(selectedDrive === 'A' || selectedDrive === 'B') && (
                            <div className="flex gap-2">
                              <button
                                onClick={() => handleDriveChange('A')}
                                className={`flex-1 px-3 py-2 rounded text-sm font-medium transition-colors ${
                                  selectedDrive === 'A'
                                    ? 'bg-blue-600 text-white'
                                    : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
                                }`}
                              >
                                {t('driveA')}
                              </button>
                              <button
                                onClick={() => handleDriveChange('B')}
                                className={`flex-1 px-3 py-2 rounded text-sm font-medium transition-colors ${
                                  selectedDrive === 'B'
                                    ? 'bg-blue-600 text-white'
                                    : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
                                }`}
                              >
                                {t('driveB')}
                              </button>
                            </div>
                          )}
                          
                          {/* Options Shugart */}
                          {(selectedDrive === '0' || selectedDrive === '1' || selectedDrive === '2' || selectedDrive === '3') && (
                            <div className="grid grid-cols-4 gap-2">
                              {['0', '1', '2', '3'].map((drive) => (
                                <button
                                  key={drive}
                                  onClick={() => handleDriveChange(drive)}
                                  className={`px-3 py-2 rounded text-sm font-medium transition-colors ${
                                    selectedDrive === drive
                                      ? 'bg-blue-600 text-white'
                                      : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
                                  }`}
                                >
                                  {t(`driveDS${drive}` as any)}
                                </button>
                              ))}
                            </div>
                          )}
                        </div>
                        
           {/* Bouton de test */}
           <button
             onClick={handleTestDrive}
             disabled={testingDrive}
             className="w-full px-4 py-2 bg-green-600 hover:bg-green-700 disabled:bg-gray-600 disabled:cursor-not-allowed text-white font-medium rounded transition-colors relative group mb-2"
             title={t('driveTestTooltip')}
           >
             {testingDrive ? t('testingDrive') : t('testDrive')}
             {/* Tooltip */}
             <div className="absolute bottom-full left-0 mb-2 w-64 p-2 bg-gray-800 text-white text-xs rounded shadow-lg opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none z-50">
               {t('driveTestTooltip')}
             </div>
           </button>
           
           {/* Bouton de vérification Track 0 */}
           <button
             onClick={handleVerifyTrack0}
             disabled={verifyingTrack0}
             className="w-full px-4 py-2 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-600 disabled:cursor-not-allowed text-white font-medium rounded transition-colors relative group mb-3"
             title={t('track0VerifyTooltip')}
           >
             {verifyingTrack0 ? t('verifyingTrack0') : t('verifyTrack0')}
             {/* Tooltip */}
             <div className="absolute bottom-full left-0 mb-2 w-64 p-2 bg-gray-800 text-white text-xs rounded shadow-lg opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none z-50">
               {t('track0VerifyTooltip')}
             </div>
           </button>
           
           {/* Résultats de la vérification Track 0 */}
           {track0Result && (
             <div className={`mt-3 p-3 rounded text-sm ${
               track0Result.sensor_ok 
                 ? 'bg-green-900/20 border border-green-700' 
                 : 'bg-yellow-900/20 border border-yellow-700'
             }`}>
               <div className="font-semibold mb-2">
                 {track0Result.sensor_ok ? (
                   <span className="text-green-400">✅ {t('track0SensorOk')}</span>
                 ) : (
                   <span className="text-yellow-400">⚠️ {t('track0SensorWarning')}</span>
                 )}
               </div>
               
               {/* Tests de seek */}
               {track0Result.seek_tests && track0Result.seek_tests.length > 0 && (
                 <div className="mb-2">
                   <div className="text-xs font-semibold mb-1">{t('track0SeekTests')}:</div>
                   <div className="space-y-1">
                     {track0Result.seek_tests.map((test: any, idx: number) => (
                       <div key={idx} className="text-xs flex items-center gap-2">
                         <span>{t('track0FromTrack')} {test.from_track} → {t('track0ToTrack')} {test.to_track}:</span>
                         {test.success ? (
                           <span className="text-green-400">✓ {t('track0Success')}</span>
                         ) : (
                           <span className="text-red-400">✗ {t('track0Failed')}</span>
                         )}
                       </div>
                     ))}
                   </div>
                 </div>
               )}
               
               {/* Tests de lecture */}
               {track0Result.read_tests && (
                 <div className="mb-2">
                   <div className="text-xs font-semibold mb-1">{t('track0ReadTests')}:</div>
                   <div className="text-xs space-y-1">
                     <div>{t('track0ReadingsCount')}: {track0Result.read_tests.readings_count}</div>
                     {track0Result.read_tests.avg_percentage !== null && (
                       <div>{t('track0AvgPercentage')}: {track0Result.read_tests.avg_percentage}%</div>
                     )}
                     {track0Result.read_tests.percentage_variance !== null && (
                       <div>{t('track0PercentageVariance')}: {track0Result.read_tests.percentage_variance}%</div>
                     )}
                   </div>
                 </div>
               )}
               
               {/* Suggestions */}
               {track0Result.suggestions && track0Result.suggestions.length > 0 && (
                 <div className="mt-2">
                   <div className="text-xs font-semibold mb-1">{t('track0Suggestions')}:</div>
                   <ul className="text-xs space-y-1 list-disc list-inside">
                     {track0Result.suggestions.map((suggestion: string, idx: number) => (
                       <li key={idx}>{suggestion}</li>
                     ))}
                   </ul>
                 </div>
               )}
               
               {/* Avertissements */}
               {track0Result.warnings && track0Result.warnings.length > 0 && (
                 <div className="mt-2">
                   <div className="text-xs font-semibold mb-1 text-yellow-400">Avertissements:</div>
                   <ul className="text-xs space-y-1 list-disc list-inside text-yellow-300">
                     {track0Result.warnings.map((warning: string, idx: number) => (
                       <li key={idx}>{warning}</li>
                     ))}
                   </ul>
                 </div>
               )}
             </div>
           )}
           </>
         ) : (
           <div className="text-sm text-gray-400 italic mb-3">
             {t('driveTestNotConnected')}
           </div>
         )}
                      
                      {/* Informations détaillées sur les lecteurs - Toujours visible */}
                      <div className="border-t border-gray-700 pt-3">
                        <button
                          onClick={() => setShowDriveInfo(!showDriveInfo)}
                          className="flex items-center gap-2 text-sm text-blue-400 hover:text-blue-300 transition-colors w-full"
                        >
                          <span>{showDriveInfo ? '▼' : '▶'}</span>
                          <span>{t('driveInfoTitle')}</span>
                        </button>
                        
                        {showDriveInfo && (
                          <div className="mt-3 space-y-4 text-sm">
                            {/* Informations IBM/PC */}
                            <div className="bg-blue-900/20 border border-blue-700 rounded p-3">
                              <h4 className="font-semibold text-blue-300 mb-2">{t('driveInfoPC')}</h4>
                              <p className="text-gray-300 text-xs mb-2">{t('driveInfoPCDesc')}</p>
                              <ul className="list-disc list-inside space-y-1 text-xs text-gray-400 ml-2">
                                <li>{t('driveInfoPC_A')}</li>
                                <li>{t('driveInfoPC_B')}</li>
                              </ul>
                            </div>
                            
                            {/* Informations Shugart */}
                            <div className="bg-purple-900/20 border border-purple-700 rounded p-3">
                              <h4 className="font-semibold text-purple-300 mb-2">{t('driveInfoShugart')}</h4>
                              <p className="text-gray-300 text-xs mb-2">{t('driveInfoShugartDesc')}</p>
                              <p className="text-gray-400 text-xs italic">{t('driveInfoShugartNote')}</p>
                            </div>
                            
                            {/* Dépannage */}
                            <div className="bg-yellow-900/20 border border-yellow-700 rounded p-3">
                              <h4 className="font-semibold text-yellow-300 mb-2">{t('driveInfoTroubleshooting')}</h4>
                              <p className="text-gray-300 text-xs mb-2 font-semibold">{t('driveInfoTrack0Error')}</p>
                              <ul className="list-disc list-inside space-y-1 text-xs text-gray-400 ml-2">
                                <li>{t('driveInfoTrack0Shugart')}</li>
                                <li>{t('driveInfoTrack0PC')}</li>
                              </ul>
                            </div>
                            
                            {/* Lien vers la documentation */}
                            <div className="text-center">
                              <a
                                href="https://github.com/keirf/greaseweazle/wiki/Drive-Select"
                                target="_blank"
                                rel="noopener noreferrer"
                                className="text-xs text-blue-400 hover:text-blue-300 underline"
                              >
                                📖 Documentation complète sur GitHub
                              </a>
                            </div>
                          </div>
                        )}
                      </div>
                    </div>
                  </div>
                </>
              )}
              
                    {detectionResult && (
                  <div className="border-t border-gray-700 pt-3">
                    <h3 className="text-base font-semibold mb-2">{t('detectionResult')}</h3>
                  
                  {/* Afficher si le port sauvegardé a été utilisé */}
                  {detectionResult.connection.last_port && (
                      <div className="mb-2 p-2 bg-blue-900/20 border border-blue-700 rounded text-xs">
                        <div className="flex items-center gap-2">
                          <span className="text-blue-400">⚡</span>
                          <span className="text-gray-300">{t('acceleratedDetection')}</span>
                          <span className="font-mono text-blue-400">{detectionResult.connection.last_port}</span>
                        </div>
                      </div>
                  )}
                  
                    <div className={`p-2 rounded mb-2 text-sm ${detectionResult.greaseweazle_found ? 'bg-green-900/30 border border-green-700' : 'bg-red-900/30 border border-red-700'}`}>
                      <div className="flex items-center gap-2 mb-1">
                      <span className={detectionResult.greaseweazle_found ? "text-green-400" : "text-red-400"}>
                        {detectionResult.greaseweazle_found ? "✓" : "✗"}
                      </span>
                      <span className="font-semibold">
                        {detectionResult.greaseweazle_found 
                          ? `${t('greaseweazleDetectedOn')} ${detectionResult.connection.port || t('unknownPort')}`
                          : t('noGreaseweazleDetected')}
                      </span>
                    </div>
                    {detectionResult.connection.error && (
                        <p className="text-xs text-red-300 mt-1">{detectionResult.connection.error}</p>
                    )}
                      <p className="text-xs text-gray-400 mt-1">
                      {detectionResult.ports_detected} {t('portsDetected')}
                        {detectionResult.ports_shown !== undefined && detectionResult.ports_shown !== detectionResult.ports_detected && (
                        <span className="ml-2">({detectionResult.ports_shown} {t('portsShown')})</span>
                      )}
                    </p>
                  </div>
                  
                  {detectionResult.ports.length > 0 && (
                      <div className="mt-2">
                      <button
                        onClick={() => setPortsExpanded(!portsExpanded)}
                          className="w-full flex items-center justify-between text-xs font-semibold text-gray-400 hover:text-gray-300 transition-colors mb-1"
                      >
                        <span>{t('detectedPorts')} ({detectionResult.ports.length}):</span>
                        <span className={`transform transition-transform ${portsExpanded ? 'rotate-180' : ''}`}>
                          ▼
                        </span>
                      </button>
                      {portsExpanded && (
                          <div className="space-y-1 max-h-48 overflow-y-auto">
                          {detectionResult.ports.map((port, idx) => (
                              <div key={idx} className={`text-xs p-1.5 rounded ${port.is_greaseweazle ? 'bg-green-900/20 border border-green-700/50' : 'bg-gray-700/50'}`}>
                              <div className="flex justify-between items-center">
                                <span className="font-mono">{port.device}</span>
                                {port.is_greaseweazle && (
                                  <span className="text-green-400 text-xs">✓ Greaseweazle</span>
                                )}
                              </div>
                              {port.description && port.description !== "n/a" && (
                                  <div className="text-xs text-gray-400 mt-0.5">{port.description}</div>
                              )}
                              {port.manufacturer && (
                                  <div className="text-xs text-gray-500 mt-0.5">
                                  {port.manufacturer}
                                  {port.product && ` - ${port.product}`}
                                </div>
                              )}
                              {port.vid && port.pid && (
                                  <div className="text-xs text-gray-600 mt-0.5">
                                  VID: {port.vid} PID: {port.pid}
                                </div>
                              )}
                            </div>
                          ))}
                        </div>
                      )}
                    </div>
                  )}
                </div>
              )}
              </div>
            )}
          </div>
        )}

        {/* Onglets pour basculer entre mode auto et manuel - Au-dessus de la grille */}
        <div className="flex gap-2 mb-2 border-b border-gray-700">
            <button
              onClick={() => setActiveTab('auto')}
            className={`px-3 py-1 text-sm font-semibold transition-colors ${
                activeTab === 'auto'
                  ? 'text-blue-400 border-b-2 border-blue-400'
                  : 'text-gray-400 hover:text-gray-300'
              }`}
            >
            {t('automaticMode')}
            </button>
            <button
              onClick={() => setActiveTab('manual')}
            className={`px-3 py-1 text-sm font-semibold transition-colors ${
                activeTab === 'manual'
                  ? 'text-blue-400 border-b-2 border-blue-400'
                  : 'text-gray-400 hover:text-gray-300'
              }`}
            >
            {t('manualMode')}
            </button>
          </div>

        {/* Section des modes d'alignement : 2 colonnes (60% gauche, 40% droite) */}
        <div className="grid xl:grid-cols-[60%_40%] gap-4 items-start">
          {/* Colonne gauche : Contrôles */}
          <div>
          {activeTab === 'auto' ? (
            <>
              {info ? (
                  <AlignmentControl 
                    alignAvailable={info.align_available} 
                    onAlignmentStart={handleAlignmentStart}
                    selectedFormat={sharedFormat}
                    onFormatChange={setSharedFormat}
                  />
              ) : (
                <div className="bg-gray-800 rounded-lg p-6 text-center text-gray-400">
                  {t('loadingGreaseweazleInfo')}
                </div>
              )}
            </>
          ) : (
            <ManualAlignment 
              alignAvailable={info?.align_available ?? false}
              selectedFormat={sharedFormat}
              onFormatChange={setSharedFormat}
                onStateChange={setManualState}
                onLiveReadingsChange={setManualLiveReadings}
                currentPosition={currentPosition}
              />
            )}
          </div>

          {/* Colonne droite : Résultats et Navigation */}
          <div>
            {activeTab === 'auto' && status && status.status !== 'idle' && (
              <div>
                <AlignmentResults status={status.status} />
              </div>
            )}
            {activeTab === 'manual' && (
              <div className="space-y-2">
                {/* Navigation - Toujours visible */}
                <NavigationControl 
                  alignAvailable={info?.align_available ?? false}
                  manualState={manualState}
                  currentPosition={currentPosition}
                  onPositionChange={(position) => {
                    setCurrentPosition(position);
                    // Sauvegarder dans localStorage
                    localStorage.setItem('currentPosition', JSON.stringify(position));
                  }}
                  onStateChange={async () => {
                    // Rafraîchir l'état manuel et mettre à jour la position
                    try {
                      const response = await axios.get('http://localhost:8000/api/manual/state')
                      setManualState(response.data)
                      // Mettre à jour la position sauvegardée depuis le backend
                      if (response.data && (response.data.current_track !== undefined || response.data.current_head !== undefined)) {
                        setCurrentPosition({
                          track: response.data.current_track ?? currentPosition.track,
                          head: response.data.current_head ?? currentPosition.head
                        })
                      }
                    } catch (err) {
                      // Si le mode n'est pas démarré, le backend peut ne pas répondre
                      // Dans ce cas, on garde la position sauvegardée
                    }
                  }}
                />

                {/* Position actuelle - Toujours affichée */}
                <div className="bg-gray-800 rounded-lg p-2">
                  <div className="flex items-center justify-between mb-1">
                    <h3 className="text-sm font-semibold">{t('currentPosition')}</h3>
                    {manualState?.is_running && (
                      <div className="flex items-center gap-2 text-green-400">
                        <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse"></div>
                        <span className="text-xs">{t('continuousStreamActive')}</span>
                      </div>
                    )}
                  </div>
                  <div className="grid grid-cols-2 gap-2 text-sm">
                    <div>
                      <span className="text-gray-400">{t('track')}</span>
                      <span className="ml-2 font-mono text-lg font-bold text-blue-400">
                        {manualState?.current_track ?? currentPosition.track}
                      </span>
                    </div>
                    <div>
                      <span className="text-gray-400">{t('head')}</span>
                      <span className="ml-2 font-mono text-lg font-bold text-blue-400">
                        {manualState?.current_head ?? currentPosition.head}
                      </span>
                    </div>
                    <div className="col-span-2">
                      <span className="text-gray-400">{t('position')}</span>
                      <span className="ml-2 font-mono">
                        T{manualState?.current_track ?? currentPosition.track}.{manualState?.current_head ?? currentPosition.head}
                      </span>
                    </div>
                  </div>
                </div>

                {/* Dernière analyse */}
                {manualState && manualState.last_reading && (
                  <div className="bg-gray-800 rounded-lg p-2">
                    <h3 className="text-sm font-semibold mb-1">{t('lastAnalysis')}</h3>
                    <div className="space-y-1 text-xs">
                      <div className="flex items-center justify-between">
                        <span className="text-gray-400">{t('percentage')}</span>
                        <span className={`text-lg font-bold ${
                          manualState.last_reading.quality === 'Perfect' ? 'text-green-400' :
                          manualState.last_reading.quality === 'Good' ? 'text-blue-400' :
                          manualState.last_reading.quality === 'Average' ? 'text-yellow-400' :
                          'text-red-400'
                        }`}>
                          {manualState.last_reading.percentage.toFixed(2)}%
                        </span>
                      </div>
                      <div className="flex items-center justify-between">
                        <span className="text-gray-400">{t('quality')}</span>
                        <span className={`font-semibold ${
                          manualState.last_reading.quality === 'Perfect' ? 'text-green-400' :
                          manualState.last_reading.quality === 'Good' ? 'text-blue-400' :
                          manualState.last_reading.quality === 'Average' ? 'text-yellow-400' :
                          'text-red-400'
                        }`}>
                          {manualState.last_reading.quality}
                        </span>
                      </div>
                      <div className="flex items-center justify-between">
                        <span className="text-gray-400">{t('sectors')}</span>
                        <span className="font-mono">
                          {manualState.last_reading.sectors_detected}/{manualState.last_reading.sectors_expected}
                        </span>
                      </div>
                    </div>
                  </div>
                )}

                {/* Historique des lectures récentes - En bas à droite - Version compacte pour mode Direct */}
                {manualState && manualState.is_running && manualLiveReadings.length > 0 && manualState.alignment_mode !== 'direct' && (
                  <div className="bg-gray-800 rounded-lg p-2">
                    <h3 className="text-sm font-semibold mb-1">📊 Historique des lectures</h3>
                    <div className="space-y-0.5 max-h-24 overflow-y-auto">
                      {manualLiveReadings.slice(-5).reverse().map((reading, idx) => (
                        <div key={idx} className="bg-gray-700/50 rounded p-1 text-xs">
                          <div className="flex items-center justify-between">
                            <div className="flex items-center gap-2">
                              <span className="text-gray-400">#{reading.reading_number}</span>
                              <span className="font-mono text-blue-400">
                                T{reading.track}.{reading.head}
                              </span>
                            </div>
                            <span className={`font-bold ${
                              reading.percentage >= 99 ? 'text-green-400' :
                              reading.percentage >= 97 ? 'text-blue-400' :
                              reading.percentage >= 95 ? 'text-yellow-400' :
                              'text-red-400'
                            }`}>
                              {reading.percentage.toFixed(1)}%
                            </span>
                          </div>
                          <div className="flex items-center justify-between mt-0.5 text-gray-400">
                            <span className="font-mono text-xs">
                              {reading.sectors_detected}/{reading.sectors_expected} secteurs
                            </span>
                            {reading.timing && reading.timing.elapsed_ms && (
                              <span className="text-xs">
                                {reading.timing.elapsed_ms.toFixed(0)}ms
                              </span>
                            )}
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* Informations contextuelles et raccourcis clavier */}
                <div className="bg-gray-800 rounded-lg p-3">
                  <h3 className="text-base font-semibold mb-1.5">{t('help')}</h3>
                  <div className="space-y-1 text-xs text-gray-300 mb-2">
                    <p>
                      <strong className="text-blue-400">{t('helpNavigationTitle')}:</strong> {t('helpNavigation')}
                    </p>
                    <p>
                      <strong className="text-green-400">{t('helpAnalyzeTitle')}:</strong> {t('helpAnalyze')}
                    </p>
                    {(!manualState || !manualState.is_running) && (
                      <p>
                        <strong className="text-purple-400">{t('helpModeTitle')}:</strong> {t('helpMode')}
                      </p>
                    )}
                  </div>
                  
                  {/* Raccourcis clavier */}
                  <div className="border-t border-gray-700 pt-1.5">
                    <h4 className="text-sm font-semibold mb-1 text-gray-300">{t('keyboardShortcuts')}</h4>
                    <div className="text-xs text-gray-400">
                      <div className="grid grid-cols-2 gap-x-3 gap-y-0.5">
                        <div className="flex items-center gap-1">
                          <kbd className="bg-gray-700 px-1.5 py-0.5 rounded text-xs">Espace</kbd>
                          <span>: {t('startStopShortcut')}</span>
                        </div>
                        <div className="flex items-center gap-1">
                          <kbd className="bg-gray-700 px-1.5 py-0.5 rounded text-xs">+</kbd>
                          <span>/</span>
                          <kbd className="bg-gray-700 px-1.5 py-0.5 rounded text-xs">-</kbd>
                          <span>: {t('moveOneTrack')}</span>
                        </div>
                        <div className="flex items-center gap-1">
                          <kbd className="bg-gray-700 px-1.5 py-0.5 rounded text-xs">1-8</kbd>
                          <span>: {t('jumpToTrack')}</span>
                        </div>
                        <div className="flex items-center gap-1">
                          <kbd className="bg-gray-700 px-1.5 py-0.5 rounded text-xs">H</kbd>
                          <span>: {t('changeHeadShortcut')}</span>
                        </div>
                        <div className="flex items-center gap-1">
                          <kbd className="bg-gray-700 px-1.5 py-0.5 rounded text-xs">R</kbd>
                          <span>: {t('recalibrateShortcut')}</span>
                        </div>
                        <div className="flex items-center gap-1">
                          <kbd className="bg-gray-700 px-1.5 py-0.5 rounded text-xs">A</kbd>
                          <span>: {t('analyzeShortcut')}</span>
                        </div>
                      </div>
                      {manualState && manualState.is_running && (
                        <div className="text-xs text-gray-500 mt-1 pt-1 border-t border-gray-700">
                          {t('continuousReadingsTip')}
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}

export default App
