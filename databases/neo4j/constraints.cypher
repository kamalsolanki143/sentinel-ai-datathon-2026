-- Sentinel AI Neo4j Database Constraints and Indexes
-- Run these statements in the Cypher Shell to initialize the graph schema

-- 1. Uniqueness Constraints

CREATE CONSTRAINT criminal_id_uniq IF NOT EXISTS FOR (c:Criminal) REQUIRE c.id IS UNIQUE;

CREATE CONSTRAINT fir_id_uniq IF NOT EXISTS FOR (f:FIR) REQUIRE f.id IS UNIQUE;
CREATE CONSTRAINT fir_number_uniq IF NOT EXISTS FOR (f:FIR) REQUIRE f.fir_number IS UNIQUE;

CREATE CONSTRAINT vehicle_id_uniq IF NOT EXISTS FOR (v:Vehicle) REQUIRE v.id IS UNIQUE;
CREATE CONSTRAINT vehicle_reg_uniq IF NOT EXISTS FOR (v:Vehicle) REQUIRE v.registration_number IS UNIQUE;

CREATE CONSTRAINT phone_id_uniq IF NOT EXISTS FOR (p:PhoneNumber) REQUIRE p.id IS UNIQUE;
CREATE CONSTRAINT phone_num_uniq IF NOT EXISTS FOR (p:PhoneNumber) REQUIRE p.number IS UNIQUE;

CREATE CONSTRAINT location_id_uniq IF NOT EXISTS FOR (l:Location) REQUIRE l.id IS UNIQUE;

-- 2. Performance Search Indexes

CREATE INDEX criminal_name_idx IF NOT EXISTS FOR (c:Criminal) ON (c.name);
CREATE INDEX fir_crime_type_idx IF NOT EXISTS FOR (f:FIR) ON (f.crime_type);
CREATE INDEX location_name_idx IF NOT EXISTS FOR (l:Location) ON (l.name);
