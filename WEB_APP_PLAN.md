# Web App Development Plan: Next.js + FastAPI

## Overview
Build a web interface that allows users to upload images or enter text queries, search the Pinecone database, and view results with Google Maps integration.

---

## Technology Stack

### Backend
- **FastAPI** - Python web framework for API endpoints
- **Python 3.x** - Existing search functions from `embed/search_images.py`
- **Existing dependencies** - Cohere, Pinecone, PIL, etc.

### Frontend
- **Next.js 14** - React framework with App Router
- **TypeScript** - Type safety (optional but recommended)
- **Tailwind CSS** - Styling
- **Google Maps JavaScript API** - Map integration
- **React Hook Form** - Form handling (optional)
- **Axios** - API client

---

## Project Structure

```
SearchUS/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py              # FastAPI app setup
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   └── search.py         # Search endpoints
│   │   ├── services/
│   │   │   ├── __init__.py
│   │   │   └── search_service.py # Wrap search functions
│   │   └── utils/
│   │       ├── __init__.py
│   │       └── image_utils.py    # Image processing helpers
│   ├── requirements.txt
│   └── .env
│
├── frontend/
│   ├── app/                      # Next.js App Router
│   │   ├── layout.tsx
│   │   ├── page.tsx              # Main search page
│   │   └── api/                  # API routes (if needed)
│   ├── components/
│   │   ├── ImageUpload.tsx
│   │   ├── TextSearch.tsx
│   │   ├── ResultsList.tsx
│   │   ├── ResultCard.tsx
│   │   ├── MapView.tsx
│   │   └── LoadingSpinner.tsx
│   ├── lib/
│   │   └── api.ts                # API client functions
│   ├── utils/
│   │   └── maps.ts               # Google Maps URL helpers
│   ├── types/
│   │   └── index.ts              # TypeScript types
│   ├── public/
│   ├── package.json
│   ├── next.config.js
│   └── tailwind.config.js
│
└── embed/                        # Existing code (unchanged)
    └── search_images.py
```

---

## Phase 1: Backend Setup

### Step 1.1: Create Backend Directory Structure
- [ ] Create `backend/` directory
- [ ] Create `backend/app/` directory
- [ ] Create `backend/app/api/` directory
- [ ] Create `backend/app/services/` directory
- [ ] Create `backend/app/utils/` directory

### Step 1.2: Set Up Backend Dependencies
- [ ] Create `backend/requirements.txt`
- [ ] Add FastAPI: `fastapi==0.104.1`
- [ ] Add CORS middleware: `fastapi` (includes CORS)
- [ ] Add file upload support: `python-multipart`
- [ ] Add Uvicorn server: `uvicorn[standard]==0.24.0`
- [ ] Keep existing dependencies: `cohere`, `pinecone`, `pillow`, `python-dotenv`

### Step 1.3: Create Backend Service Layer
- [ ] Create `backend/app/services/search_service.py`
- [ ] Import functions from `embed/search_images.py`
- [ ] Create wrapper functions for image search
- [ ] Create wrapper functions for text search
- [ ] Handle file uploads (convert uploaded file to image path)
- [ ] Format results as JSON-serializable dictionaries

### Step 1.4: Create Backend API Endpoints
- [ ] Create `backend/app/api/search.py`
- [ ] Create POST endpoint: `/api/search/image`
  - Accept multipart/form-data with image file
  - Process image upload
  - Call search service
  - Return JSON results
- [ ] Create POST endpoint: `/api/search/text`
  - Accept JSON with query text
  - Call search service
  - Return JSON results
- [ ] Add error handling for both endpoints
- [ ] Add request validation

### Step 1.5: Create FastAPI Main App
- [ ] Create `backend/app/main.py`
- [ ] Initialize FastAPI app
- [ ] Add CORS middleware (allow frontend origin)
- [ ] Include API router
- [ ] Add health check endpoint
- [ ] Load environment variables

### Step 1.6: Test Backend Locally
- [ ] Create `.env` file in backend/ (copy from root)
- [ ] Run backend: `uvicorn app.main:app --reload --port 8000`
- [ ] Test `/api/search/text` endpoint with curl/Postman
- [ ] Test `/api/search/image` endpoint with curl/Postman
- [ ] Verify CORS headers are set correctly

---

## Phase 2: Frontend Setup

### Step 2.1: Initialize Next.js Project
- [ ] Run `npx create-next-app@latest frontend`
- [ ] Choose TypeScript: Yes
- [ ] Choose ESLint: Yes
- [ ] Choose Tailwind CSS: Yes
- [ ] Choose App Router: Yes
- [ ] Choose src/ directory: No (use app/ directly)
- [ ] Choose import alias: Yes (@/*)

### Step 2.2: Install Additional Dependencies
- [ ] Install Axios: `npm install axios`
- [ ] Install Google Maps types: `npm install @types/google.maps` (if using TypeScript)
- [ ] Install React Hook Form (optional): `npm install react-hook-form`
- [ ] Install icon library (optional): `npm install lucide-react` or `react-icons`

### Step 2.3: Configure Next.js
- [ ] Update `next.config.js` for API proxy (if needed)
- [ ] Configure environment variables (`.env.local`)
  - Add `NEXT_PUBLIC_API_URL=http://localhost:8000`
  - Add `NEXT_PUBLIC_GOOGLE_MAPS_API_KEY` (if using embedded maps)

### Step 2.4: Set Up TypeScript Types
- [ ] Create `frontend/types/index.ts`
- [ ] Define `SearchResult` interface
  - filename: string
  - score: number
  - lat: number
  - lon: number
  - heading: number
  - metadata: object
- [ ] Define `SearchResponse` interface
- [ ] Define `ImageSearchRequest` interface
- [ ] Define `TextSearchRequest` interface

---

## Phase 3: Build Core Components

### Step 3.1: Create API Client
- [ ] Create `frontend/lib/api.ts`
- [ ] Create function: `searchByImage(file: File)`
  - Create FormData
  - POST to `/api/search/image`
  - Return typed results
- [ ] Create function: `searchByText(query: string)`
  - POST to `/api/search/text`
  - Return typed results
- [ ] Add error handling
- [ ] Add request/response interceptors

### Step 3.2: Create Image Upload Component
- [ ] Create `frontend/components/ImageUpload.tsx`
- [ ] Add drag & drop area
- [ ] Add file input
- [ ] Add image preview
- [ ] Handle file validation (size, type)
- [ ] Show loading state
- [ ] Emit onUpload callback with File object
- [ ] Style with Tailwind CSS

### Step 3.3: Create Text Search Component
- [ ] Create `frontend/components/TextSearch.tsx`
- [ ] Add text input field
- [ ] Add search button
- [ ] Add example queries (optional)
- [ ] Handle form submission
- [ ] Show loading state
- [ ] Emit onSearch callback with query string
- [ ] Style with Tailwind CSS

### Step 3.4: Create Result Card Component
- [ ] Create `frontend/components/ResultCard.tsx`
- [ ] Display result data
  - Similarity score
  - Location coordinates
  - Heading
  - Filename
- [ ] Add "Open in Google Maps" button
- [ ] Add "Open Street View" button (optional)
- [ ] Show thumbnail if available
- [ ] Style with Tailwind CSS

### Step 3.5: Create Results List Component
- [ ] Create `frontend/components/ResultsList.tsx`
- [ ] Accept results array as prop
- [ ] Map over results
- [ ] Render ResultCard for each
- [ ] Show empty state if no results
- [ ] Add sorting/filtering options (optional)
- [ ] Style with Tailwind CSS

### Step 3.6: Create Map View Component
- [ ] Create `frontend/components/MapView.tsx`
- [ ] Option A: Embedded Google Maps
  - Use `@react-google-maps/api`
  - Display map with markers
  - Show info windows
- [ ] Option B: Direct Links (Simpler)
  - Generate Google Maps URLs
  - Display buttons for each result
- [ ] Show top result prominently
- [ ] Handle Google Maps API key
- [ ] Style with Tailwind CSS

### Step 3.7: Create Loading Spinner Component
- [ ] Create `frontend/components/LoadingSpinner.tsx`
- [ ] Create animated spinner
- [ ] Add loading text
- [ ] Make it reusable
- [ ] Style with Tailwind CSS

### Step 3.8: Create Utility Functions
- [ ] Create `frontend/utils/maps.ts`
- [ ] Create function: `generateGoogleMapsUrl(lat, lon)`
- [ ] Create function: `generateStreetViewUrl(lat, lon, heading)`
- [ ] Create function: `calculateDistance(lat1, lon1, lat2, lon2)`
- [ ] Add TypeScript types

---

## Phase 4: Build Main Page

### Step 4.1: Create Main Page Layout
- [ ] Edit `frontend/app/page.tsx`
- [ ] Set up state management
  - searchType: 'image' | 'text'
  - results: SearchResult[]
  - loading: boolean
  - error: string | null
- [ ] Create search handler functions
- [ ] Handle search type switching

### Step 4.2: Integrate Search Components
- [ ] Add ImageUpload component
- [ ] Add TextSearch component
- [ ] Add toggle/buttons to switch between modes
- [ ] Connect to search handlers
- [ ] Handle loading states

### Step 4.3: Integrate Results Display
- [ ] Add ResultsList component
- [ ] Add MapView component
- [ ] Conditionally render based on results
- [ ] Show loading spinner during search
- [ ] Display error messages

### Step 4.4: Add Page Styling
- [ ] Create responsive layout
- [ ] Add header/title
- [ ] Style search area
- [ ] Style results area
- [ ] Add spacing and padding
- [ ] Make it mobile-friendly

---

## Phase 5: Google Maps Integration

### Step 5.1: Set Up Google Maps API
- [ ] Get Google Maps API key
- [ ] Add to `.env.local`
- [ ] Configure API restrictions (if needed)
- [ ] Enable required APIs:
  - Maps JavaScript API
  - Geocoding API (optional)
  - Street View Static API (optional)

### Step 5.2: Implement Map Display
- [ ] Choose approach: Embedded map or direct links
- [ ] If embedded: Set up `@react-google-maps/api`
- [ ] Create map container
- [ ] Add markers for results
- [ ] Center map on top result
- [ ] Add info windows (optional)

### Step 5.3: Implement Street View Links
- [ ] Generate Street View URLs with coordinates and heading
- [ ] Test URL format
- [ ] Add "View Street View" buttons
- [ ] Open in new tab/window

### Step 5.4: Add Map Controls
- [ ] Add zoom controls
- [ ] Add pan controls
- [ ] Add marker click handlers
- [ ] Highlight selected result on map

---

## Phase 6: Polish & Enhancements

### Step 6.1: Error Handling
- [ ] Add error boundaries
- [ ] Handle API errors gracefully
- [ ] Show user-friendly error messages
- [ ] Add retry functionality
- [ ] Log errors for debugging

### Step 6.2: Loading States
- [ ] Add loading spinners
- [ ] Disable buttons during search
- [ ] Show progress indicators
- [ ] Optimistic UI updates (optional)

### Step 6.3: Responsive Design
- [ ] Test on mobile devices
- [ ] Adjust layout for small screens
- [ ] Make map responsive
- [ ] Optimize touch interactions
- [ ] Test on tablets

### Step 6.4: Performance Optimization
- [ ] Add image optimization
- [ ] Implement result pagination (if many results)
- [ ] Add debouncing for text search
- [ ] Optimize re-renders
- [ ] Add loading skeletons

### Step 6.5: Accessibility
- [ ] Add ARIA labels
- [ ] Ensure keyboard navigation
- [ ] Add focus indicators
- [ ] Test with screen readers
- [ ] Add alt text for images

### Step 6.6: Additional Features (Optional)
- [ ] Add result filtering by similarity score
- [ ] Add sorting options
- [ ] Show distance from query location
- [ ] Add favorites/bookmarks
- [ ] Add search history
- [ ] Add export results feature

---

## Phase 7: Testing

### Step 7.1: Backend Testing
- [ ] Test image upload endpoint
- [ ] Test text search endpoint
- [ ] Test error cases
- [ ] Test with various image formats
- [ ] Test with edge cases (empty queries, etc.)

### Step 7.2: Frontend Testing
- [ ] Test image upload flow
- [ ] Test text search flow
- [ ] Test results display
- [ ] Test map integration
- [ ] Test error states
- [ ] Test loading states

### Step 7.3: Integration Testing
- [ ] Test full flow: upload → search → display
- [ ] Test with real Pinecone data
- [ ] Verify Google Maps links work
- [ ] Test on different browsers
- [ ] Test on different devices

---

## Phase 8: Deployment

### Step 8.1: Prepare Backend for Deployment
- [ ] Update CORS settings for production domain
- [ ] Set up environment variables
- [ ] Configure production settings
- [ ] Add logging
- [ ] Set up health checks

### Step 8.2: Prepare Frontend for Deployment
- [ ] Update API URL for production
- [ ] Set up environment variables
- [ ] Optimize build
- [ ] Configure Next.js for production
- [ ] Add analytics (optional)

### Step 8.3: Deploy Backend
- [ ] Choose platform: Railway, Render, Heroku, AWS, etc.
- [ ] Set up deployment pipeline
- [ ] Configure environment variables
- [ ] Test deployed backend
- [ ] Set up monitoring

### Step 8.4: Deploy Frontend
- [ ] Choose platform: Vercel (recommended for Next.js), Netlify, etc.
- [ ] Connect to Git repository
- [ ] Configure build settings
- [ ] Set up environment variables
- [ ] Test deployed frontend
- [ ] Set up custom domain (optional)

---

## Environment Variables Needed

### Backend (.env)
```
COHERE_API_KEY=your_cohere_key
PINECONE_API_KEY=your_pinecone_key
```

### Frontend (.env.local)
```
NEXT_PUBLIC_API_URL=http://localhost:8000  # Development
NEXT_PUBLIC_API_URL=https://your-backend-url.com  # Production
NEXT_PUBLIC_GOOGLE_MAPS_API_KEY=your_google_maps_key  # If using embedded maps
```

---

## API Endpoints Specification

### POST /api/search/image
**Request:**
- Content-Type: `multipart/form-data`
- Body: `file` (image file)

**Response:**
```json
{
  "results": [
    {
      "filename": "40.661942_-73.981805_182.jpg",
      "score": 0.95,
      "lat": 40.661942,
      "lon": -73.981805,
      "heading": 182,
      "country": "USA",
      "metadata": {}
    }
  ],
  "query_type": "image"
}
```

### POST /api/search/text
**Request:**
```json
{
  "query": "urban street scene"
}
```

**Response:**
```json
{
  "results": [
    {
      "filename": "40.661942_-73.981805_182.jpg",
      "score": 0.87,
      "lat": 40.661942,
      "lon": -73.981805,
      "heading": 182,
      "country": "USA",
      "metadata": {}
    }
  ],
  "query_type": "text"
}
```

---

## Development Commands

### Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

### Frontend
```bash
cd frontend
npm install
npm run dev  # Runs on http://localhost:3000
```

---

## Key Considerations

1. **File Upload Handling**: Backend needs to handle multipart/form-data and process uploaded images
2. **CORS**: Backend must allow requests from frontend origin
3. **API Rate Limits**: Be aware of Cohere API rate limits
4. **Image Processing**: May need to resize/optimize uploaded images
5. **Error Handling**: Handle cases where Pinecone/Cohere APIs fail
6. **Security**: Validate file uploads, sanitize inputs
7. **Performance**: Consider caching, pagination for large result sets

---

## Next Steps After Completion

1. Add user authentication (if needed)
2. Add search history/persistence
3. Add advanced filtering options
4. Add result export functionality
5. Add analytics tracking
6. Add unit/integration tests
7. Add CI/CD pipeline
8. Add monitoring and logging

---

## Notes

- Start with MVP features, add enhancements later
- Test each phase before moving to the next
- Keep backend and frontend separate for easier deployment
- Use TypeScript for better type safety
- Follow Next.js best practices (App Router, Server Components where possible)
- Consider using Server Actions for API calls (Next.js 14 feature)

