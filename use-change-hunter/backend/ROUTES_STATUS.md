# Backend Routes Summary

## Routes Implementation

The backend routes are connected to the services layer:

- **search.py** - Main property search endpoint (uses planning_service + scoring_service)
- **property.py** - Get/create properties (will integrate with DB models) 
- **score.py** - Calculate scores (uses scoring_service)
- **scenario.py** - Financial scenarios (uses scenario_service)
- **export.py** - Export analysis (uses export_service)
- **health.py** - Health check

Each route uses dependency injection to access services that handle the business logic.

## Frontend State Management TODO

Next step: Create Zustand store and React Query integration for the frontend
