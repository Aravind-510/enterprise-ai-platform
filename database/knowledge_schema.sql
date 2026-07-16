-- =====================================================
-- Enterprise AI Platform
-- Sprint 2
-- Knowledge Base Database Schema
-- PostgreSQL
-- =====================================================

-- Drop tables (for development only)

DROP TABLE IF EXISTS document_permissions CASCADE;
DROP TABLE IF EXISTS document_versions CASCADE;
DROP TABLE IF EXISTS document_chunks CASCADE;
DROP TABLE IF EXISTS documents CASCADE;

---------------------------------------------------------
-- Documents
---------------------------------------------------------

CREATE TABLE documents (

    id SERIAL PRIMARY KEY,

    title VARCHAR(255) NOT NULL,

    file_name VARCHAR(255) NOT NULL UNIQUE,

    document_type VARCHAR(50) NOT NULL,

    department VARCHAR(100) NOT NULL,

    owner VARCHAR(150) NOT NULL,

    version INTEGER NOT NULL DEFAULT 1,

    status VARCHAR(30) NOT NULL DEFAULT 'Pending',

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP

);

---------------------------------------------------------
-- Document Chunks
---------------------------------------------------------

CREATE TABLE document_chunks (

    id SERIAL PRIMARY KEY,

    document_id INTEGER NOT NULL,

    chunk_number INTEGER NOT NULL,

    chunk_text TEXT NOT NULL,

    embedding_id VARCHAR(255),

    page_number INTEGER DEFAULT 1,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_document_chunks_document
        FOREIGN KEY(document_id)
        REFERENCES documents(id)
        ON DELETE CASCADE

);

---------------------------------------------------------
-- Document Versions
---------------------------------------------------------

CREATE TABLE document_versions (

    id SERIAL PRIMARY KEY,

    document_id INTEGER NOT NULL,

    version INTEGER NOT NULL,

    uploaded_by VARCHAR(150) NOT NULL,

    approved_by VARCHAR(150),

    approval_date TIMESTAMP,

    remarks TEXT,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_document_versions_document
        FOREIGN KEY(document_id)
        REFERENCES documents(id)
        ON DELETE CASCADE

);

---------------------------------------------------------
-- Document Permissions
---------------------------------------------------------

CREATE TABLE document_permissions (

    id SERIAL PRIMARY KEY,

    role VARCHAR(100) NOT NULL,

    department VARCHAR(100) NOT NULL,

    access_level VARCHAR(50) NOT NULL,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP

);

---------------------------------------------------------
-- Constraints
---------------------------------------------------------

ALTER TABLE documents
ADD CONSTRAINT chk_document_status
CHECK (
    status IN (
        'Pending',
        'Approved',
        'Rejected',
        'Archived'
    )
);

ALTER TABLE document_permissions
ADD CONSTRAINT chk_access_level
CHECK (
    access_level IN (
        'Read',
        'Write',
        'Admin'
    )
);

---------------------------------------------------------
-- Indexes
---------------------------------------------------------

CREATE INDEX idx_documents_department
ON documents(department);

CREATE INDEX idx_documents_owner
ON documents(owner);

CREATE INDEX idx_documents_status
ON documents(status);

CREATE INDEX idx_documents_type
ON documents(document_type);

CREATE INDEX idx_document_chunks_document
ON document_chunks(document_id);

CREATE INDEX idx_document_chunks_embedding
ON document_chunks(embedding_id);

CREATE INDEX idx_document_versions_document
ON document_versions(document_id);

CREATE INDEX idx_document_permissions_role
ON document_permissions(role);

CREATE INDEX idx_document_permissions_department
ON document_permissions(department);

---------------------------------------------------------
-- Sample Permissions
---------------------------------------------------------

INSERT INTO document_permissions
(role, department, access_level)
VALUES
('Admin','HR','Admin'),
('HR Manager','HR','Write'),
('HR Employee','HR','Read'),

('Finance Manager','Payroll','Write'),
('Finance Employee','Payroll','Read'),

('Project Manager','Projects','Write'),
('Project Member','Projects','Read'),

('Engineering Manager','Engineering','Write'),
('Engineer','Engineering','Read'),

('Support Manager','Support','Write'),
('Support Engineer','Support','Read');

---------------------------------------------------------
-- Sample Documents
---------------------------------------------------------

INSERT INTO documents
(
title,
file_name,
document_type,
department,
owner,
version,
status
)
VALUES
(
'Employee Handbook',
'employee_handbook.pdf',
'PDF',
'HR',
'Admin',
1,
'Approved'
),
(
'Payroll Policy',
'payroll_policy.docx',
'DOCX',
'Payroll',
'Finance Team',
1,
'Approved'
);

---------------------------------------------------------
-- Sample Versions
---------------------------------------------------------

INSERT INTO document_versions
(
document_id,
version,
uploaded_by,
approved_by,
approval_date,
remarks
)
VALUES
(
1,
1,
'Admin',
'HR Manager',
CURRENT_TIMESTAMP,
'Initial Release'
),
(
2,
1,
'Finance Team',
'Finance Manager',
CURRENT_TIMESTAMP,
'Approved'
);

---------------------------------------------------------
-- Sample Chunks
---------------------------------------------------------

INSERT INTO document_chunks
(
document_id,
chunk_number,
chunk_text,
embedding_id,
page_number
)
VALUES
(
1,
1,
'Employees are entitled to annual leave according to company policy.',
'embed_001',
1
),
(
1,
2,
'Remote work policy requires manager approval.',
'embed_002',
2
);

---------------------------------------------------------
-- Verify
---------------------------------------------------------

SELECT * FROM documents;

SELECT * FROM document_chunks;

SELECT * FROM document_versions;

SELECT * FROM document_permissions;