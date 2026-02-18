import type { ObjectTypeStats } from '../types';

const TYPE_LABELS: Record<string, string> = {
  Pedestrian: '보행자',
  Bike: '자전거',
  Vehicle: '차량',
  LargeVehicle: '대형차량',
};

const TYPE_COLORS: Record<string, string> = {
  Pedestrian: '#4CAF50',
  Bike: '#2196F3',
  Vehicle: '#FF9800',
  LargeVehicle: '#F44336',
};

interface TypeBadgeProps {
  stats: ObjectTypeStats[];
}

export function TypeBadge({ stats }: TypeBadgeProps) {
  if (stats.length === 0) {
    return <p className="kpi-empty">데이터 없음</p>;
  }

  return (
    <div className="type-badge-list">
      {stats.map((stat) => (
        <div key={stat.type} className="type-badge">
          <span
            className="type-dot"
            style={{ backgroundColor: TYPE_COLORS[stat.type] ?? '#999' }}
          />
          <span className="type-label">{TYPE_LABELS[stat.type] ?? stat.type}</span>
          <span className="type-count">{stat.count}건</span>
          {stat.avg_speed !== null && (
            <span className="type-speed">{stat.avg_speed} m/s</span>
          )}
        </div>
      ))}
    </div>
  );
}
