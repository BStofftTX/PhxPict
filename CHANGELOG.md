# Changelog

All notable changes to PhxPict are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [Unreleased]

### Changed
- CLI indexing now validates the photo-library folder before opening SQLite.
- Core indexing tests use the deterministic filename provider and never load a
  visual model or contact a model host.

### Added
- Formal release-change record for the controlled private-beta program.

### Security and privacy
- PhxPict is designed for local-first indexing. Private-beta releases must not add
  telemetry, cloud inference, or photo uploads without a documented review.
