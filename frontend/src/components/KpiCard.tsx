interface KpiCardProps {
  title: string;
  value: string | number;
  unit?: string;
  isEmpty?: boolean;
}

export function KpiCard({ title, value, unit, isEmpty }: KpiCardProps) {
  return (
    <div className="kpi-card">
      <p className="kpi-title">{title}</p>
      {isEmpty ? (
        <p className="kpi-empty">데이터 없음</p>
      ) : (
        <p className="kpi-value">
          {value}
          {unit && <span className="kpi-unit"> {unit}</span>}
        </p>
      )}
    </div>
  );
}
