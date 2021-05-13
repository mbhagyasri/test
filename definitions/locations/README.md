# Locations/Instances

Each location represents a platform instance.

- Each instance has its own subdomain and we expect copies of core platform services (IDP)
- Instances may share existing AWS account and other integrations.

So for example: USA - One instance of the platform may consist of several EKS clusters in different AWS regions but they sit behind the same DNS domain.
