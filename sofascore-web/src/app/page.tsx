'use client';

import { useState, useEffect, useCallback } from 'react';

interface Match {
  id: number;
  homeTeam: {
    name: string;
    shortName: string;
  };
  awayTeam: {
    name: string;
    shortName: string;
  };
  startTimestamp: number;
  tournament: {
    name: string;
  };
  status: {
    code: number;
    description: string;
  };
}

interface SofaScoreData {
  events: Match[];
  ip_used?: string;
  error?: string;
}

export default function Home() {
  const [selectedDate, setSelectedDate] = useState('2025-10-08');
  const [data, setData] = useState<SofaScoreData | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchData = useCallback(async (date: string) => {
    setLoading(true);
    setError(null);
    try {
      const response = await fetch(`/api/scorelive/matches/${date}`);
      const result = await response.json();
      setData(result);
    } catch (err) {
      setError('Veri çekilirken hata oluştu');
      console.error('API Error:', err);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchData(selectedDate);
  }, [selectedDate, fetchData]); // selectedDate veya fetchData değiştiğinde çalış

  const formatDate = (timestamp: number) => {
    return new Date(timestamp * 1000).toLocaleString('tr-TR');
  };

  const getStatusColor = (code: number) => {
    switch (code) {
      case 0: return 'text-gray-500'; // Not started
      case 100: return 'text-green-500'; // Finished
      case 1: return 'text-blue-500'; // Live
      default: return 'text-gray-500';
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      <div className="container mx-auto px-4 py-8">
        <div className="max-w-6xl mx-auto">
          <h1 className="text-3xl font-bold text-center mb-8 text-gray-900 dark:text-white">
            SofaScore Maç Sonuçları
          </h1>
          
          {/* Tarih Seçici */}
          <div className="mb-8 flex justify-center">
            <div className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow-md">
              <label htmlFor="date" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Tarih Seçin:
              </label>
              <input
                type="date"
                id="date"
                value={selectedDate}
                onChange={(e) => setSelectedDate(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white"
              />
            </div>
          </div>

          {/* Loading */}
          {loading && (
            <div className="text-center py-8">
              <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div>
              <p className="mt-2 text-gray-600 dark:text-gray-400">Veriler yükleniyor...</p>
            </div>
          )}

          {/* Error */}
          {error && (
            <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
              {error}
            </div>
          )}

          {/* API Error */}
          {data?.error && (
            <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
              API Hatası: {data.error}
            </div>
          )}

          {/* IP Bilgisi */}
          {data?.ip_used && (
            <div className="mb-4 text-center">
              <span className="text-sm text-gray-600 dark:text-gray-400">
                Kullanılan IP: {data.ip_used}
              </span>
            </div>
          )}

          {/* Maç Listesi */}
          {data?.events && data.events.length > 0 && (
            <div className="grid gap-4">
              {data.events.map((match) => (
                <div
                  key={match.id}
                  className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6 hover:shadow-lg transition-shadow"
                >
                  <div className="flex items-center justify-between">
                    <div className="flex-1">
                      <div className="flex items-center justify-between mb-2">
                        <div className="text-sm text-gray-500 dark:text-gray-400">
                          {match.tournament.name}
                        </div>
                        <div className={`text-sm font-medium ${getStatusColor(match.status.code)}`}>
                          {match.status.description}
                        </div>
                      </div>
                      
                      <div className="flex items-center justify-between">
                        <div className="text-left">
                          <div className="font-semibold text-lg text-gray-900 dark:text-white">
                            {match.homeTeam.name}
                          </div>
                          <div className="text-sm text-gray-500 dark:text-gray-400">
                            {match.homeTeam.shortName}
                          </div>
                        </div>
                        
                        <div className="text-center mx-4">
                          <div className="text-xs text-gray-500 dark:text-gray-400">
                            {formatDate(match.startTimestamp)}
                          </div>
                        </div>
                        
                        <div className="text-right">
                          <div className="font-semibold text-lg text-gray-900 dark:text-white">
                            {match.awayTeam.name}
                          </div>
                          <div className="text-sm text-gray-500 dark:text-gray-400">
                            {match.awayTeam.shortName}
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}

          {/* Boş Durum */}
          {data?.events && data.events.length === 0 && !loading && (
            <div className="text-center py-8">
              <p className="text-gray-600 dark:text-gray-400">
                Seçilen tarihte maç bulunamadı.
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
