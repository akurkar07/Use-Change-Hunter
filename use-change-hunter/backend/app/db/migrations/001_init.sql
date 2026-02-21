-- Initial database schema
CREATE EXTENSION IF NOT EXISTS postgis;

-- Strategy type enum for type safety
CREATE TYPE strategy_type AS ENUM ('opportunity', 'risk', 'development', 'sustainability');

-- cached Ibex calls (protects credits)
CREATE TABLE ibex_cache (
  cache_key TEXT PRIMARY KEY,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  expires_at TIMESTAMPTZ,
  payload_json JSONB NOT NULL,
  response_json JSONB NOT NULL
);

CREATE INDEX ibex_cache_expires_at_idx ON ibex_cache(expires_at);
CREATE INDEX ibex_cache_created_at_idx ON ibex_cache(created_at);

-- "properties" in MVP can just be points user clicks or inferred from planning site addresses
CREATE TABLE properties (
  id UUID PRIMARY KEY,
  address TEXT,
  postcode TEXT,
  property_type TEXT,
  geom GEOGRAPHY(POINT, 4326),
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX properties_geom_idx ON properties USING GIST (geom);
CREATE INDEX properties_postcode_idx ON properties(postcode);

-- scoring results (per strategy)
CREATE TABLE opportunity_scores (
  id UUID PRIMARY KEY,
  property_id UUID NOT NULL REFERENCES properties(id) ON DELETE CASCADE,
  strategy_type strategy_type NOT NULL,
  score_total INT NOT NULL CHECK (score_total >= 0 AND score_total <= 100),
  score_risk INT NOT NULL CHECK (score_risk >= 0 AND score_risk <= 100),
  score_confidence INT NOT NULL CHECK (score_confidence >= 0 AND score_confidence <= 100),
  breakdown JSONB NOT NULL,
  scenario JSONB,
  generated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX opportunity_scores_property_strategy_idx ON opportunity_scores(property_id, strategy_type);
CREATE INDEX opportunity_scores_generated_at_idx ON opportunity_scores(generated_at);

-- planning scenarios for what-if analysis
CREATE TABLE scenarios (
  id UUID PRIMARY KEY,
  property_id UUID NOT NULL REFERENCES properties(id) ON DELETE CASCADE,
  name TEXT,
  description TEXT,
  scenario_type TEXT NOT NULL,
  parameters JSONB NOT NULL,
  results JSONB,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX scenarios_property_idx ON scenarios(property_id);
CREATE INDEX scenarios_scenario_type_idx ON scenarios(scenario_type);
