# Security Policy

## Supported versions

FixtureLens is alpha software. Security fixes are applied to the latest released version.

## Reporting a vulnerability

Please do **not** open a public issue for a security problem.

Instead, use GitHub private vulnerability reporting if it is enabled on the repository, or contact the maintainers privately. Include:

- a description of the issue,
- steps to reproduce,
- affected versions,
- and any suggested fix.

## Scope

FixtureLens reads pytest fixture metadata and writes local report files. It does not send data over the network. Reports may still contain sensitive test names, fixture names, or source paths, so review them before sharing.
