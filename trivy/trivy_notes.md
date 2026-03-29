# Trivy: Detailed Study Notes

## What Trivy Is

Trivy is an all-in-one open-source security scanner maintained by Aqua Security. Its job is to inspect software artifacts and identify security issues before those artifacts move further into build, release, or deployment workflows.

Trivy is widely used because one tool can cover multiple security checks that otherwise require separate scanners.

## Definition in One Line

Trivy is a security scanner that detects:

- vulnerabilities
- misconfigurations
- secrets
- license issues

across targets such as:

- container images
- filesystems
- code repositories
- infrastructure-as-code files
- Kubernetes resources
- SBOM documents
- cloud accounts and some VM targets

## What Trivy Can Scan

The most important Trivy targets are:

- `trivy image` for container images
- `trivy fs` for local filesystems and project folders
- `trivy repo` for local or remote repositories
- `trivy config` for configuration and IaC scanning
- `trivy k8s` for Kubernetes cluster and workload scanning
- `trivy sbom` for scanning SBOM files
- `trivy aws` for AWS account misconfiguration scanning
- `trivy vm` for selected VM image use cases

This target-based design is one of Trivy's biggest strengths. The command changes depending on what you are scanning, but the security model remains consistent.

## Important Terms

Some Trivy terms appear often and are worth defining clearly.

### CVE

CVE stands for Common Vulnerabilities and Exposures. It is a public identifier used to track known security vulnerabilities.

### IaC

IaC means Infrastructure as Code. These are configuration files that define infrastructure and deployment behavior, such as:

- Terraform
- Kubernetes YAML
- Dockerfiles
- Helm-related files
- CloudFormation

### SBOM

SBOM means Software Bill of Materials. It is a structured inventory of the components inside a software artifact, such as a container image or application package.

### SARIF

SARIF is a machine-readable output format used by security and code analysis tools so findings can be imported into platforms such as code scanning dashboards.

## What Trivy Looks For

Trivy is not limited to one type of finding.

### 1. Vulnerabilities

Trivy detects known vulnerabilities in:

- OS packages
- language-specific dependencies
- some non-packaged software
- Kubernetes components

This is the CVE-focused part of Trivy. It compares detected software against vulnerability data sources and reports issues by severity.

### 2. Misconfigurations

Trivy can detect insecure configuration patterns in:

- Dockerfiles
- Kubernetes YAML
- Terraform
- CloudFormation
- Helm-related configuration files

Examples of misconfigurations include:

- containers running as root
- overly broad network exposure
- missing encryption settings
- insecure defaults in infrastructure definitions

### 3. Secrets

Trivy can detect exposed secrets such as:

- passwords
- API keys
- tokens
- cloud credentials
- private keys

Secret scanning is especially useful in repositories, filesystems, and container images where credentials may be accidentally committed or copied.

### 4. License Issues

Trivy can also inspect package license information. This matters less for pure vulnerability management, but it is useful for compliance and legal review.

## How Trivy Works Internally

Trivy follows a practical internal flow:

1. determine the target type
2. enable the relevant scanners
3. inspect files, manifests, package metadata, or image layers
4. identify software components and configuration objects
5. compare findings with cached vulnerability and policy data
6. output the results in the selected format

The core internal building blocks are:

- target acquisition
- package and dependency detection
- vulnerability matching
- misconfiguration policy checks
- secret detection rules
- report generation

## Target Acquisition

The first internal step is understanding the target.

Examples:

- `trivy image nginx:latest` means inspect a container image
- `trivy fs .` means recursively inspect the current directory
- `trivy repo .` means scan the repository structure
- `trivy config .` means analyze config and IaC files for misconfigurations

For container images, Trivy can look in several places such as:

- local Docker
- containerd
- Podman
- remote container registries
- tar archives
- OCI layouts

This is why Trivy fits naturally into both local development and CI/CD environments.

## Vulnerability Detection Logic

When Trivy runs vulnerability scans, it first detects software packages and dependency manifests. Then it maps them to vulnerability advisories.

Important points:

- for OS packages, Trivy prefers vendor security advisories
- for language ecosystems, Trivy uses ecosystem-specific data sources
- vendor severity can differ from public CVSS scoring
- the same package may appear as fixed in one distribution and still vulnerable in another

This explains why Trivy results must be interpreted in the context of the actual package source and operating system.

## Misconfiguration Detection Logic

Trivy does not use CVE matching for configuration scans. Instead, it checks files against predefined security rules and policies.

That means it can flag insecure patterns even when there is no CVE involved.

Example idea:

- a Docker image may have no critical package vulnerability
- but the Dockerfile or Kubernetes manifest may still be insecure

This is why `trivy config` is different from `trivy image`.

## Secret Detection Logic

Trivy's secret scanner walks plaintext files and looks for patterns that match known secret formats or risky credential shapes.

This works well for:

- access tokens
- cloud keys
- passwords in config files
- private keys accidentally committed into a repository

Because this is pattern-based detection, results sometimes need human validation. Some findings will be real secrets, while others may be test strings or false positives.

## Installation Options

Trivy supports several installation paths.

Common ones are:

- `brew install trivy`
- official package manager installation on Linux
- GitHub release binary download
- official container image such as `aquasec/trivy`

For quick use in container-focused workflows, the official Trivy image is often convenient. For CI agents and developer laptops, a native binary installation is usually simpler.

## Quick Start Flow

If someone is learning Trivy for the first time, a practical learning path is:

1. install Trivy
2. check the version
3. scan a container image
4. scan a project directory
5. scan configuration files
6. add filters such as severity and exit codes
7. export results in JSON, SARIF, CycloneDX, or SPDX
8. integrate the scan into CI/CD

Simple first commands:

- `trivy --version`
- `trivy image python:3.4-alpine`
- `trivy fs .`
- `trivy config .`

## Configuration Precedence

Trivy supports three main ways to supply settings:

1. CLI flags
2. environment variables
3. configuration file

The official configuration precedence is:

- CLI flags override everything
- environment variables override config file settings
- configuration file provides defaults

Examples:

- `TRIVY_DEBUG=true trivy image alpine:3.15`
- `trivy --config /etc/trivy/myconfig.yaml image alpine:3.15`

This is useful in CI/CD because teams often keep shared defaults in `trivy.yaml` and override only a few values in the pipeline.

## Core Commands

These are the most useful Trivy commands to remember.

### Scan a Container Image

- `trivy image nginx:latest`

Use this when you want to scan a built or pulled container image for vulnerabilities and other enabled scanner findings.

Additional useful image examples:

- `trivy image python:3.4-alpine`
- `trivy image --severity HIGH,CRITICAL nginx:latest`
- `trivy image --ignore-unfixed nginx:latest`
- `trivy image --format json --output result.json nginx:latest`
- `trivy image --input ruby-3.1.tar`

### Scan a Filesystem

- `trivy fs .`

Use this when you want to scan a local project directory for dependency vulnerabilities and secrets.

Additional useful filesystem examples:

- `trivy fs /path/to/project`
- `trivy fs --scanners vuln,secret,misconfig .`

### Scan a Repository

- `trivy repo .`
- `trivy repo https://github.com/example/project`

Use this when you want repository-oriented scanning of local or remote code.

### Scan Config and IaC Files

- `trivy config .`

Use this when you want to inspect configuration files for misconfigurations.

Additional useful config examples:

- `trivy config .`
- `trivy config --misconfig-scanners=terraform,dockerfile .`

### Scan a Kubernetes Cluster

- `trivy k8s --report=summary`

Use this when you want a cluster-level security overview for workloads and resources.

Additional useful Kubernetes examples:

- `trivy k8s --report summary`
- `trivy k8s --include-namespaces kube-system --report summary`
- `trivy k8s kind-kind --report summary`

### Scan an SBOM

- `trivy sbom ./sbom.spdx`
- `trivy sbom ./sbom.cdx.json`

Use this when you already have an SBOM and want Trivy to analyze it for vulnerabilities or licenses.

### Scan AWS for Misconfigurations

- `trivy aws --region us-east-1`
- `trivy aws --service s3`

Use this when you want to inspect a live AWS environment for misconfigurations.

Important note:

- `trivy aws` is experimental in the official docs
- it focuses on cloud misconfiguration scanning rather than normal image vulnerability scanning

### Scan VM Targets

- `trivy vm ami:ami-0123456789abcdefg`
- `trivy vm ebs:snap-0123456789abcdefg`

Use this when you need vulnerability scanning on supported VM-related artifacts, especially in AWS-oriented workflows.

### Run in Server Mode

- `trivy server`

Use this when you want client/server style scanning instead of every client handling all scan logic directly.

## High-Value Flags

These flags make Trivy much more practical in real environments.

### Filter by Severity

- `--severity HIGH,CRITICAL`

This limits the report to the findings you care about most urgently.

### Ignore Unfixed Vulnerabilities

- `--ignore-unfixed`

This hides vulnerabilities for which no fix is currently available. Teams often use this to reduce noise during pipeline enforcement.

### Select Scanners Explicitly

- `--scanners vuln,misconfig,secret`

This tells Trivy exactly what to scan for.

Examples:

- `trivy image --scanners vuln,secret nginx:latest`
- `trivy fs --scanners secret .`
- `trivy image --scanners vuln alpine:3.19`

The most common scanner names are:

- `vuln`
- `misconfig`
- `secret`
- `license`

### Write Machine-Readable Output

- `--format json`
- `--format sarif`
- `--format cyclonedx`
- `--output results.json`

This is important for CI/CD, dashboards, artifact storage, and automated policy checks.

### Fail the Build Based on Findings

- `--exit-code 1`

This is how Trivy becomes a pipeline gate instead of only a reporting tool.

Example:

- `trivy image --severity HIGH,CRITICAL --exit-code 1 myimage:latest`

### Download Databases Ahead of Time

- `--download-db-only`

This is useful for controlled environments, prewarming caches, or pipeline optimization.

### Run with Offline Data

- `--offline-scan`

This is useful when the environment has restricted network access and the database has already been downloaded.

### Control Noise with Ignore Files

- `.trivyignore`
- `--ignorefile`

These are useful when a team has reviewed certain findings and wants to avoid repeated noise.

## Detailed Target Notes

## 1. Container Image Scanning

Container image scanning is one of Trivy's most common and most important use cases.

What Trivy checks in an image:

- base operating system packages
- application dependencies
- some bundled software components
- optionally secrets and misconfigurations depending on scanners enabled

Why this matters:

- many risks come from base images rather than custom app code
- outdated packages in parent images affect downstream images
- teams often discover issues before pushing an image to a registry

What the report usually shows:

- target image name
- package name
- installed version
- fixed version if available
- vulnerability ID
- severity

This makes `trivy image` a strong checkpoint before push, release, or deployment.

## 2. Filesystem Scanning

Filesystem scanning is useful before an image even exists.

What `trivy fs` is good for:

- scanning local project directories
- detecting vulnerable dependencies
- finding secrets in files
- optionally detecting IaC misconfigurations in the same path

This is a strong shift-left pattern because security checks happen earlier in development.

## 3. Repository Scanning

Repository scanning is similar to filesystem scanning, but it is repository-aware and can work with local or remote repositories.

Useful cases:

- scanning a remote Git repository directly
- reviewing a branch or repository without building an image first
- security checks in Git-based workflows

Examples:

- `trivy repo /path/to/your/repository`
- `trivy repo https://github.com/knqyf263/trivy-ci-test`

## 4. Configuration and IaC Scanning

`trivy config` is used to inspect infrastructure and deployment definitions.

Common file types:

- Terraform
- Kubernetes manifests
- Dockerfiles
- CloudFormation
- Helm-related configuration
- Ansible

This is a very important Trivy capability because many serious incidents happen due to insecure configuration, not only vulnerable packages.

Examples of what Trivy may flag:

- privileged containers
- risky security contexts
- open access patterns
- missing encryption settings
- weak infrastructure defaults

Trivy also supports:

- selecting a subset of misconfiguration scanners
- custom checks with Rego
- compliance-oriented reporting

Examples:

- `trivy config --misconfig-scanners=terraform,dockerfile .`
- `trivy config --config-check ./policy.rego --namespaces user ./configs`

This is valuable when built-in checks are not enough and an organization needs custom policy enforcement.

## 4A. Helm-Related Scanning

Helm is part of Trivy's IaC coverage.

According to the official Helm coverage docs:

- Trivy supports scanning Helm templates and packaged charts
- template scanning supports misconfiguration and secret scanning
- packaged chart scanning supports misconfiguration scanning

Practical idea:

- Trivy resolves Helm templates into Kubernetes manifests
- then it runs Kubernetes-related checks against the rendered output

This matters because Helm charts can hide risky settings behind values and templates. Scanning only raw YAML is not always enough.

## 5. Kubernetes Security Scanning

Kubernetes scanning helps inspect live cluster resources.

Why it matters:

- a secure image can still be deployed with insecure Kubernetes settings
- runtime environment and workload configuration matter
- cluster-wide visibility is useful for platform and security teams

Useful commands:

- `trivy k8s --report summary`
- `trivy k8s --include-namespaces kube-system --report summary`

The summary mode is helpful when a team wants a high-level view before drilling into details.

## 6. SBOM Generation and SBOM Scanning

SBOM is a major Trivy topic because it helps with supply chain visibility.

Trivy can generate SBOMs from targets such as images and filesystems.

Examples:

- `trivy image --format cyclonedx --output result.cdx nginx:latest`
- `trivy image --format spdx-json --output result.spdx.json nginx:latest`
- `trivy fs --format cyclonedx --output result.json /app/myproject`

Important detail from the official docs:

- `--format cyclonedx` generates an SBOM and does not include vulnerability scanning by default
- if you want vulnerabilities in that flow, you must explicitly select the relevant scanner behavior

Trivy can also scan existing SBOM files:

- `trivy sbom ./sbom.spdx`
- `trivy sbom ./sbom.cdx.json`

This is useful for:

- supply chain audits
- vulnerability review from exported inventories
- compliance and artifact exchange workflows

## 7. Cloud Scanning

Trivy also supports cloud-oriented scanning. A common example is AWS account scanning for misconfigurations.

Examples:

- `trivy aws --region us-east-1`
- `trivy aws --service s3`
- `trivy aws --service s3 --service ec2`
- `trivy aws --service s3 --arn arn:aws:s3:::example-bucket`

Why this matters:

- teams often want to scan live cloud resources in addition to IaC files
- configuration drift can happen after deployment
- cloud misconfiguration scanning complements image and IaC scanning

Important note:

- the AWS scanning feature is marked experimental in official Trivy documentation

## 8. VM Scanning

Trivy also supports selected VM-oriented scanning use cases.

Examples:

- `trivy vm ami:ami-0123456789abcdefg`
- `trivy vm ebs:snap-0123456789abcdefg`

This is useful when the organization still has workloads outside pure container platforms and wants similar vulnerability visibility.

## 9. Built-In Checks and Custom Checks

For misconfiguration scanning, Trivy uses built-in checks and also supports user-defined custom checks.

Built-in check behavior:

- many checks are written in Rego and Go
- checks are distributed through the `trivy-checks` bundle
- Trivy updates those checks and caches them locally
- if fresh checks cannot be downloaded, Trivy can fall back to embedded checks

Custom check behavior:

- organizations can write custom policies in Rego
- custom checks can be loaded with `--config-check`
- package prefixes can be selected with `--namespaces`
- additional data can be passed for policy evaluation

Examples:

- `trivy config --config-check /path/to/policy.rego --namespaces user ./iac`
- `trivy config --config-check ./my-check --data ./data --namespaces user ./configs`

This is important because Trivy can move from a generic scanner to an organization-specific policy engine.

## Practical Scanning Patterns

## 1. Scan an Image Before Push or Deploy

A common DevSecOps pattern is:

1. build the image
2. run `trivy image`
3. fail the pipeline if the result exceeds the accepted threshold
4. push or deploy only if the scan passes

This catches inherited vulnerabilities from base images and installed packages before production deployment.

## 2. Scan the Project Folder Early

Using `trivy fs .` early in development helps catch:

- dependency vulnerabilities
- secrets in local files
- some project-level risks before the image is built

This supports shift-left security because the scan can happen before containerization.

## 3. Scan IaC Before Infrastructure Apply

Using `trivy config .` is valuable before:

- `terraform apply`
- Kubernetes deployment
- Helm-based rollout
- container build from Dockerfiles

This catches configuration issues earlier than runtime validation.

## 4. Gate CI/CD with Exit Codes

In pipelines, teams often use a command pattern like:

- `trivy image --severity HIGH,CRITICAL --ignore-unfixed --exit-code 1 myimage:latest`

The idea is:

- only fail for urgent findings
- skip unfixed noise if the team chooses that policy
- block release automatically when the rule is violated

## How to Read Trivy Output

A Trivy report usually includes:

- target name
- total findings by severity
- affected package or component
- vulnerability identifier such as CVE or advisory ID
- installed version
- fixed version if available
- short title or description

A good reading order is:

1. total critical and high findings
2. whether a fixed version exists
3. whether the issue is in the base image, app dependency, or config
4. whether the finding should block the pipeline immediately

This keeps triage focused and operational.

## Common Practical Filters

These are common combinations teams actually use:

- `trivy image --severity HIGH,CRITICAL myimage:latest`
- `trivy image --severity HIGH,CRITICAL --ignore-unfixed myimage:latest`
- `trivy image --severity HIGH,CRITICAL --ignore-unfixed --exit-code 1 myimage:latest`
- `trivy fs --scanners vuln,secret,misconfig .`
- `trivy config --misconfig-scanners=terraform,dockerfile .`

These patterns matter because most production teams do not want every possible finding to fail the pipeline. They usually tune Trivy to match policy.

## Compliance and Reporting Use

Trivy is also used for reporting and compliance-oriented workflows, not only quick terminal scans.

Reasons:

- output can be exported as JSON, SARIF, CycloneDX, SPDX, and table formats
- findings can be stored as artifacts
- SBOM and scan outputs support audit-style reviews
- compliance reports can be generated for some target types

This makes Trivy useful for both engineer-focused triage and governance-focused reporting.

## Trivy in CI/CD

Trivy works well in CI/CD because:

- it is a single CLI
- it supports machine-readable output
- it has exit-code-based enforcement
- it can run against images, repos, filesystems, and config files
- it can reuse cached databases for speed

Typical placement in a pipeline:

1. checkout code
2. optional `trivy fs .`
3. build the image
4. run `trivy image`
5. optional `trivy config .`
6. fail or continue based on severity policy

This is why Trivy is often one of the easiest DevSecOps tools to adopt.

Examples of CI/CD-friendly commands:

- `trivy image --severity HIGH,CRITICAL --ignore-unfixed --exit-code 1 myimage:latest`
- `trivy image --format sarif --output trivy.sarif myimage:latest`
- `trivy image --format json --output trivy.json myimage:latest`

Practical CI/CD ideas:

- fail only on `HIGH` and `CRITICAL`
- store JSON or SARIF results as build artifacts
- use Trivy before pushing images to a registry
- run `trivy config .` before `terraform apply` or Kubernetes deployment

Trivy also has official or community integrations documented for platforms such as:

- GitHub Actions
- Azure DevOps
- CircleCI
- GitLab-related workflows

## Important Trivy Concepts

### Target vs Scanner

This is one of the most important concepts in Trivy.

- target means what you are scanning, such as image, filesystem, repo, config, or cluster
- scanner means what kind of issue you are looking for, such as vulnerabilities, secrets, misconfigurations, or licenses

Understanding this distinction makes Trivy much easier to use.

### Database and Cache

Trivy relies on vulnerability and policy data. To avoid repeated downloads, it caches that information locally.

This means:

- first scans can be slower because data must be fetched
- later scans are faster because the cache is warm
- offline and air-gapped setups often need deliberate database preloading

The official docs also support:

- self-hosting Trivy databases
- choosing repositories for database retrieval
- warming caches before scan-heavy CI jobs

### Severity Does Not Equal Exploitability

A critical severity finding is important, but teams still need context:

- is the vulnerable package actually reachable
- is the package part of the final runtime path
- is a fix available
- is the issue in a dev-only dependency or production path

Trivy reports the finding, but remediation decisions still need engineering judgment.

## Limitations

Trivy is powerful, but it is not a complete security program by itself.

Important limitations:

- it detects known issues, not unknown zero-days
- vulnerability data freshness affects results
- some findings need manual triage
- secret scanning can produce false positives
- it does not replace runtime protection or deep manual review

It is best understood as a fast and practical preventive control.

## Practical Mental Model

If you want one simple way to remember Trivy, use this:

- choose the target
- choose the scanners
- filter the severity
- decide whether the result should only report or actually fail the pipeline

That is the core Trivy operating model.

## Trivy in One View

Trivy is a single security scanner that can inspect multiple artifact types and multiple classes of security issues. Internally, it detects packages, configs, and secrets, then compares them against vulnerability databases and policy checks. Externally, it fits into developer machines, CI/CD pipelines, registries, and Kubernetes workflows as a fast security checkpoint before release or deployment.
