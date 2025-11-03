'use client';

import { useState } from 'react';
import ImageUpload from '@/components/ImageUpload';
import TextSearch from '@/components/TextSearch';
import ResultsList from '@/components/ResultsList';
import MapView from '@/components/MapView';
import LoadingSpinner from '@/components/LoadingSpinner';
import { SearchResult } from '@/types';
import { searchByText, searchByImage } from '@/lib/api';
import { Search, Image as ImageIcon, AlertCircle } from 'lucide-react';

type SearchType = 'text' | 'image';

export default function Home() {
  const [searchType, setSearchType] = useState<SearchType>('text');
  const [results, setResults] = useState<SearchResult[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleTextSearch = async (query: string) => {
    setLoading(true);
    setError(null);
    setResults([]);

    try {
      const response = await searchByText(query);
      setResults(response.results);
    } catch (err: any) {
      setError(err.message || 'An error occurred during search');
      console.error('Search error:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleImageSearch = async (file: File) => {
    setLoading(true);
    setError(null);
    setResults([]);

    try {
      const response = await searchByImage(file);
      setResults(response.results);
    } catch (err: any) {
      setError(err.message || 'An error occurred during search');
      console.error('Search error:', err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white border-b border-gray-200 shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <h1 className="text-3xl font-bold text-gray-900">SearchUS</h1>
          <p className="text-gray-600 mt-1">Search San Francisco Street View Images</p>
        </div>
      </header>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Search Type Toggle */}
        <div className="mb-6">
          <div className="inline-flex rounded-lg border border-gray-300 bg-white p-1">
            <button
              onClick={() => {
                setSearchType('text');
                setResults([]);
                setError(null);
              }}
              className={`
                px-4 py-2 rounded-md text-sm font-medium transition-colors flex items-center gap-2
                ${
                  searchType === 'text'
                    ? 'bg-blue-600 text-white'
                    : 'text-gray-700 hover:bg-gray-100'
                }
              `}
            >
              <Search className="w-4 h-4" />
              Text Search
            </button>
            <button
              onClick={() => {
                setSearchType('image');
                setResults([]);
                setError(null);
              }}
              className={`
                px-4 py-2 rounded-md text-sm font-medium transition-colors flex items-center gap-2
                ${
                  searchType === 'image'
                    ? 'bg-blue-600 text-white'
                    : 'text-gray-700 hover:bg-gray-100'
                }
              `}
            >
              <ImageIcon className="w-4 h-4" />
              Image Search
            </button>
          </div>
        </div>

        {/* Search Area */}
        <div className="bg-white rounded-lg border border-gray-200 shadow-sm p-6 mb-8">
          {searchType === 'text' ? (
            <TextSearch onSearch={handleTextSearch} disabled={loading} />
          ) : (
            <ImageUpload onUpload={handleImageSearch} disabled={loading} />
          )}
        </div>

        {/* Error Message */}
        {error && (
          <div className="mb-6 bg-red-50 border border-red-200 rounded-lg p-4 flex items-center gap-3">
            <AlertCircle className="w-5 h-5 text-red-600 flex-shrink-0" />
            <p className="text-red-800">{error}</p>
          </div>
        )}

        {/* Loading State */}
        {loading && (
          <div className="mb-8">
            <LoadingSpinner text="Searching..." size="lg" />
          </div>
        )}

        {/* Results */}
        {!loading && results.length > 0 && (
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
            <div className="lg:col-span-2">
              <ResultsList results={results} queryType={searchType} />
            </div>
            <div className="lg:col-span-1">
              <MapView results={results} />
            </div>
          </div>
        )}

        {/* Empty State */}
        {!loading && results.length === 0 && !error && (
          <div className="text-center py-12 bg-white rounded-lg border border-gray-200">
            <Search className="w-12 h-12 text-gray-400 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">
              Ready to search
            </h3>
            <p className="text-gray-500">
              {searchType === 'text'
                ? 'Enter a text query to find similar Street View images'
                : 'Upload an image to find similar Street View images'}
            </p>
          </div>
        )}
      </div>

      {/* Footer */}
      <footer className="mt-16 border-t border-gray-200 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <p className="text-center text-gray-500 text-sm">
            SearchUS - Powered by Cohere, Pinecone, and Google Street View
          </p>
        </div>
      </footer>
    </main>
  );
}

