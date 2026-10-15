# LootZero Engine

Collecte les offres de jeux gratuits depuis GamerPower et les insère dans Supabase avec une déduplication sur `game_id`.

## Configuration

Le workflow GitHub Actions utilise deux secrets du dépôt :

- `SUPABASE_URL`
- `SUPABASE_KEY`

Le endpoint source est configurable avec `DEALS_SOURCE_URL` (par défaut : `https://www.gamerpower.com/api/giveaways`).

## Base de données

Appliquer `supabase/migrations/20261015183500_create_deals.sql` au projet Supabase cible.

## Exécution locale

```bash
SUPABASE_URL=https://<project>.supabase.co SUPABASE_KEY=<service-or-api-key> python3 lootzero.py
```

Le workflow `.github/workflows/check.yml` s’exécute toutes les 30 minutes et peut aussi être lancé manuellement.
