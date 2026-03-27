-- Jalankan perintah SQL ini di SQL Editor Supabase Anda untuk memperbaiki error insert.

-- Perbaikan untuk tabel 'users'
ALTER TABLE users ALTER COLUMN id SET DEFAULT gen_random_uuid();
ALTER TABLE users ALTER COLUMN created_at SET DEFAULT now();

-- Perbaikan untuk tabel 'scores'
ALTER TABLE scores ALTER COLUMN id SET DEFAULT gen_random_uuid();
ALTER TABLE scores ALTER COLUMN created_at SET DEFAULT now();
