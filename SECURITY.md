# Security

Report security issues through the repository's private vulnerability reporting
flow or through the maintainer contact listed in the package metadata.

For this repo, security-sensitive issues include:

- protocol signatures that expose secrets or credentials;
- contracts that serialize sensitive values without redaction;
- imports that pull implementation packages into SPI;
- validation gaps that allow unsafe protocol or contract shapes;
- compatibility changes that could cause downstream implementations to silently
  skip authorization, validation, or audit behavior.

Do not include credentials, tokens, private keys, or production payloads in a
public issue, PR, or discussion.
