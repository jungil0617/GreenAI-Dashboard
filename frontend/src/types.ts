export interface ObjectTypeStats {
  type: 'Pedestrian' | 'Bike' | 'Vehicle' | 'LargeVehicle';
  count: number;
  avg_speed: number | null;
}

export interface KPIData {
  total_count: number;
  avg_speed: number | null;
  by_type: ObjectTypeStats[];
  timestamp: string;
}

export type TimeRange = '5m' | '30m';
