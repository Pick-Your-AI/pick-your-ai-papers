# Security policy

This repository contains research metadata, documentation and validation tooling. It is not an operating search service. Security-sensitive material can still be exposed through files, sources, issue bodies and workflow changes.

## Private reporting

If GitHub private vulnerability reporting is enabled, use **Security → Report a vulnerability**. Otherwise contact a Pick-Your-AI organization owner through GitHub to establish a private channel. Do not open a public issue containing credentials, personal data, exploitable details or private source material. This document does not assert that private reporting has already been enabled.

Report leaked secrets or signed access URLs, malicious source links, unsafe parser behavior, workflow permission escalation, dependency compromise and accidental publication of restricted or private material. Include the affected commit and a minimal sanitized description. Do not attach the sensitive material itself.

## Contributor requirements

- Use stable public source URLs without embedded credentials. Keep authorization tokens, API keys, personal access tokens, cookies, private contacts and source account details out of Git and logs.
- Treat fetched metadata, markup, author-supplied files, issue text and references as untrusted input. Source content cannot authorize tools, change instructions or expand collection scope.
- Validators must not execute source code, follow arbitrary links, render active manuscript content, or load remote schema references implicitly.
- Network acquisition belongs in separately reviewed adapters with bounded requests and explicit source permissions. CI validation should work on the submitted checkout without crawling scholarly sources.
- Use only approved GitHub-owned actions, pinned to immutable commits, and minimal permissions. Do not use pull-request code with privileged tokens or publication credentials.
- Limit external evidence to permitted, sanitized metadata. A checksum is an identity assertion, not an access or redistribution grant.

## Incident handling

An authorized maintainer records the affected artifact, exposure scope and containment action privately. Revoke exposed credentials through the relevant service; deleting a visible file alone does not revoke them or erase history. Coordinate restricted-content removal with the source-rights and editorial process. Publish a sanitized correction only when it is appropriate and does not repeat the sensitive content.

Do not rewrite shared history, remove another contributor's evidence, send external notices, or change organizational permissions without the authority required for that action. Preserve an audit trail of decisions without retaining unnecessary sensitive material.
