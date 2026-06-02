# Polymorphic Seed Registry

Status: data-contract proposal.

This registry is a conservative bridge between the current world model and the
larger production-hardening proposal. It lets HFF store different seed record
types without flattening them into the same kind of claim.

## Why this exists

The repo now has review gates for high-impact claims and a read-only bio-threat
registry. The next gap is seed typing: laws, science, philosophy, literature,
history, immutable constraints, model types, and speculative future models should
not all be treated as ordinary facts.

The registry keeps those categories separate and marks speculative future models
as low-confidence planning objects, not current evidence.

## Scope

Included:

- typed seed records
- source references and limitations
- explicit uncertainty statements
- speculative future model defaults
- read-only registry safety flags
- tests proving speculative records cannot become current facts or autonomous action

Not included:

- runtime integration
- database persistence
- dashboard exposure
- polling
- autonomous action
- accepted-fact promotion
- mesh sync
- deployment changes

## Seed kinds

```text
science
law
ethics
philosophy
literature
history
model_type
immutable_constraint
speculative_future_model
unknown
```

## Speculative future model rule

Speculative future models are allowed only as low-confidence predictive structures.

Required posture:

```text
kind: speculative_future_model
status: low_confidence_predictive
operational_assumption: false
used_for: stress testing and safety planning
not_used_for: current factual claims, public authority, autonomous action
```

They cannot drive autonomous action. They cannot become current facts just
because they are useful for safety planning.

## Relationship to perfect-adjacent review

The perfect-adjacent review route blocks overclaims and impossible claims. This
registry gives that route a cleaner upstream structure: a record can be
scientific evidence, a legal constraint, a philosophical principle, a literary
case, a model type, or a speculative future model without pretending all of those
are the same epistemic object.

## Validation

```powershell
$env:PYTHONPATH = (Get-Location).Path
python -m py_compile .\polymorphic_seed_registry.py .\tests\test_polymorphic_seed_registry.py
python .\tests\test_polymorphic_seed_registry.py
```
