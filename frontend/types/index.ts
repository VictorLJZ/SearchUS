/**
 * TypeScript type definitions
 */

export interface SearchResult {
  filename: string;
  score: number;
  lat: number;
  lon: number;
  heading: number;
  city?: string;
  country: string;
  metadata: Record<string, any>;
}

export interface SearchResponse {
  results: SearchResult[];
  query_type: 'text' | 'image';
  query?: string;
  total_results: number;
}

export interface TextSearchRequest {
  query: string;
  top_k?: number;
}

export interface ImageSearchRequest {
  file: File;
  top_k?: number;
}

