# Tithika Intelligence Architecture

Tithika Intelligence is an explainable orchestration layer above the deterministic Panchang, Muhurat and Jyotish engines. It does **not** replace astronomical or traditional-rule calculations with generated values.

## Six production layers

1. **Intelligence Core** — registry for deterministic engines, provenance/confidence envelopes, short-lived non-personal cache and synthesis-provider routing.
2. **Panchang / Muhurat Advisor** — ranks verified Choghadiya periods, Panchang Muhurtas and supported purpose-specific Muhurat profiles for today or a seven-day range.
3. **Jyotish Intelligence** — fuses Janma Kundali, complete Shadbala, D9, Yoga rules, Vimshottari and current planetary positions.
4. **Conversational Tithika** — natural-language intent routing into advisor, Jyotish, profile and quality services; it requests required birth inputs rather than fabricating them.
5. **Recommendation / Profile Engine** — applies explicit user preferences after verified calculation. Profile data is request-scoped and is not persistently cached by the intelligence service.
6. **Quality AI** — cross-engine invariants and anomaly detection, including solar-event ordering, Choghadiya period counts, Panchang state completeness and cross-engine sunrise drift.

## Evidence contract

Every successful response contains an `intelligence` object with:

- service/version/mode;
- synthesis provider;
- cache policy;
- normalized confidence;
- engine-level provenance with version and source category;
- explicit system boundaries.

Categories separate calculated facts, calculated strengths, traditional rules and orchestration. Generated synthesis is never allowed to invent Tithi, Nakshatra, planetary longitude or Muhurat timestamps.

## Multi-provider design

The default provider is deterministic synthesis. An optional HTTP JSON synthesis provider can be enabled with:

- `TITHIKA_AI_EXTERNAL=1`
- `TITHIKA_AI_ENDPOINT=<gateway URL>`
- `TITHIKA_AI_API_KEY=<optional bearer token>`

External synthesis is disabled by default. For Jyotish, only compact derived findings are sent to the provider; raw birth payloads are not passed to it.

## Cache/privacy

The filesystem TTL cache is limited to non-personal advisor context. Jyotish and profile requests declare persistent cache disabled. The cache defaults to the operating-system temporary directory and can be overridden with `TITHIKA_AI_CACHE_DIR`.

## HTTP surface

The PHP API exposes:

- `ai-health`
- `ai-advisor`
- `ai-jyotish`
- `ai-ask`
- `ai-profile`
- `ai-quality`

The premium UI is available at the dedicated `/intelligence/` pretty route. It is intentionally outside the historical 292-page product-route certification contract so the existing public map remains stable while the intelligence product evolves independently.
