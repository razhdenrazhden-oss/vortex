import { useMemo } from 'react';

function decodePolyline(str: string): Array<[number, number]> {
  const points: Array<[number, number]> = [];
  let index = 0;
  let lat = 0;
  let lng = 0;

  while (index < str.length) {
    let b;
    let shift = 0;
    let result = 0;
    do {
      b = str.charCodeAt(index++) - 63;
      result |= (b & 0x1f) << shift;
      shift += 5;
    } while (b >= 0x20);
    lat += result & 1 ? ~(result >> 1) : result >> 1;

    shift = 0;
    result = 0;
    do {
      b = str.charCodeAt(index++) - 63;
      result |= (b & 0x1f) << shift;
      shift += 5;
    } while (b >= 0x20);
    lng += result & 1 ? ~(result >> 1) : result >> 1;

    points.push([lat / 1e5, lng / 1e5]);
  }

  return points;
}

export default function MiniRouteMap({ polyline }: { polyline?: string | null }) {
  const path = useMemo(() => {
    if (!polyline) return '';
    try {
      const pts = decodePolyline(polyline);
      if (pts.length < 2) return '';
      const lats = pts.map((p) => p[0]);
      const lngs = pts.map((p) => p[1]);
      const minLat = Math.min(...lats);
      const maxLat = Math.max(...lats);
      const minLng = Math.min(...lngs);
      const maxLng = Math.max(...lngs);
      const dx = maxLng - minLng || 1;
      const dy = maxLat - minLat || 1;
      return pts
        .map(([lat, lng], i) => `${i === 0 ? 'M' : 'L'} ${((lng - minLng) / dx) * 96 + 2} ${98 - ((lat - minLat) / dy) * 96}`)
        .join(' ');
    } catch {
      return '';
    }
  }, [polyline]);

  return (
    <div className="mt-2 rounded-lg border border-slate-700 bg-slate-900">
      <svg viewBox="0 0 100 100" className="h-24 w-full" preserveAspectRatio="none">
        {path ? <path d={path} stroke="#22c55e" strokeWidth={2} fill="none" /> : <text x="8" y="55" fill="#94a3b8" fontSize="10">No route polyline</text>}
      </svg>
    </div>
  );
}
