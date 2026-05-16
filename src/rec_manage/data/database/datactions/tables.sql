PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS business (
    business_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    lat REAL NOT NULL,
    lng REAL NOT NULL
);

CREATE TABLE IF NOT EXISTS manager (
    manager_id INTEGER PRIMARY KEY AUTOINCREMENT,
    business_id INTEGER NOT NULL REFERENCES business(business_id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    password TEXT NOT NULL,
    role TEXT NOT NULL DEFAULT 'manager'
);

CREATE TABLE IF NOT EXISTS invite_code (
    code_id INTEGER PRIMARY KEY AUTOINCREMENT,
    business_id INTEGER NOT NULL REFERENCES business(business_id) ON DELETE CASCADE,
    code TEXT NOT NULL UNIQUE,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    expires_at TEXT,
    used INTEGER DEFAULT 0
);

CREATE TABLE IF NOT EXISTS zone (
    zone_id INTEGER PRIMARY KEY AUTOINCREMENT,
    business_id INTEGER NOT NULL REFERENCES business(business_id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    color TEXT NOT NULL DEFAULT '#38e441',
    coordinates TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS employee (
    employee_id INTEGER PRIMARY KEY AUTOINCREMENT,
    business_id INTEGER NOT NULL REFERENCES business(business_id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    password TEXT DEFAULT NULL,
    default_status TEXT NOT NULL DEFAULT 'active',
    profile_picture TEXT DEFAULT NULL
);

CREATE TABLE IF NOT EXISTS zone_assignment (
    assignment_id INTEGER PRIMARY KEY AUTOINCREMENT,
    zone_id INTEGER NOT NULL REFERENCES zone(zone_id) ON DELETE CASCADE,
    employee_id INTEGER NOT NULL REFERENCES employee(employee_id) ON DELETE CASCADE,
    UNIQUE(zone_id, employee_id)
);

CREATE TABLE IF NOT EXISTS time_slot (
    slot_id INTEGER PRIMARY KEY AUTOINCREMENT,
    business_id INTEGER NOT NULL REFERENCES business(business_id) ON DELETE CASCADE,
    shift_date TEXT NOT NULL,
    start_time TEXT NOT NULL,
    UNIQUE(business_id, shift_date, start_time)
);

CREATE TABLE IF NOT EXISTS slot_assignment (
    slot_assignment_id INTEGER PRIMARY KEY AUTOINCREMENT,
    slot_id INTEGER NOT NULL REFERENCES time_slot(slot_id) ON DELETE CASCADE,
    assignment_id INTEGER NOT NULL REFERENCES zone_assignment(assignment_id) ON DELETE CASCADE,
    status TEXT NOT NULL DEFAULT 'active',
    UNIQUE(slot_id, assignment_id)
);