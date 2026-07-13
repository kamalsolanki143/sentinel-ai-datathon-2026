-- Sentinel AI PostgreSQL Database Schema
-- Designed for Law Enforcement Intelligence Operations

-- 1. Create Enums safely using PL/pgSQL
DO $$ 
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'officer_role_enum') THEN
        CREATE TYPE officer_role_enum AS ENUM ('admin', 'officer', 'analyst');
    END IF;

    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'criminal_status_enum') THEN
        CREATE TYPE criminal_status_enum AS ENUM ('active', 'arrested', 'deceased', 'absconding');
    END IF;

    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'crime_type_enum') THEN
        CREATE TYPE crime_type_enum AS ENUM ('theft', 'cybercrime', 'murder', 'assault', 'fraud', 'kidnapping', 'drug_trafficking', 'vehicle_theft', 'robbery', 'other');
    END IF;

    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'fir_status_enum') THEN
        CREATE TYPE fir_status_enum AS ENUM ('open', 'under_investigation', 'closed', 'chargesheet_filed');
    END IF;

    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'chat_role_enum') THEN
        CREATE TYPE chat_role_enum AS ENUM ('user', 'assistant');
    END IF;
END $$;

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- 2. Create Tables

CREATE TABLE IF NOT EXISTS officers (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    badge_number VARCHAR(50) UNIQUE NOT NULL,
    rank VARCHAR(100),
    department VARCHAR(100),
    hashed_password VARCHAR(255) NOT NULL,
    role officer_role_enum NOT NULL DEFAULT 'officer',
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS criminals (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    aliases VARCHAR(255)[] NOT NULL DEFAULT '{}',
    dob DATE,
    gender VARCHAR(20),
    nationality VARCHAR(100) NOT NULL DEFAULT 'Indian',
    address TEXT,
    photo_url VARCHAR(500),
    risk_score DOUBLE PRECISION NOT NULL DEFAULT 0.0,
    status criminal_status_enum NOT NULL DEFAULT 'active',
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS firs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    fir_number VARCHAR(100) UNIQUE NOT NULL,
    date_filed TIMESTAMP NOT NULL,
    crime_type crime_type_enum NOT NULL,
    description TEXT,
    location_lat DOUBLE PRECISION,
    location_lng DOUBLE PRECISION,
    location_name VARCHAR(255),
    district VARCHAR(100),
    state VARCHAR(100),
    status fir_status_enum NOT NULL DEFAULT 'open',
    officer_id UUID NOT NULL REFERENCES officers(id),
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS criminal_firs (
    criminal_id UUID NOT NULL REFERENCES criminals(id) ON DELETE CASCADE,
    fir_id UUID NOT NULL REFERENCES firs(id) ON DELETE CASCADE,
    role_in_crime VARCHAR(100) NOT NULL DEFAULT 'suspect',
    PRIMARY KEY (criminal_id, fir_id)
);

CREATE TABLE IF NOT EXISTS vehicles (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    registration_number VARCHAR(50) UNIQUE NOT NULL,
    make VARCHAR(100),
    model VARCHAR(100),
    color VARCHAR(50),
    owner_criminal_id UUID REFERENCES criminals(id) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS phone_numbers (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    number VARCHAR(20) NOT NULL,
    criminal_id UUID NOT NULL REFERENCES criminals(id) ON DELETE CASCADE,
    is_active BOOLEAN NOT NULL DEFAULT TRUE
);

CREATE TABLE IF NOT EXISTS known_locations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    criminal_id UUID NOT NULL REFERENCES criminals(id) ON DELETE CASCADE,
    location_name VARCHAR(255) NOT NULL,
    lat DOUBLE PRECISION NOT NULL,
    lng DOUBLE PRECISION NOT NULL,
    frequency_score INTEGER NOT NULL DEFAULT 1
);

CREATE TABLE IF NOT EXISTS crime_hotspots (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    district VARCHAR(100) NOT NULL,
    lat DOUBLE PRECISION NOT NULL,
    lng DOUBLE PRECISION NOT NULL,
    risk_score DOUBLE PRECISION NOT NULL,
    crime_type VARCHAR(100) NOT NULL,
    prediction_date TIMESTAMP NOT NULL,
    model_version VARCHAR(50) NOT NULL DEFAULT 'v1.0'
);

CREATE TABLE IF NOT EXISTS chat_sessions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    officer_id UUID NOT NULL REFERENCES officers(id),
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS chat_messages (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    session_id UUID NOT NULL REFERENCES chat_sessions(id) ON DELETE CASCADE,
    role chat_role_enum NOT NULL,
    content TEXT NOT NULL,
    timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- 3. Create Performance Indexes

CREATE INDEX IF NOT EXISTS idx_criminals_name ON criminals (name);
CREATE INDEX IF NOT EXISTS idx_firs_crime_type ON firs (crime_type);
CREATE INDEX IF NOT EXISTS idx_firs_district ON firs (district);
CREATE INDEX IF NOT EXISTS idx_firs_date_filed ON firs (date_filed);
CREATE INDEX IF NOT EXISTS idx_crime_hotspots_district ON crime_hotspots (district);
