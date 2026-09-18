# Clean-Room and Sanitization Record

The private source inventory contained unsafe material, including plaintext
credentials, internal host and domain names, email addresses, network
addresses, employee names, customer references, environment labels, and
company-specific operational procedures.

## Excluded

- Original scripts and command sequences
- Password, token, key, and service-account values
- Hostnames, IP addresses, domains, directory paths, and email addresses
- Customer, employee, application, datacenter, and ticket identifiers
- Internal approval chains, support groups, and change procedures
- Employer templates, diagrams, documentation, and proprietary terminology

## Public Project Method

1. Identify only broad, transferable engineering themes.
2. Design a new generic data model and workflow.
3. Write implementation and tests from scratch.
4. Use fictional hosts, owners, environments, and policies.
5. Scan the completed project for company identifiers, secrets, private
   addresses, and source-artifact strings before publication.

The original downloaded material must remain private and must not be committed
to this or any other public repository.

