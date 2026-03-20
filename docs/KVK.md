# KVK lookup (Basisprofiel)

## Backend

- **Endpoint:** `GET /kvk/lookup/{8-cijferig_nummer}`
- **Official API:** [KVK Basisprofiel](https://developers.kvk.nl/nl/documentation/basisprofiel-api) — `https://api.kvk.nl/api/v1/basisprofielen?kvkNummer=...`
- **Auth:** HTTP header `apikey: <KVK_API_KEY>` (aanvragen op [developers.kvk.nl](https://developers.kvk.nl/nl/apply-for-apis))

## Environment

| Variable | Description |
|----------|-------------|
| `KVK_API_KEY` | Productie / test key van KVK |
| `KVK_API_BASE` | Default `https://api.kvk.nl` (optioneel test-URL) |
| `KVK_USE_MOCK` | `true` = alleen ingebouwde testnummers |

## Zonder API key

Zonder key werken alleen **mock-testnummers**:

- `12345678` — fictief bedrijf (Bakkerij-voorbeeld uit BrewTag HTML)
- `69599084` — voorbeeld uit KVK-documentatie (Bol.com — bij live API echt profiel)

## Frontend

`KvkLookup` op `/beer/order` roept het backend-endpoint aan via dezelfde API-base als de beer-endpoints (`NEXT_PUBLIC_API_URL` of rewrite).
