'use client';

import { SearchResult } from '@/types';
import ResultCard from './ResultCard';

interface ResultsListProps {
  results: SearchResult[];
  queryType?: 'text' | 'image';
}

export default function ResultsList({ results, queryType }: ResultsListProps) {
  if (results.length === 0) {
    return (
      <div className="text-center py-12">
        <p className="text-gray-500 text-lg">No results found</p>
        <p className="text-gray-400 text-sm mt-2">
          Try a different {queryType === 'image' ? 'image' : 'search query'}
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-xl font-bold text-gray-900">
          Search Results ({results.length})
        </h2>
      </div>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {results.map((result, index) => (
          <ResultCard key={result.filename} result={result} index={index} />
        ))}
      </div>
    </div>
  );
}

