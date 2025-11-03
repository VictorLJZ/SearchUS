'use client';

import { SearchResult } from '@/types';
import { MapPin, Navigation, ExternalLink } from 'lucide-react';
import { generateGoogleMapsUrl, generateStreetViewUrl } from '@/utils/maps';

interface ResultCardProps {
  result: SearchResult;
  index: number;
}

export default function ResultCard({ result, index }: ResultCardProps) {
  const mapsUrl = generateGoogleMapsUrl(result.lat, result.lon);
  const streetViewUrl = generateStreetViewUrl(result.lat, result.lon, result.heading);

  return (
    <div className="bg-white rounded-lg border border-gray-200 p-4 hover:shadow-md transition-shadow">
      <div className="flex items-start justify-between mb-3">
        <div className="flex items-center gap-2">
          <span className="text-lg font-bold text-blue-600">#{index + 1}</span>
          <span className="text-sm font-semibold text-gray-900">
            {(result.score * 100).toFixed(1)}% match
          </span>
        </div>
      </div>

      <div className="space-y-2 mb-4">
        <div className="flex items-center gap-2 text-sm text-gray-600">
          <MapPin className="w-4 h-4" />
          <span>
            {result.lat.toFixed(6)}, {result.lon.toFixed(6)}
          </span>
        </div>
        <div className="flex items-center gap-2 text-sm text-gray-600">
          <Navigation className="w-4 h-4" />
          <span>Heading: {result.heading}°</span>
        </div>
        {result.city && (
          <div className="text-sm text-gray-600">
            {result.city}, {result.country}
          </div>
        )}
        <div className="text-xs text-gray-400 font-mono truncate">
          {result.filename}
        </div>
      </div>

      <div className="flex gap-2">
        <a
          href={mapsUrl}
          target="_blank"
          rel="noopener noreferrer"
          className="flex-1 px-3 py-2 bg-blue-600 text-white text-sm rounded-lg hover:bg-blue-700 transition-colors flex items-center justify-center gap-2"
        >
          <MapPin className="w-4 h-4" />
          Maps
        </a>
        <a
          href={streetViewUrl}
          target="_blank"
          rel="noopener noreferrer"
          className="flex-1 px-3 py-2 bg-green-600 text-white text-sm rounded-lg hover:bg-green-700 transition-colors flex items-center justify-center gap-2"
        >
          <ExternalLink className="w-4 h-4" />
          Street View
        </a>
      </div>
    </div>
  );
}

