# Research validation fixture boundary

Mutation fixtures are constructed in temporary directory copies by `tests/test_research.py`. Invented reviews, permissions, integrity checks and publication receipts use `synthetic` IDs and `example.org` URLs and are test-only. They never enter the real catalog, evidence register or a publication artifact.

The tests include a complete synthetic eligibility path and then remove one condition at a time, so the release gate is tested for field-specific and operation-specific permission rather than merely rejecting every record. They also test missing execution evidence, false verification labels, borrowed citation checks, identity collisions, private/raw material and exact publication-byte binding.
