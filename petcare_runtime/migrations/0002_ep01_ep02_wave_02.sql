CREATE TABLE vaccination_record (
  vaccination_record_id TEXT PRIMARY KEY,
  pet_id TEXT NOT NULL,
  vaccine_name TEXT NOT NULL,
  administered_at TEXT NOT NULL,
  next_due_at_nullable TEXT,
  provider_name_nullable TEXT,
  batch_number_nullable TEXT,
  status TEXT NOT NULL,
  recorded_at TEXT NOT NULL,
  updated_at TEXT NOT NULL,
  version_no INTEGER NOT NULL
);

CREATE TABLE lab_result (
  lab_result_id TEXT PRIMARY KEY,
  pet_id TEXT NOT NULL,
  lab_name TEXT NOT NULL,
  test_name TEXT NOT NULL,
  result_value_nullable TEXT,
  result_unit_nullable TEXT,
  result_flag_nullable TEXT,
  collected_at_nullable TEXT,
  reported_at_nullable TEXT,
  attachment_document_id_nullable TEXT,
  recorded_at TEXT NOT NULL,
  updated_at TEXT NOT NULL,
  version_no INTEGER NOT NULL
);

CREATE TABLE clinical_note (
  clinical_note_id TEXT PRIMARY KEY,
  pet_id TEXT NOT NULL,
  consultation_id_nullable TEXT,
  note_type TEXT NOT NULL,
  content_structured_or_text TEXT NOT NULL,
  author_actor_id TEXT NOT NULL,
  signed_by_actor_id_nullable TEXT,
  signed_at_nullable TEXT,
  status TEXT NOT NULL,
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL,
  version_no INTEGER NOT NULL
);

CREATE TABLE uphr_document (
  uphr_document_id TEXT PRIMARY KEY,
  pet_id TEXT NOT NULL,
  document_type TEXT NOT NULL,
  object_storage_key TEXT NOT NULL,
  mime_type TEXT NOT NULL,
  size_bytes INTEGER NOT NULL,
  uploaded_by_actor_id TEXT NOT NULL,
  visibility_scope TEXT NOT NULL,
  checksum_sha256 TEXT NOT NULL,
  created_at TEXT NOT NULL
);
