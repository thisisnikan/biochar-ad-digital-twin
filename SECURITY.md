# Security policy

## Supported version

This research prototype currently supports the latest commit on `main`.

## Reporting a vulnerability

Do not open a public issue for credentials, private datasets, personally identifiable
information or another sensitive disclosure. Contact the repository owner privately through
the owner's GitHub profile and include the affected component, reproduction steps and
potential impact.

## Data protection boundary

The repository must never contain API keys, access tokens or author-shared source files without
explicit redistribution permission. `data/private/` and `results/private/` are ignored as a
second line of defence; contributors remain responsible for reviewing staged changes before
every commit.
