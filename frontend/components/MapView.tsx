'use client';

import { SearchResult } from '@/types';
import { MapPin } from 'lucide-react';
import { generateGoogleMapsUrl, generateStreetViewUrl } from '@/utils/maps';

interface MapViewProps {
  results: SearchResult[];
}

export default function MapView({ results }: MapViewProps) {
  if (results.length === 0) {
    return null;
  }

  // Use top result for map center
  const topResult = results[0];

  // Generate Google Maps embed URL
  const mapEmbedUrl = `https://www.google.com/maps/embed/v1/place?key=${process.env.NEXT_PUBLIC_GOOGLE_MAPS_API_KEY || ''}&q=${topResult.lat},${topResult.lon}&zoom=15`;

  // If no API key, show direct link instead
  if (!process.env.NEXT_PUBLIC_GOOGLE_MAPS_API_KEY) {
    return (
      <div className="bg-white rounded-lg border border-gray-200 p-6">
        <h3 className="text-lg font-bold text-gray-900 mb-4">Location Map</h3>
        <div className="space-y-4">
          <div className="bg-gray-100 rounded-lg p-8 text-center">
            <MapPin className="w-12 h-12 text-gray-400 mx-auto mb-2" />
            <p className="text-gray-600 mb-4">
              Top result location: {topResult.lat.toFixed(6)}, {topResult.lon.toFixed(6)}
            </p>
            <a
              href={generateGoogleMapsUrl(topResult.lat, topResult.lon)}
              target="_blank"
              rel="noopener noreferrer"
              className="inline-block px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
            >
              Open in Google Maps
            </a>
          </div>
          <div className="grid grid-cols-2 gap-2">
            {results.slice(0, 4).map((result, index) => (
              <a
                key={result.filename}
                href={generateGoogleMapsUrl(result.lat, result.lon)}
                target="_blank"
                rel="noopener noreferrer"
                className="p-3 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors text-sm"
              >
                <div className="font-medium">Result #{index + 1}</div>
                <div className="text-gray-600 text-xs">
                  {result.lat.toFixed(4)}, {result.lon.toFixed(4)}
                </div>
              </a>
            ))}
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg border border-gray-200 p-6">
      <h3 className="text-lg font-bold text-gray-900 mb-4">Location Map</h3>
      <div className="rounded-lg overflow-hidden border border-gray-200">
        <iframe
          width="100%"
          height="400"
          style={{ border: 0 }}
          loading="lazy"
          allowFullScreen
          referrerPolicy="no-referrer-when-downgrade"
          src={mapEmbedUrl}
        />
      </div>
      <div className="mt-4 grid grid-cols-2 gap-2">
        {results.slice(0, 4).map((result, index) => (
          <a
            key={result.filename}
            href={generateGoogleMapsUrl(result.lat, result.lon)}
            target="_blank"
            rel="noopener noreferrer"
            className="p-3 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors text-sm"
          >
            <div className="font-medium">Result #{index + 1}</div>
            <div className="text-gray-600 text-xs">
              {result.lat.toFixed(4)}, {result.lon.toFixed(4)}
            </div>
          </a>
        ))}
      </div>
    </div>
  );
}

