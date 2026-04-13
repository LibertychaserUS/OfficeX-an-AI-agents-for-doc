# Package Contract

The active product is `Document Operations System`.

The current implementation still uses the compatibility package:

- `tools.report_scaffold_v3`

## Purpose

The package contract exists so the platform does not drift into an accidental
file pile.

## Rule

A module is considered active only when it is:

1. part of the package contract
2. importable
3. reachable from real execution paths when appropriate
4. covered by tests
5. reflected in operator-facing docs when behavior changes

## Compatibility Boundary

The package name may stay historical for a transition period, but product docs
must not mistake the implementation detail for the product identity.
