# CHECKPOINT_06

date: 2026-04-12

## Title

Active CLI defaults detached from archived `GU2` manifests

## Summary

- The active manifest set was switched away from archived `GU2` documents and
  templates.
- The following active manifests now point at the neutral platform-owned sample
  baseline:
  - `/Users/nihao/Documents/Playground/document-ops-system/manifests/baseline.yml`
  - `/Users/nihao/Documents/Playground/document-ops-system/manifests/template_profile.yml`
  - `/Users/nihao/Documents/Playground/document-ops-system/manifests/write_contract.yml`
  - `/Users/nihao/Documents/Playground/document-ops-system/manifests/layout_contract.yml`
- The prior `GU2` versions of those manifests were preserved under:
  - `/Users/nihao/Documents/Playground/document-ops-system/archive/legacy_profiles/gu2/manifests`
- Default CLI verification passed after the cutover:
  - `show-config`
  - `import-baseline`

## Boundary

- Archived `GU2` case material remains available for historical review.
- The active OfficeX toolchain no longer requires archived `GU2` files for its
  default baseline and template profile.

## Follow-up

- remove or archive remaining non-runtime active-path `GU2` references
- replace report-oriented compatibility names when the runtime contracts are
  stable enough for a package migration
