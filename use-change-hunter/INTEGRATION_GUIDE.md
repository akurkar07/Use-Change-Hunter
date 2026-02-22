# Full-Stack Integration Guide

This document describes the complete integration between the backend FastAPI services and the frontend React application with state management.

## Architecture Overview

### Backend Stack
- **Framework**: FastAPI (async/await)
- **Database**: PostgreSQL with async SQLAlchemy 2.0
- **Caching**: Redis (with database fallback)
- **API Client**: Aiohttp for external Ibex API calls
- **Export**: Weasyprint (PDF), Openpyxl (Excel), JSON

### Frontend Stack
- **Framework**: Next.js 14 with TypeScript
- **State Management**: Zustand + React Query
- **HTTP Client**: Axios
- **Styling**: Tailwind CSS

## Data Flow

### 1. Search Flow

```
User Input (SearchBar)
    ↓
SearchStore.setQuery()
    ↓
useSearchProperties() hook (React Query)
    ↓
api.searchProperties() (Axios)
    ↓
POST /api/search/ (Backend)
    ↓
PlanningService.search_nearby_precedents() (with caching)
    ↓
ScoringService.calculate_score()
    ↓
Response with properties[] + scores[]
    ↓
SearchStore.setResults()
    ↓
PropertyGrid Component (re-renders with new data)
```

### 2. Property Details Flow

```
User clicks PropertyCard
    ↓
SearchStore.setSelectedProperty()
    ↓
useProperty() + usePropertyScore() + usePrecedents() hooks
    ↓
Parallel API calls:
    - GET /api/properties/{id}
    - POST /api/scores/calculate
    - GET /api/properties/{id}/precedents
    ↓
UI displays in SidePanel + DetailPage
```

### 3. Scenario Calculation Flow

```
User creates Scenario
    ↓
useCreateScenario() mutation
    ↓
POST /api/scenarios/
    ↓
ScenarioService.calculate_scenario_breakdown()
    ↓
Returns: ARV, profit, ROI, financing costs
    ↓
React Query invalidates scenarios query
    ↓
useScenarios() refetches data
    ↓
ScenarioBuilder component updates
```

## Component Integration

### SearchBar Component
**File**: `frontend/src/components/SearchBar.tsx`

```typescript
import { useSearchStore } from '@/lib/stores/searchStore';
import { useSearchProperties } from '@/lib/hooks';

const SearchBar: React.FC = () => {
  const store = useSearchStore();
  const { isLoading, error } = useSearchProperties(
    query.postcode,
    query.strategy,
    query.radius
  );

  const handleSubmit = (e) => {
    store.setQuery({ postcode, strategy, radius });
    // React Query will fetch automatically because of enabled condition
  };
};
```

**State Management**:
- Local state: form inputs (postcode, strategy, radius)
- Zustand store: persisted search query
- React Query: server state (API response)

### Search Results Page
**File**: `frontend/src/app/search/page.tsx`

```typescript
const SearchPage = () => {
  // Get persisted state from store
  const { query, properties, scores, selectedPropertyId } = useSearchStore();
  
  // Fetch fresh data with React Query
  const { properties: fetchedProperties, scores: fetchedScores, isLoading } =
    usePropertySearch(query.postcode, query.strategy, query.radius);

  // Display data (freshly fetched + persisted fallback)
  return (
    <PropertyGrid properties={fetchedProperties || properties} />
  );
};
```

**State Management**:
- Zustand: query, selected property, view mode
- React Query: fresh search results cached for 5 minutes
- Local component state: view mode toggle

### Property Detail Page
**File**: `frontend/src/app/property/[id]/page.tsx` (to be created)

Expected hooks:
```typescript
const DetailPage = ({ propertyId }: { propertyId: string }) => {
  const { data: property } = useProperty(propertyId);
  const { data: score } = usePropertyScore(propertyId);
  const { data: precedents } = usePrecedents(propertyId);
  const { data: scenarios } = useScenarios(propertyId);
  const createScenarioMutation = useCreateScenario();

  return (
    <PropertyDetailView
      property={property}
      score={score}
      precedents={precedents}
      scenarios={scenarios}
      onCreateScenario={createScenarioMutation.mutate}
    />
  );
};
```

## State Management Strategy

### Zustand Store (searchStore)

**Persistent State** (stored in localStorage):
- `query`: Current search parameters
- `viewMode`: Grid or map view preference

**Ephemeral State** (cleared on page nav):
- `properties`, `scores`, `precedents`: Search results
- `selectedPropertyId`: Currently selected property
- `isLoading`, `error`: UI state

**Actions**:
```typescript
// Dispatch new search
store.setQuery({ postcode: 'SW1A1AA', strategy: 'extension', radius: 1000 });

// Update results (called after API response)
store.setResults(properties, scores);

// Select property
store.setSelectedProperty(propertyId);

// View mode toggle
store.setViewMode('map');
```

### React Query Hooks

**Query Caching Strategy**:
| Hook | Stale Time | Cache Time | Data |
|------|-----------|-----------|------|
| `useSearchProperties` | 5 min | 10 min | 50-100 properties + scores |
| `useProperty` | 10 min | 30 min | Single property details |
| `usePropertyScore` | 5 min | 10 min | Opportunity score |
| `usePrecedents` | 10 min | 30 min | Planning precedents array |
| `useScenarios` | 10 min | 30 min | Financial scenarios |

**Mutation Invalidation**:
```typescript
// After creating scenario, refresh scenarios list
queryClient.invalidateQueries({
  queryKey: searchKeys.scenarios(propertyId)
});
```

## API Client Configuration

### Base URL
```typescript
// .env.local
NEXT_PUBLIC_API_BASE=http://localhost:8000
```

### Endpoints Mapping

| Function | Method | Endpoint | Response |
|----------|--------|----------|----------|
| `searchProperties` | POST | `/api/search/` | `SearchResponse` |
| `getProperty` | GET | `/api/properties/{id}` | `PropertyResponse` |
| `calculateScore` | POST | `/api/scores/calculate` | `OpportunityScore` |
| `getPrecedents` | GET | `/api/properties/{id}/precedents` | `Precedent[]` |
| `getScenarios` | GET | `/api/scenarios/?property_id=...` | `Scenario[]` |
| `createScenario` | POST | `/api/scenarios/` | `Scenario` |
| `updateScenario` | PUT | `/api/scenarios/{id}` | `Scenario` |
| `exportProperty` | POST | `/api/export/` | `Blob` \| `{ url }` |

## Backend Services

### 1. Planning Service
- **Purpose**: Extract planning precedents from Ibex API
- **Caching**: 2-hour TTL with deterministic cache keys
- **Key Methods**:
  - `search_nearby_precedents(postcode, strategy, radius)` → `Precedent[]`
  - `analyze_precedents(precedents)` → `ScoreBreakdown`

### 2. Scoring Service
- **Algorithm**: 
  - 40% precedent score (based on count + recency)
  - 35% approval score (from approval rate)
  - 25% risk score inverse (from refusal rate)
- **Returns**: `OpportunityScore` with breakdown

### 3. Scenario Service
- **Calculates**: ARV, financing costs, profit/ROI
- **Finance Types**: Cash, BTL mortgage, development loan
- **Assumptions**: 30% uplift, 70% LTV, 15% soft costs
- **Methods**:
  - `calculate_scenario_breakdown(property, parameters)`
  - `rank_scenarios(scenarios)`
  - `compare_scenarios(scenario1, scenario2)`

### 4. Cache Service
- **Dual-layer**: Redis (fast) + Database (persistent)
- **Purpose**: Protect expensive Ibex API credits
- **TTL Configuration**: 2 hours for planning data
- **Fallback**: Uses DB if Redis unavailable

### 5. Export Service
- **Formats**: JSON, Excel (styled), PDF (HTML-based)
- **Content**: Property details + scores + precedents + scenarios
- **Performance**: Async generation, blob return

## Type System

### TypeScript Interfaces

**Search Query**:
```typescript
interface SearchQuery {
  postcode: string;
  strategy: 'extension' | 'hmo' | 'office_to_resi' | 'retail_to_mixed' | 'flats';
  radius: number; // meters
}
```

**Property**:
```typescript
interface Property {
  id: string;
  address?: string;
  postcode?: string;
  property_type?: string;
  created_at: string;
}
```

**OpportunityScore**:
```typescript
interface OpportunityScore {
  id: string;
  property_id: string;
  score_total: number; // 0-100
  score_risk: number; // 0-100, higher = more risk
  score_confidence: number; // 0-100, based on data quality
  breakdown: {
    precedents_found: number;
    approved: number;
    refused: number;
    approval_rate: number; // 0-1
    nearby_schemes: number;
  };
}
```

**Scenario**:
```typescript
interface Scenario {
  id: string;
  property_id: string;
  name?: string;
  scenario_type: string;
  parameters: {
    buy_price?: number;
    build_cost?: number;
    finance_type?: 'cash' | 'btl_mortgage' | 'development_loan';
    hold_years?: number;
  };
  results?: {
    total_cost: number;
    gross_profit: number;
    roi_pct: number;
  };
}
```

## Error Handling

### Frontend Error Flow
```typescript
// In hooks
const { error } = useSearchProperties(postcode, strategy, radius);

// Error types from API
- 400: Validation error (invalid postcode, radius)
- 401: Unauthorized (missing API key)
- 429: Rate limited (too many Ibex API calls)
- 500: Server error

// Display to user
{error && (
  <Alert variant="destructive">
    Error: {error.message}
    <Button onClick={() => retry()}>Retry</Button>
  </Alert>
)}
```

### Caching Fallback
```
1. Try Redis cache
2. If miss, query backend + Ibex API
3. If Ibex API fails, try database cache
4. If database empty, return empty results with warning
```

## Performance Optimization

### Query Deduplication
React Query automatically deduplicates requests:
```typescript
// Only one request sent to backend even though component renders twice
<Property id="123" />
<Property id="123" />
```

### Stale-While-Revalidate
```typescript
// Serve stale data immediately, fetch fresh in background
const { data } = useSearchProperties(postcode, strategy, radius);
// Stale time: 5 min
// GC time: 10 min
```

### Pagination
```typescript
// Store maintains pagination state
store.pagination = { total: 250, offset: 0, limit: 20 };
// Load next page in PropertyGrid
```

## Development Setup

### Environment Variables
```bash
# .env.local
NEXT_PUBLIC_API_BASE=http://localhost:8000
NEXT_PUBLIC_IBEX_API_KEY=your_key_here
```

### Backend Setup
```bash
cd use-change-hunter/backend
python -m pip install -r pyproject.toml
export DATABASE_URL=postgresql+asyncpg://user:pass@localhost/usechange
export REDIS_URL=redis://localhost:6379
python -m uvicorn app.main:app --reload
```

### Frontend Setup
```bash
cd use-change-hunter/frontend
npm install
npm run dev
```

## Testing

### Component Testing Pattern
```typescript
import { render, screen, waitFor } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';

const queryClient = new QueryClient();

test('search returns properties', async () => {
  render(
    <QueryClientProvider client={queryClient}>
      <SearchBar />
    </QueryClientProvider>
  );

  // Type and submit search
  // Wait for API call
  await waitFor(() => {
    expect(screen.getByText(/properties found/)).toBeInTheDocument();
  });
});
```

### E2E Testing Flow
1. User enters postcode "SW1A1AA"
2. Clicks "Search" button
3. Waits for PropertyGrid to populate with results
4. Clicks on property card
5. Verifies ScoreCard and precedents display
6. Verifies URL changes to /property/{id}
7. Creates new scenario
8. Verifies results calculate correctly

## Deployment Checklist

- [ ] Backend: Set production DATABASE_URL (managed PostgreSQL)
- [ ] Backend: Set production REDIS_URL (managed Redis)
- [ ] Backend: Set production IBEX_JWT (API credentials)
- [ ] Frontend: Set NEXT_PUBLIC_API_BASE (production domain)
- [ ] Frontend: Build and test: `npm run build && npm run start`
- [ ] Backend: Run migrations: `alembic upgrade head`
- [ ] Backend: Start with proper CORS headers
- [ ] Frontend: Set up CDN for static assets
- [ ] Monitor: Set up error logging (Sentry)
- [ ] Monitor: Set up performance monitoring (Vercel Analytics)

## Troubleshooting

### Q: Search returns empty results
**A**: Check if Ibex API is accessible. Verify:
1. `IBEX_JWT` is correct
2. `REDIS_URL` is accessible
3. Database fallback cache is populated

### Q: Components not updating after mutation
**A**: Ensure mutation.onSuccess() calls `queryClient.invalidateQueries()`:
```typescript
const createScenarioMutation = useCreateScenario();
// This automatically invalidates and refetches
```

### Q: React Query showing stale data
**A**: Lower stale time or force refetch:
```typescript
const { refetch } = useSearchProperties(postcode, strategy, radius);
<button onClick={() => refetch()}>Refresh</button>
```

### Q: CORS errors in browser
**A**: Backend main.py includes CORS middleware. Verify:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```
