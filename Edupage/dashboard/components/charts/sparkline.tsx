interface SparklineProps {
  values: number[];
  color?: string;
}

export function Sparkline({ values, color = '#a855f7' }: SparklineProps) {
  if (!values.length) return null;
  const width = 120;
  const height = 40;
  const max = Math.max(...values);
  const min = Math.min(...values);
  const range = max - min || 1;
  const points = values
    .map((v, i) => {
      const x = (i / Math.max(values.length - 1, 1)) * width;
      const y = height - ((v - min) / range) * height;
      return `${x},${y}`;
    })
    .join(' ');

  return (
    <svg className="sparkline" width={width} height={height} viewBox={`0 0 ${width} ${height}`}>
      <polyline points={`0,${height} ${points} ${width},${height}`} fill="url(#gradient)" stroke="none" />
      <defs>
        <linearGradient id="gradient" x1="0" x2="0" y1="0" y2="1">
          <stop offset="0%" stopColor={`${color}66`} />
          <stop offset="100%" stopColor="transparent" />
        </linearGradient>
      </defs>
      <polyline points={points} fill="none" stroke={color} strokeWidth={2.5} />
    </svg>
  );
}
