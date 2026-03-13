# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/) and versioning follows [PEP 440](https://peps.python.org/pep-0440/) and Python packaging conventions.

## [unreleased]

### Added

- Added CodeQL and OpenSSF vulnerability scanning.
- Improved package management and upgrade constraints.

### Changed

- None documented yet.

### Deprecated

- None documented yet.

### Removed

- Smithery support has been removed.

### Fixed

- AirTable vulnerability scan improvements.

### Security

- None documented yet.

## [0.4.3] - 2025-12-02

### Added

- Improved middleware.
- Dockerfile and vulnerability improvements.

## [0.4.2] - 2025-12-02

### Added

- Strip unknown arguments passed to tool calls from systems such as n8n.

### Fixed

- Multiple configuration issues.

## [0.4.1] - 2025-11-26

### Added

- Setup new tooling.
- Added `ToolResult` metadata.

## [0.4.0.post1] - 2025-10-17

### Fixed

- Corrected Python version restriction for backward compatibility with some dependencies.

## [0.4.0] - 2025-10-17

### Added

- Enabled LRU and TTL caches for historical and latest rates lookups.

## [0.3.6] - 2025-09-11

### Fixed

- Corrected pytest fixture.

## [0.3.5.post0] - 2025-09-07

### Fixed

- Corrected copyright statement in LICENSE and added an AUTHORS file.

## [0.3.5] - 2025-09-07

### Fixed

- Smithery configuration fixed by contribution from Smithery staff.

## [0.3.4] - 2025-08-17

### Added

- Updated Smithery configuration and Dockerfile to cater for HTTP transport.

## [0.3.3] - 2025-08-01

### Added

- Changes to tooling.

## [0.3.2] - 2025-07-08

### Added

- Some LLMs pass a single currency, as a string, for obtaining rates. It needs to be converted to a list.
- Slightly reworded documentation for tool parameters.

## [0.3.1] - 2025-07-04

### Added

- Fixed metadata errors with FastMCP version upgrade.

## [0.3.0] - 2025-06-29

### Added

- Improved tool documentation and parameter signatures.

## [0.2.9] - 2025-06-27

### Added

- Brought back Smithery deployment.
- Default transport is now `stdio`.

## [0.2.8] - 2025-06-26

### Added

- Updates to project metadata and improved handling of primitive types for `TextContent` responses.

## [0.2.7] - 2025-06-24

### Added

- Changed experimental metadata to appear in a namespace to avoid collisions.
- Extended `meta` in `TextContent`, if it exists.

## [0.2.6] - 2025-06-23

### Added

- Added more metadata to `TextContent` responses, such as API call status, bytes downloaded and duration in microseconds.

## [0.2.5] - 2025-06-21

### Added

- Added experimental metadata in MCP responses.

## [0.2.4] - 2025-06-19

### Removed

- Smithery deployment abandoned for now.
- `FAST_MCP_HOST` and `FAST_MCP_PORT` are no longer supported directly by FastMCP since version 2.8.1, but supported by this FrankfurterMCP.

## [0.2.3] - 2025-06-14

### Added

- Dockerfile optimisations.

## [0.2.2] - 2025-06-13

### Added

- Fixes Smithery deployment.

## [0.2.1] - 2025-06-13

### Added

- Fixes to Dockerfiles to enable passing environment variables.

## [0.2.0] - 2025-06-12

### Added

- Added a command line interface to show tools information from a running instance of the server using either the `sse` or the `streamable-http` transport.
- Code re-organisation.
- Updated documentation in the README.

## [0.1.8] - 2025-06-12

### Added

- Improved code and annotations.

## [0.1.6] - 2025-06-09

### Added

- Added containerisation.
- Added support for self-signed certificates for proxy servers and custom endpoints.

## [0.1.5] - 2025-06-08

### Added

- Added currency conversion for specific dates.
- Added `uvicorn` graceful shutdown timeout limit.

## [0.1.2] - 2025-06-08

### Added

- Implemented the basic functionality.
- Published the package to [PyPI](https://pypi.org/project/frankfurtermcp/).


[unreleased]: https://github.com/anirbanbasu/frankfurtermcp/compare/v.0.4.3...HEAD
[0.4.3]: https://github.com/anirbanbasu/frankfurtermcp/compare/v.0.4.2...v.0.4.3
[0.4.2]: https://github.com/anirbanbasu/frankfurtermcp/compare/v.0.4.1...v.0.4.2
[0.4.1]: https://github.com/anirbanbasu/frankfurtermcp/compare/v.0.4.0.post1...v.0.4.1
[0.4.0.post1]: https://github.com/anirbanbasu/frankfurtermcp/compare/v.0.4.0...v.0.4.0.post1
[0.4.0]: https://github.com/anirbanbasu/frankfurtermcp/compare/v.0.3.6...v.0.4.0
[0.3.6]: https://github.com/anirbanbasu/frankfurtermcp/compare/v.0.3.5.post0...v.0.3.6
[0.3.5.post0]: https://github.com/anirbanbasu/frankfurtermcp/compare/v.0.3.5...v.0.3.5.post0
[0.3.5]: https://github.com/anirbanbasu/frankfurtermcp/compare/v.0.3.4...v.0.3.5
[0.3.4]: https://github.com/anirbanbasu/frankfurtermcp/compare/v.0.3.3...v.0.3.4
[0.3.3]: https://github.com/anirbanbasu/frankfurtermcp/compare/v.0.3.2...v.0.3.3
[0.3.2]: https://github.com/anirbanbasu/frankfurtermcp/compare/v.0.3.1...v.0.3.2
[0.3.1]: https://github.com/anirbanbasu/frankfurtermcp/compare/v.0.3.0...v.0.3.1
[0.3.0]: https://github.com/anirbanbasu/frankfurtermcp/compare/v.0.2.9...v.0.3.0
[0.2.9]: https://github.com/anirbanbasu/frankfurtermcp/compare/v.0.2.8...v.0.2.9
[0.2.8]: https://github.com/anirbanbasu/frankfurtermcp/compare/v.0.2.7...v.0.2.8
[0.2.7]: https://github.com/anirbanbasu/frankfurtermcp/compare/v.0.2.6...v.0.2.7
[0.2.6]: https://github.com/anirbanbasu/frankfurtermcp/compare/v.0.2.5...v.0.2.6
[0.2.5]: https://github.com/anirbanbasu/frankfurtermcp/compare/v.0.2.4...v.0.2.5
[0.2.4]: https://github.com/anirbanbasu/frankfurtermcp/compare/v.0.2.3...v.0.2.4
[0.2.3]: https://github.com/anirbanbasu/frankfurtermcp/compare/v.0.2.2...v.0.2.3
[0.2.2]: https://github.com/anirbanbasu/frankfurtermcp/compare/v.0.2.1...v.0.2.2
[0.2.1]: https://github.com/anirbanbasu/frankfurtermcp/compare/v.0.2.0...v.0.2.1
[0.2.0]: https://github.com/anirbanbasu/frankfurtermcp/compare/v.0.1.8...v.0.2.0
[0.1.8]: https://github.com/anirbanbasu/frankfurtermcp/compare/v.0.1.6...v.0.1.8
[0.1.6]: https://github.com/anirbanbasu/frankfurtermcp/compare/v.0.1.5...v.0.1.6
[0.1.5]: https://github.com/anirbanbasu/frankfurtermcp/compare/v.0.1.2...v.0.1.5
[0.1.2]: https://github.com/anirbanbasu/frankfurtermcp/compare/v.0.0.1...v.0.1.2
