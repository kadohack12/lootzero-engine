create table if not exists public.deals (
    id uuid default gen_random_uuid() primary key,
    game_id text unique not null,
    title text not null,
    store text not null,
    original_price text,
    url text not null,
    expires_at timestamp with time zone,
    created_at timestamp with time zone default now()
);
