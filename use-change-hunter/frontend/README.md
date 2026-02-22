# Use-Change Hunter Frontend

Modern, responsive React/Next.js frontend for identifying planning-based property value-add opportunities.

## 🎯 Overview

Use-Change Hunter helps property developers and investors identify hidden opportunities through intelligent analysis of planning precedents. The frontend provides an intuitive interface for:

- **Property Search**: Find opportunities by postcode, address, or strategy
- **Opportunity Scoring**: Visualize properties with 0-100 scores based on local planning patterns
- **Planning Precedents**: View approved/refused applications nearby
- **Financial Modeling**: Build scenarios and calculate potential returns
- **Report Export**: Generate professional PDF/Excel reports

## 🏗️ Architecture

### Technology Stack

- **Framework**: Next.js 14 (React 18)
- **Language**: TypeScript (strict mode)
- **Styling**: Tailwind CSS 3.3 with custom color palette
- **Maps**: Leaflet + React-Leaflet
- **API Client**: Axios with typed methods
- **State**: Zustand (ready, not yet integrated)
- **Data Fetching**: React Query v5 (ready, not yet integrated)
- **Charts**: Recharts for financial visualizations
- **Icons**: Lucide React

### Directory Structure

```
frontend/src/
├── app/                           # Next.js app router
│   ├── layout.tsx                # Root layout with nav/footer
│   ├── page.tsx                  # Home/hero page
│   ├── search/
│   │   └── page.tsx              # Search results (grid/map view)
│   └── property/
│       └── [id]/
│           └── page.tsx          # Property detail with tabs
├── components/
│   ├── ui/                       # Reusable UI components
│   │   ├── Button.tsx            # Button with 4 variants
│   │   ├── Card.tsx              # Card container with sections
│   │   ├── Badge.tsx             # Badge + ScoreBadge
│   │   ├── Input.tsx             # Input, Select, TextArea
│   │   └── Tabs.tsx              # Tab navigation
│   ├── SearchBar.tsx             # Full search form
│   ├── ScoreCard.tsx             # Score visualization
│   ├── PrecedentsList.tsx        # Approved/refused precedents
│   ├── PropertyCard.tsx          # Property grid card
│   ├── ScenarioBuilder.tsx       # Financial modeling form
│   ├── ExportDialog.tsx          # PDF/Excel/JSON export
│   ├── Map.tsx                   # Leaflet map integration
│   └── index.ts                  # Barrel exports
├── lib/
│   └── api-client.ts             # Typed Axios client
├── types/
│   └── index.ts                  # TypeScript interfaces
├── globals.css                   # Tailwind + custom styles
└── [...other config files]
```

## 🎨 UI Components

### Base Components (Reusable)

- **Button**: Primary, secondary, outline, danger variants with sizes
- **Card**: Semantic CardHeader/CardBody/CardFooter structure
- **Badge**: Text badges + circular ScoreBadge for scores
- **Input**: Text input, Select dropdown, TextArea with labels
- **Tabs**: Tabbed content navigation

### Feature Components

- **SearchBar**: Postcode input + strategy select + radius slider
- **ScoreCard**: 3-column score display + breakdown table
- **PrecedentsList**: Approved/refused applications with distance/date
- **PropertyCard**: Property grid card with score and quick stats
- **PropertyGrid**: Responsive grid wrapper
- **ScenarioBuilder**: Financial modeling form with breakdown calculations
- **ExportDialog**: Format selection (PDF/Excel/JSON) + options
- **Map**: Leaflet map with property markers (SSR-safe)

## 🎯 Pages

### Home (`/`)

- Hero section with value proposition
- SearchBar for quick access
- Feature highlights
- How-it-works walkthrough
- Benefits section
- CTA section

### Search Results (`/search?postcode=XX&strategy=Y&radius=Z`)

- Dual view: Grid (left) + Details panel (right) OR Full map
- PropertyGrid showing 9 results
- Selected property details
- View full details / Export buttons
- Toggle between grid and map view

### Property Detail (`/property/[id]`)

- Full property address and metadata
- Tabs: Overview / Precedents / Scenarios / Analysis
- **Overview**: Score card + property details + opportunities
- **Precedents**: Approved/refused applications with statistics
- **Scenarios**: Pre-built scenarios + builder form
- **Analysis**: Strategic insights and recommendations
- Sidebar: Quick actions + key metrics
- Export dialog

## 🔌 API Integration

### Typed API Client (`lib/api-client.ts`)

```typescript
// Search properties
api.searchProperties({ postcode, strategy, radius });

// Get property details
api.getProperty(propertyId);

// Calculate scores
api.calculateScore(propertyId, strategy);

// Get precedents
api.getPrecedents(propertyId, radius);

// Financial modeling
api.getScenarios(propertyId);
api.createScenario(propertyId, data);

// Exports
api.exportPDF(propertyId, options);
api.exportExcel(propertyId, options);
api.exportJSON(propertyId, options);
```

### Backend Endpoints Supported

```
GET/POST /api/properties
GET      /api/properties/{id}
GET      /api/properties/{id}/score
GET      /api/properties/{id}/precedents
GET      /api/scenarios/{id}
POST     /api/scenarios
GET/POST /api/export/{format}
GET      /api/search
```

## 🚀 Getting Started

### Prerequisites

- Node.js 18+
- npm or yarn

### Installation

```bash
# Install dependencies
npm install

# Create environment file
cp .env.example .env.local

# Configure environment
# Edit .env.local with your backend URL and Mapbox token
```

### Development

```bash
# Start dev server (runs on http://localhost:3000)
npm run dev

# Type checking in another terminal
npm run type-check

# Build for production
npm build
npm start
```

## 🎨 Styling System

### Color Palette (Tailwind Config)

- **Primary**: `primary-50` to `primary-950` (blue-based)
- **Success**: `success-50` to `success-950` (green-based)
- **Warning**: `warning-50` to `warning-950` (amber-based)
- **Danger**: `danger-50` to `danger-950` (red-based)

### Responsive Breakpoints

- `sm`: 640px
- `md`: 768px
- `lg`: 1024px
- `xl`: 1280px

## 📊 Data Types

All TypeScript interfaces defined in `src/types/index.ts`:

```typescript
// Property with location and metadata
interface Property {
  id: string;
  postcode: string;
  address: string;
  latitude: number;
  longitude: number;
  area_sqm: number;
  historic_use: string;
  listed_status: string;
  opportunity_strategies: string[];
  distance_nearest_precedent: number;
}

// Opportunity score with breakdown
interface OpportunityScore {
  id: string;
  property_id: string;
  score_total: number; // 0-100
  score_risk: number; // 0-100
  score_confidence: number; // 0-100
  score_breakdown: ScoreBreakdown;
}

// Planning precedent
interface Precedent {
  reference: string; // "21/00456/FUL"
  proposal: string;
  decision: "approved" | "refused" | "withdrawn";
  date_decided: string;
  distance_m: number;
  lat: number;
  lng: number;
}

// Financial scenario
interface Scenario {
  id: string;
  property_id: string;
  name: string;
  strategy: string;
  development_cost: number;
  holding_period_months: number;
  finance_type: string;
  finance_rate: number;
  assumptions: string;
}
```

## 🔄 State Management (Ready to Integrate)

### Zustand Store Pattern

```typescript
// Already set up in dependencies, ready to use:
import create from "zustand";

const useSearchStore = create((set) => ({
  query: "",
  strategy: "extension",
  radius: 1000,
  results: [],
  setQuery: (q) => set({ query: q }),
  // ...
}));
```

### React Query Integration

```typescript
// Hooks ready for integration:
const { data: results, isLoading } = useQuery({
  queryKey: ["properties", postcode, strategy],
  queryFn: () => api.searchProperties({ postcode, strategy, radius }),
});
```

## 🗺️ Map Integration

Leaflet map with:

- OpenStreetMap tiles
- Circle markers for properties (color-coded by score)
- Popups showing property details
- Click handlers for property selection
- SSR-safe dynamic import

## 📱 Responsive Design

- **Mobile**: Single column, stack all content
- **Tablet**: 2-column layouts with sidebars
- **Desktop**: Full 3-column layouts with sticky sidebars

## 🔒 Security Notes

- API client includes CSRF token support
- Environment variables for sensitive data
- Leaflet tokens handled via Next.js config
- No sensitive data logged

## 📚 Component Usage Examples

### SearchBar

```tsx
<SearchBar onSubmit={(data) => handleSearch(data)} isLoading={isSearching} />
```

### PropertyGrid

```tsx
<PropertyGrid
  properties={properties}
  scores={scores}
  isLoading={isLoading}
  onViewProperty={(id) => navigate(`/property/${id}`)}
  onExportProperty={(id) => handleExport(id)}
/>
```

### ScenarioBuilder

```tsx
<ScenarioBuilder
  initialScenario={existingScenario}
  onSave={(data) => api.createScenario(propertyId, data)}
  isLoading={isSaving}
/>
```

### ExportDialog

```tsx
<ExportDialog
  propertyAddress={property.address}
  onExport={(format, options) => api.export(propertyId, format, options)}
/>
```

## 🐛 Development Tips

1. **Type Safety**: TypeScript strict mode catches errors early
2. **Component Testing**: All components accept test IDs
3. **API Mocking**: SearchPage has built-in mock data for development
4. **Responsive Testing**: Use Chrome DevTools device emulation
5. **Performance**: Next.js automatic code splitting + image optimization

## 📦 Building for Production

```bash
# Build optimized bundle
npm run build

# Run production server
npm start

# Analyze bundle size
npm install -D @next/bundle-analyzer
# Then configure in next.config.js
```

## 🤝 Integration Checklist

- [ ] Connect SearchBar to real API
- [ ] Wire up React Query for data fetching
- [ ] Implement Zustand store for search state
- [ ] Connect PropertyCard to property detail navigation
- [ ] Implement map marker clustering
- [ ] Add authentication/login flow
- [ ] Connect export functionality to backend
- [ ] Add error boundary and error pages
- [ ] Implement analytics tracking
- [ ] Add loading skeletons to all pages

## 📖 Next Steps

1. **Backend Connection**: Point API client to backend server
2. **State Management**: Integrate Zustand store and React Query
3. **Error Handling**: Add error boundaries and retry logic
4. **Analytics**: Add Google Analytics / Mixpanel tracking
5. **Authentication**: Implement sign-up/sign-in flow
6. **Refinements**: Polish animations, add dark mode, etc.

## 📞 Support

For issues or questions about the frontend:

1. Check `types/index.ts` for API contract
2. Review `lib/api-client.ts` for endpoint configuration
3. Inspect component prop interfaces for usage patterns
4. Check Tailwind config for available colors/utilities
