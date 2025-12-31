import { useState, useEffect } from 'react';
import axios from 'axios';

interface Settings {
  last_port: string | null;
  last_port_date: string | null;
}

const API_URL = 'http://localhost:8000/api';

export function useSettings() {
  const [settings, setSettings] = useState<Settings>({
    last_port: null,
    last_port_date: null,
  });
  const [loading, setLoading] = useState(true);

  const fetchSettings = async () => {
    try {
      const response = await axios.get<Settings & { all_settings: any }>(`${API_URL}/settings`);
      setSettings({
        last_port: response.data.last_port,
        last_port_date: response.data.last_port_date,
      });
    } catch (error) {
      console.error('Error fetching settings:', error);
    } finally {
      setLoading(false);
    }
  };

  const saveLastPort = async (port: string) => {
    try {
      await axios.post(`${API_URL}/settings/last_port`, { port }, {
        headers: { 'Content-Type': 'application/json' },
      });
      setSettings((prev) => ({
        ...prev,
        last_port: port,
        last_port_date: new Date().toISOString(),
      }));
    } catch (error) {
      console.error('Error saving port:', error);
    }
  };

  useEffect(() => {
    fetchSettings();
  }, []);

  return {
    settings,
    loading,
    saveLastPort,
    refreshSettings: fetchSettings,
  };
}

