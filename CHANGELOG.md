# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/) and versioning follows [PEP 440](https://peps.python.org/pep-0440/) and Python packaging conventions.

## [unreleased]

### Added

- None documented yet.

### Changed

- None documented yet.

### Deprecated

- None documented yet.

### Removed

- None documented yet.

### Fixed

- None documented yet.

### Security

- None documented yet.

## [0.4.6] - 2026-06-19

### Added

- None documented yet.

### Changed

- Upgraded dependencies.

### Deprecated

- None documented yet.

### Removed

- None documented yet.

### Fixed

- Multiple vulnerabilities fixed as shown below.

| OSV URL | CVSS | ECOSYSTEM | PACKAGE | VERSION | FIXED VERSION | SOURCE |
|---|---|---|---|---|---|---|
| https://osv.dev/GHSA-537c-gmf6-5ccf | 7.5  | PyPI      | cryptography     | 48.0.0  | 48.0.1        | uv.lock |
| https://osv.dev/PYSEC-2026-175  and https://osv.dev/GHSA-993g-76c3-p5m4  | 4.2  | PyPI      | pyjwt            | 2.12.1  | 2.13.0        | uv.lock |
| https://osv.dev/PYSEC-2026-177 and https://osv.dev/GHSA-fhv5-28vv-h8m8   | 3.7  | PyPI      | pyjwt            | 2.12.1  | 2.13.0        | uv.lock |
| https://osv.dev/PYSEC-2026-178 and https://osv.dev/GHSA-w7vc-732c-9m39  | 5.3  | PyPI      | pyjwt            | 2.12.1  | 2.13.0        | uv.lock |
| https://osv.dev/PYSEC-2026-179 and https://osv.dev/GHSA-xgmm-8j9v-c9wx  | 7.4  | PyPI      | pyjwt            | 2.12.1  | 2.13.0        | uv.lock |
| https://osv.dev/GHSA-jq35-7prp-9v3f | 5.4  | PyPI      | pyjwt            | 2.12.1  | 2.13.0        | uv.lock |
| https://osv.dev/GHSA-5rvq-cxj2-64vf | 7.5  | PyPI      | python-multipart | 0.0.29  | 0.0.30        | uv.lock |
| https://osv.dev/GHSA-6jv3-5f52-599m | 3.7  | PyPI      | python-multipart | 0.0.29  | 0.0.30        | uv.lock |
| https://osv.dev/GHSA-v9pg-7xvm-68hf | 3.7  | PyPI      | python-multipart | 0.0.29  | 0.0.31        | uv.lock |
| https://osv.dev/GHSA-vffw-93wf-4j4q | 3.7  | PyPI      | python-multipart | 0.0.29  | 0.0.30        | uv.lock |
| https://osv.dev/PYSEC-2026-161 and https://osv.dev/GHSA-86qp-5c8j-p5mr | 6.5  | PyPI      | starlette        | 1.0.0   | 1.0.1         | uv.lock |
| https://osv.dev/GHSA-82w8-qh3p-5jfq | 7.5  | PyPI      | starlette        | 1.0.0   | 1.3.1         | uv.lock |
| https://osv.dev/GHSA-jp82-jpqv-5vv3 | 3.7  | PyPI      | starlette        | 1.0.0   | 1.3.0         | uv.lock |
| https://osv.dev/GHSA-wqp7-x3pw-xc5r | 7.5  | PyPI      | starlette        | 1.0.0   | 1.1.0         | uv.lock |
| https://osv.dev/GHSA-x746-7m8f-x49c | 5.3  | PyPI      | starlette        | 1.0.0   | 1.1.0         | uv.lock |


### Security

- None documented yet.

## [0.4.5] - 2026-05-12

### Added

- None documented yet.

### Changed

- Upgraded dependencies.

### Removed

- Smithery support has been removed.

### Fixed

- Vulnerabilities fixed as shown below.

| OSV URL | CVSS | ECOSYSTEM | PACKAGE | VERSION | FIXED VERSION | SOURCE |
|---|---|---|---|---|---|---|
| https://osv.dev/GHSA-m8x7-r2rg-vh5g | 6.7 | PyPI | fastmcp | 3.1.1 | 3.2.0 | uv.lock |
| https://osv.dev/GHSA-rww4-4w9c-7733 | 8.2 | PyPI | fastmcp | 3.1.1 | 3.2.0 | uv.lock |
| https://osv.dev/GHSA-vv7q-7jx5-f767 | 10.0 | PyPI | fastmcp | 3.1.1 | 3.2.0 | uv.lock |


### Security

- None documented yet.

## [0.4.4] - 2026-03-26

### Added

- Added CodeQL and OpenSSF vulnerability scanning.
- Added a CHANGELOG file.
- Added the means to use a local Frankfurter API server with the Docker compose setup.

### Changed

- Improved package management and upgrade constraints.

### Removed

- Smithery support has been removed.

### Fixed

- AirTable vulnerability scan improvements.

### Security

- The following vulnerabilities exist.

| OSV URL | CVSS | ECOSYSTEM | PACKAGE | VERSION | FIXED VERSION | SOURCE |
|---|---|---|---|---|---|---|
| https://osv.dev/GHSA-5239-wwwm-4pmq | 3.3 | PyPI | pygments | 2.19.2 | -- | uv.lock |

## [0.4.3] - 2026-01-15

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


[unreleased]: https://github.com/anirbanbasu/frankfurtermcp/compare/v.0.4.6...HEAD
[0.4.6]: https://github.com/anirbanbasu/frankfurtermcp/compare/v.0.4.5...v.0.4.6
[0.4.5]: https://github.com/anirbanbasu/frankfurtermcp/compare/v.0.4.4...v.0.4.5
[0.4.4]: https://github.com/anirbanbasu/frankfurtermcp/compare/v.0.4.3...v.0.4.4
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
