import { useState, useEffect } from 'react';
import { KpiCard } from './components/KpiCard';
import { TypeBadge } from './components/TypeBadge';
import { useWebSocket } from './hooks/useWebSocket';
import type { KPIData, TimeRange } from './types';
import './App.css';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const TIME_RANGE_OPTIONS: { label: string; value: TimeRange; minutes: number }[] = [
  { label: '최근 5분', value: '5m', minutes: 5 },
  { label: '최근 30분', value: '30m', minutes: 30 },
];

function App() {
  const { kpiData: wsKpiData, isConnected } = useWebSocket();
  const [timeRange, setTimeRange] = useState<TimeRange>('5m');
  const [statsData, setStatsData] = useState<KPIData | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [lastUpdated, setLastUpdated] = useState<string>('');

  const fetchStats = async (range: TimeRange) => {
    setIsLoading(true);
    try {
      const minutes = TIME_RANGE_OPTIONS.find((o) => o.value === range)!.minutes;
      const to = new Date();
      const from = new Date(to.getTime() - minutes * 60 * 1000);

      const toISO = to.toISOString().slice(0, 19);
      const fromISO = from.toISOString().slice(0, 19);

      const res = await fetch(`${API_URL}/stats?from=${fromISO}&to=${toISO}`);
      const data = await res.json();

      setStatsData({
        total_count: data.total_count,
        avg_speed: data.avg_speed,
        by_type: data.by_type,
        timestamp: new Date().toISOString(),
      });
      setLastUpdated(new Date().toLocaleTimeString('ko-KR'));
    } catch (e) {
      console.error('통계 조회 실패:', e);
    } finally {
      setIsLoading(false);
    }
  };

  // 시간 범위 변경 시 즉시 조회
  useEffect(() => {
    fetchStats(timeRange);
  }, [timeRange]);

  // WebSocket으로 새 데이터 오면 stats 갱신
  useEffect(() => {
    if (wsKpiData) {
      fetchStats(timeRange);
    }
  }, [wsKpiData]);

  const isEmpty = !statsData || statsData.total_count === 0;

  return (
    <div className="dashboard">
      <header className="header">
        <div className="header-left">
          <h1 className="header-title">GreenAI Dashboard</h1>
          <span className={`status-badge ${isConnected ? 'connected' : 'disconnected'}`}>
            {isConnected ? '● 실시간 연결 중' : '○ 연결 끊김'}
          </span>
        </div>
        <div className="header-right">
          <select
            className="time-select"
            value={timeRange}
            onChange={(e) => setTimeRange(e.target.value as TimeRange)}
          >
            {TIME_RANGE_OPTIONS.map((opt) => (
              <option key={opt.value} value={opt.value}>
                {opt.label}
              </option>
            ))}
          </select>
          {lastUpdated && (
            <span className="last-updated">마지막 갱신: {lastUpdated}</span>
          )}
        </div>
      </header>

      <main className="main">
        {isLoading ? (
          <div className="loading">데이터 불러오는 중...</div>
        ) : (
          <>
            <section className="kpi-section">
              <KpiCard
                title="총 감지 수"
                value={statsData?.total_count ?? 0}
                unit="건"
                isEmpty={isEmpty}
              />
              <KpiCard
                title="평균 속도"
                value={statsData?.avg_speed ?? '-'}
                unit="m/s"
                isEmpty={isEmpty || statsData?.avg_speed === null}
              />
            </section>

            <section className="type-section">
              <h2 className="section-title">타입별 감지 현황</h2>
              <TypeBadge stats={statsData?.by_type ?? []} />
            </section>
          </>
        )}
      </main>
    </div>
  );
}

export default App;
