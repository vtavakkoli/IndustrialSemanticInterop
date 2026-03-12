# Protocol Scope (Honest Boundaries)

## IEEE 1451-style adapter
Implemented:
- TEDS-like metadata fields (`manufacturer`, `model_number`, `serial_number`).
- Channel + scalar measurement ingestion.
Not implemented:
- Full IEEE 1451 command classes, timing profiles, transducer electronic interface details.

## IEC 61499-style adapter
Implemented:
- Representative function-block exchange payload (`fb_type`, `event`, `data`, `metadata`).
Not implemented:
- Runtime execution engine, distributed deployment lifecycle, management model.

## OPC UA bridge adapter
Implemented:
- Node-write style payload (`node_id`, value, timestamp, status).
Not implemented:
- Live OPC UA server/session, subscription model, security policy negotiation.

## Hybrid pipeline
Implemented:
- Controlled chaining from canonical message to OPC UA representation and onward to IEC 61499-style exchange payload.
Not implemented:
- Runtime co-simulation with live middleware or production-grade transport.
