# Helm: Detailed Study Notes

## What Helm Is

Helm is a package manager for Kubernetes. It helps teams define, install, upgrade, and manage Kubernetes applications using reusable packages called charts.

A simple way to think about Helm is:

- Kubernetes gives you the raw objects such as Deployments, Services, ConfigMaps, and Ingress resources.
- Helm helps you package those objects together in a reusable and configurable form.

Without Helm, teams often manage many YAML files manually. With Helm, they can use one chart template and supply different values for development, staging, and production.

## Why Helm Matters

Helm is useful because Kubernetes applications usually involve many related resources:

- Deployments
- Services
- Ingress rules
- ConfigMaps
- Secrets
- autoscaling settings
- persistent storage definitions

Managing these resources manually becomes difficult when:

- the same application is deployed to multiple environments
- image tags and replicas change frequently
- different teams need consistent deployment standards
- upgrades and rollbacks must be tracked

Helm solves this by turning Kubernetes resource definitions into parameterized packages.

## Core Concepts

Before understanding the working mechanism, it helps to know the main building blocks:

- Chart: the package that contains Kubernetes templates, default values, and metadata
- Release: a deployed instance of a chart in a cluster
- Values: configuration inputs used to customize templates
- Template: a YAML file with placeholders and logic
- Repository: a place where packaged charts are stored and shared

One chart can create many releases. For example, the same chart may be installed as:

- `myapp-dev`
- `myapp-stage`
- `myapp-prod`

Each release can use different values even though the chart itself is the same.

## Typical Chart Structure

A Helm chart usually contains files such as:

- `Chart.yaml` for metadata
- `values.yaml` for default configuration
- `templates/` for Kubernetes manifest templates
- `charts/` for dependent subcharts
- `templates/_helpers.tpl` for reusable template helpers
- `templates/tests/` for chart tests in many charts created from scaffolding
- `crds/` for custom resource definitions when needed

This directory structure is part of Helm's internal working model. Helm expects chart content in a predictable layout so it can load metadata, merge values, and render templates correctly.

## High-Level Workflow

At a high level, Helm works like this:

1. A user runs a Helm command such as install, upgrade, template, or rollback.
2. Helm loads the chart and reads default values.
3. Helm merges additional values from files, command-line overrides, or environment-specific input.
4. Helm renders templates into plain Kubernetes YAML manifests.
5. Helm sends those manifests to the Kubernetes API server, or prints them if running in template mode.
6. Kubernetes creates or updates resources in the cluster.
7. Helm stores release information so future upgrades or rollbacks are possible.

This high-level flow is the bridge between the internal and external working mechanism.

## Internal Working Mechanism

## 1. Chart Loading and Validation

Internally, Helm begins by loading chart metadata and validating the chart structure. It reads files such as:

- chart name and version
- application version
- chart dependencies
- default values
- template files

If required files are missing or malformed, Helm stops before rendering anything. This validation step is important because Helm needs a well-formed package before it can safely generate Kubernetes manifests.

## 2. Values Loading and Merge Logic

One of Helm's most important internal mechanisms is values merging. Helm combines configuration from multiple sources:

- defaults in `values.yaml`
- extra values files such as `values-dev.yaml` or `values-prod.yaml`
- command-line overrides such as `--set`

The merge result becomes the final values object used during template rendering.

This is a powerful design because it allows:

- one reusable chart
- many environment-specific deployments
- controlled overrides without copying entire YAML sets

Internally, Helm resolves precedence so that the most specific value wins. That means a command-line override can replace a default defined in the chart.

## 3. Template Rendering Engine

The template rendering engine is the core of Helm's internal behavior. Templates inside the `templates/` directory are not plain YAML. They contain placeholders and logic expressions.

Helm processes templates by:

- loading the template files
- injecting the merged values and chart metadata
- applying helper functions and template expressions
- producing final YAML manifests

This means Helm is not deploying templates directly. It first transforms them into normal Kubernetes resource definitions.

Template rendering commonly controls:

- image names and tags
- replica counts
- resource limits and requests
- labels and annotations
- environment variables
- conditional resources such as optional Ingress or autoscaling objects

This internal rendering step is why Helm is more flexible than static YAML files.

## 4. Helper Templates and Reusability

Helm supports reusable helper logic, often stored in `_helpers.tpl`. Internally, helpers reduce duplication by centralizing repeated template fragments such as:

- naming conventions
- label blocks
- selector labels
- common annotations

This matters because Kubernetes objects often share repeated metadata. Instead of copying the same label logic across many files, Helm can render it from one helper template.

## 5. Dependency Resolution

Charts can depend on other charts. Internally, Helm can load and package subcharts so a parent chart can deploy a larger application stack.

Examples:

- an application chart may depend on a database chart
- a platform chart may include ingress or monitoring components

Dependency handling allows chart composition. That means teams can build higher-level deployment packages from smaller reusable units.

## 6. Manifest Generation

After values are merged and templates are processed, Helm generates plain Kubernetes manifests. At this point, the internal transformation step is complete.

These generated manifests are what Kubernetes will actually receive. Helm therefore acts as a compiler from chart templates to raw YAML resources.

A useful mental model is:

- chart plus values go in
- Kubernetes manifests come out

This is one of the most important things to understand about Helm.

## 7. Release State Management

Helm does more than just render YAML. It also tracks release state. Internally, Helm stores information about:

- release name
- chart version
- values used
- rendered manifests
- revision history

This release tracking is what makes commands such as upgrade, history, and rollback possible. Without stored release metadata, Helm would not know what changed between one deployment and the next.

## 8. Upgrade and Rollback Logic

When a user runs `helm upgrade`, Helm repeats the render process using the new chart or values, compares it operationally through the Kubernetes apply path, and records a new release revision.

When a user runs `helm rollback`, Helm uses stored revision data to restore a previous release state.

This internal revision model gives Helm an important operational advantage:

- deployments are versioned
- changes are traceable
- rollback is structured rather than manual

## External Working Mechanism

## 1. Interaction with Kubernetes

Externally, Helm works by communicating with the Kubernetes API server using the current cluster context and credentials.

From the outside, the process looks like this:

- the user points Helm to a cluster
- Helm renders manifests
- Helm submits those manifests to Kubernetes
- Kubernetes schedules pods and creates the actual runtime resources

This means Helm is not a replacement for Kubernetes. It is a management layer that prepares and sends Kubernetes resources.

## 2. Developer Workflow

Developers often use Helm in a repeatable workflow such as:

1. write or modify a chart
2. update values for an environment
3. render locally using `helm template`
4. validate with `helm lint`
5. install or upgrade in a cluster

This external workflow is important because Helm helps teams shift from manually editing YAML to maintaining reusable deployment packages.

## 3. CI/CD Integration

Helm fits naturally into CI/CD pipelines. Common uses include:

- packaging charts during build
- deploying applications after image creation
- upgrading releases in staging or production
- validating templates before merge

A pipeline may do something like:

1. build the application image
2. push the image to a registry
3. update the image tag in Helm values
4. run `helm upgrade --install`
5. verify rollout status

This makes Helm a deployment automation tool as much as a packaging tool.

## 4. Chart Repositories and Distribution

Externally, charts are often shared through repositories. A chart repository lets teams:

- publish versioned charts
- pull charts from a central source
- reuse vendor or internal platform charts

This is similar to how package managers share software packages. Helm uses repositories so teams do not need to copy chart directories manually between projects.

## 5. Environment Management

One of Helm's biggest external benefits is environment customization. The same chart can be reused across:

- local development
- testing
- staging
- production

Only the values change. This external operating model helps teams keep deployment structure consistent while still adapting to different replica counts, domains, secrets, resource sizes, or image versions.

## 6. Operations and Day-2 Management

Externally, Helm helps with day-2 operations after the first deployment:

- checking release history
- upgrading versions
- rolling back failed releases
- inspecting rendered values and manifests

This operational lifecycle is why Helm is widely used in real Kubernetes environments. It is not only for initial installation. It also helps manage change over time.

## 7. Relationship with GitOps Tools

Helm is often used together with GitOps tools such as Argo CD or Flux. In that setup:

- Helm provides chart packaging and templating
- the GitOps tool watches Git and applies the desired release state

This is an important external mechanism because Helm can either be:

- run directly by a user or CI pipeline
- used indirectly by a GitOps controller

In both cases, Helm remains the chart rendering and release-definition layer.

## Common Commands and What They Mean

Some important Helm commands are:

- `helm create` to scaffold a new chart
- `helm lint` to validate chart structure and template quality
- `helm template` to render manifests locally without deploying
- `helm install` to create a release
- `helm upgrade` to update a release
- `helm upgrade --install` to create or update depending on whether the release exists
- `helm rollback` to restore an earlier release revision
- `helm uninstall` to remove a release
- `helm list` to show deployed releases
- `helm history` to show release revisions
- `helm repo add`, `helm repo update`, and `helm search repo` to work with chart repositories
- `helm test` to run chart-defined validation tests

These commands matter because most day-to-day Helm usage is operational rather than theoretical.

## Helm Commands and Their Use

Below is a more practical command reference that explains not only what a command is, but when and why teams use it.

Before using some of the examples below, it helps to keep one pattern in mind:

- release name is the deployed Helm release, such as `hello-world-chart`
- chart path can be `.` when you are standing inside the chart directory
- namespace is the Kubernetes namespace where the release exists
- values file provides environment-specific overrides such as image tag, replicas, ingress host, or resource limits

### 1. `helm create`

Use:

- creates a starter chart directory with default files and templates
- best when you want a quick chart scaffold instead of writing every file manually

Example:

- `helm create myapp`

When teams use it:

- starting a new application deployment chart
- learning the standard Helm chart structure

### 2. `helm lint`

Use:

- checks chart structure and template quality
- catches obvious problems before deployment

Example:

- `helm lint ./myapp`

When teams use it:

- before committing a chart
- in CI to reject broken templates early

### 3. `helm template`

Use:

- renders chart templates locally without sending anything to Kubernetes
- helps inspect the final YAML after values are merged

Example:

- `helm template myapp ./myapp`
- `helm template myapp ./myapp -f values-prod.yaml`

When teams use it:

- debugging templates
- checking the exact Deployment, Service, or Ingress YAML Helm will generate

### 4. `helm install`

Use:

- installs a chart as a new release in the cluster
- creates Kubernetes resources for the first time

Example:

- `helm install myapp ./myapp`
- `helm install myapp ./myapp -n dev --create-namespace`

When teams use it:

- first deployment of an application
- environment setup for dev, test, or production

### 5. `helm upgrade`

Use:

- updates an existing release with a changed chart or new values
- applies configuration, image, or replica changes

Example:

- `helm upgrade myapp ./myapp`
- `helm upgrade myapp ./myapp -f values-prod.yaml`

When teams use it:

- rolling out a new image tag
- changing environment settings
- updating resource limits, ports, or scaling values

### 6. `helm upgrade --install`

Use:

- installs the release if it does not exist
- upgrades it if it already exists

Example:

- `helm upgrade --install myapp ./myapp -n prod`

When teams use it:

- CI/CD automation where the pipeline should work for both first-time deploy and update
- reducing conditional deployment logic in scripts

### 7. `helm uninstall`

Use:

- removes a release and the resources managed by that release

Example:

- `helm uninstall myapp`
- `helm uninstall myapp -n dev`

When teams use it:

- cleaning up test environments
- removing applications no longer needed in a cluster

### 8. `helm list`

Use:

- shows releases currently known in a namespace or cluster scope

Example:

- `helm list`
- `helm list -n prod`

When teams use it:

- checking whether a release exists
- seeing deployed release names and revisions

### 9. `helm history`

Use:

- shows release revision history
- helps track changes over time

Example:

- `helm history myapp`

When teams use it:

- before rollback
- while investigating failed or risky upgrades

### 10. `helm rollback`

Use:

- restores a previous release revision
- useful when a new deployment is unhealthy or misconfigured

Example:

- `helm rollback myapp 2`

When teams use it:

- after a failed upgrade
- when a new image or values file caused production issues

### 11. `helm get values`

Use:

- shows the values used by a release
- helps compare expected configuration with what is actually deployed

Example:

- `helm get values myapp`
- `helm get values myapp -n prod`

When teams use it:

- debugging configuration drift
- confirming which overrides were applied to a release

### 12. `helm get manifest`

Use:

- shows the rendered manifests stored for a release
- helps inspect what Helm actually deployed

Example:

- `helm get manifest myapp`

When teams use it:

- troubleshooting a live release
- comparing deployed resources with chart templates

### 13. `helm repo add`

Use:

- adds a chart repository to the local Helm client

Example:

- `helm repo add bitnami https://charts.bitnami.com/bitnami`

When teams use it:

- preparing to install charts published by vendors or internal platform teams

### 14. `helm repo update`

Use:

- refreshes repository metadata so Helm knows the latest available chart versions

Example:

- `helm repo update`

When teams use it:

- before searching or installing from repositories
- after adding a new repository

### 15. `helm search repo`

Use:

- searches charts available in configured repositories

Example:

- `helm search repo nginx`

When teams use it:

- discovering reusable charts
- checking exact chart names before installation

### 16. `helm pull`

Use:

- downloads a chart package locally without installing it

Example:

- `helm pull bitnami/nginx`

When teams use it:

- inspecting a chart offline
- packaging or reviewing vendor charts before deployment

### 17. `helm dependency update`

Use:

- downloads or refreshes subchart dependencies defined in `Chart.yaml`

Example:

- `helm dependency update ./myapp`

When teams use it:

- after declaring chart dependencies
- before packaging or installing a parent chart

### 18. `helm package`

Use:

- bundles a chart directory into a versioned archive

Example:

- `helm package ./myapp`

When teams use it:

- publishing charts to a repository
- versioning internal charts for reuse

### 19. `helm test`

Use:

- runs chart-defined tests after installation
- verifies that the release behaves as expected

Example:

- `helm test myapp`

When teams use it:

- after install or upgrade
- validating connectivity, startup, or service response

### 20. `helm show values`

Use:

- prints the default values of a chart
- helps understand what can be overridden before installation

Example:

- `helm show values bitnami/nginx`

When teams use it:

- reviewing third-party charts
- preparing custom values files for a new deployment

## Practical Command Notes and Examples

This section adds hands-on commands in the same style teams use during day-to-day Helm work.

## 1. Create a Helm Chart

Command:

```bash
helm create helmchartname
```

Use:

- creates a new chart folder with the standard Helm structure
- useful as the first step when building a custom chart

What gets created:

- `Chart.yaml`
- `values.yaml`
- `templates/`
- helper files and a starter test template

## 2. Understanding a Typical Upgrade Command

Example:

```bash
helm upgrade helloword-chart . -n hello-world-helm -f values.yaml
```

Meaning of each part:

| Part | Meaning |
|---|---|
| `helm upgrade` | Updates an existing Helm release |
| `helloword-chart` | Release name already installed |
| `.` | Current directory containing the Helm chart |
| `-n hello-world-helm` | Namespace where the release exists |
| `-f values.yaml` | Use values from this file |

This command is one of the most common real-world Helm operations. Teams edit `values.yaml`, then run `helm upgrade` to apply the new configuration.

## 3. Preview Changes with Helm Diff

Important note:

- `helm diff` is not part of core Helm
- it comes from the `helm-diff` plugin

Plugin install example:

```bash
helm plugin install https://github.com/databus23/helm-diff
```

The plugin's current docs say Helm 4 users may need:

```bash
helm plugin install https://github.com/databus23/helm-diff --verify=false
```

Preview what would change:

```bash
helm diff upgrade helloword-chart . -n hello-world-helm -f values.yaml --color
```

Use:

- shows the difference between what is currently deployed and what would be deployed
- helps review changes before running the real upgrade

If the release does not exist yet or was not previously installed in the normal way, use:

```bash
helm diff upgrade helloword-chart . \
  -n hello-world-helm \
  -f values.yaml \
  --allow-unreleased
```

Use:

- allows diffing even when the release is not yet present
- helpful when switching charts or checking first-time deployment behavior

## 4. Apply Updated Values

Command:

```bash
helm upgrade helloword-chart . -n hello-world-helm -f values.yaml
```

Use:

- applies the changes from the chart and values file to the existing release
- common after changing image tags, resources, replica counts, or ingress settings

## 5. Roll Back to a Previous Revision

Command:

```bash
helm rollback helloword-chart 1 -n hello-world-helm
```

Use:

- restores the release to revision `1`
- helpful when a recent upgrade introduced a failure

Before rollback, teams usually check history:

```bash
helm history helloword-chart -n hello-world-helm
```

## 6. Compare Two Revisions

Command:

```bash
helm diff revision helloword-chart 3 4 -n hello-world-helm
```

Use:

- compares revision `3` and revision `4`
- useful when investigating exactly what changed between releases

## 7. Safe Preview with `--dry-run`

Command:

```bash
helm upgrade helloword-chart . -n hello-world-helm -f values.yaml --dry-run
```

Use:

- simulates the upgrade
- does not apply anything to Kubernetes

This is one of the safest ways to preview Helm behavior before making a real cluster change.

## 8. Deeper Debugging with `--debug`

Command:

```bash
helm upgrade helloword-chart . -n hello-world-helm -f values.yaml --debug
```

Use:

- prints extra debug information
- helps when the chart renders unexpectedly or the upgrade fails

## 9. Most Common Preview Pattern: `--dry-run --debug`

Command:

```bash
helm upgrade helloword-chart . -n hello-world-helm -f values.yaml --dry-run --debug
```

Use:

- simulates the change
- prints detailed internal information
- often the best first troubleshooting command for Helm upgrades

In this output, two value views are especially important:

1. `USER-SUPPLIED VALUES`
   These are the values you directly provided to Helm.
2. `COMPUTED VALUES`
   These are the final merged values Helm actually uses after combining chart defaults and overrides.

This distinction is important because many Helm issues come from misunderstanding which values won after merging.

## 10. Generate All YAML Manifests

Command:

```bash
helm template helloword .
```

Use:

- renders all Kubernetes YAML locally
- lets you inspect the final Deployment, Service, ConfigMap, Ingress, and other objects without applying them

This is especially useful for debugging templates and confirming that variables resolve correctly.

## 11. Check Chart Errors with Lint

Command:

```bash
helm lint .
```

Use:

- checks the chart for obvious structural or template problems
- should usually be run before install or upgrade

## 12. Uninstall the Helm Release

Command:

```bash
helm uninstall helloword-chart -n hello-world-helm
```

Use:

- removes the release and the Kubernetes resources managed by it
- useful for cleanup or removing an application from an environment

## 13. Add a Helm Repository

Command:

```bash
helm repo add bitnami https://charts.bitnami.com/bitnami
```

Use:

- adds the Bitnami repository to your local Helm client
- allows you to search and install charts from that repository

## 14. Check Configured Repositories

Command:

```bash
helm repo list
```

Use:

- shows all repositories currently added to the local Helm client

## 15. Update All Helm Repositories

Command:

```bash
helm repo update
```

Use:

- refreshes metadata for all added repositories
- should be run before searching or installing if you want recent chart information

## 16. Update a Specific Repository

Command:

```bash
helm repo update acko
```

Use:

- refreshes only the `acko` repository
- convenient when you want a faster targeted update

## 17. Search Charts in Added Repositories

Command:

```bash
helm search repo acko
```

Use:

- searches only the repositories already added to your local Helm configuration

## 18. Search Charts in the Global Hub

Command:

```bash
helm search hub nginx
```

Use:

- searches public charts through Artifact Hub or a compatible hub endpoint
- useful when you have not added a repository locally yet

Comparison:

| Command | Scope |
|---|---|
| `helm search repo` | Searches locally added repositories |
| `helm search hub` | Searches public/global chart listings |

## 19. Remove a Repository

Command:

```bash
helm repo remove bitnami
```

Use:

- removes the repository from the local Helm client configuration

## 20. Install a Chart Using a Values File

Command:

```bash
helm install my-nginx bitnami/nginx -f values.yaml
```

Use:

- installs the `bitnami/nginx` chart
- applies custom values from `values.yaml`

This is a very common pattern when deploying vendor charts because teams rarely use the default values exactly as they come.

## Debugging and Safe Preview

One practical lesson is that Helm should be debugged before it touches the cluster whenever possible.

Important commands for this are:

- `helm lint` to catch obvious chart problems
- `helm template` to inspect rendered YAML locally
- `helm install --dry-run --debug` or `helm upgrade --dry-run --debug` to preview what Helm is about to do

These commands are important externally because they reduce failed deployments. Internally, they let you inspect the result of values merging and template rendering before the Kubernetes API sees anything.

## Practical Chart Creation Flow

A common application workflow is to containerize an application and then deploy it with Helm. That practical flow is valuable because it shows Helm in context rather than isolation.

The real-world sequence is:

1. create or package the application
2. build and push the container image
3. scaffold a Helm chart
4. connect values such as image name, tag, port, and service settings
5. install the chart
6. verify the release after deployment

This teaches an important point:

- Helm usually sits after application build and image creation
- Helm is the packaging and deployment layer for the Kubernetes side of the workflow

## Helmfile in the Helm Ecosystem

It is also useful to keep the boundary clear between Helm and Helmfile:

- Helm is the chart and release manager
- Helmfile is an additional wrapper used to manage multiple Helm releases declaratively

Why teams use Helmfile:

- to manage several Helm releases in one place
- to separate environments more cleanly
- to keep large Kubernetes application stacks organized
- to coordinate multi-chart deployments with one declarative file

So Helmfile is not part of Helm's internal mechanism, but it is part of the external ecosystem many teams use around Helm.

## Chart Repositories in Practice

Chart repositories are important because charts need distribution as well as creation.

From a practical point of view:

- a chart repository stores packaged charts and an `index.yaml`
- teams add repositories with commands such as `helm repo add`
- they refresh repository metadata with `helm repo update`
- they search charts using repository-aware commands

This matters externally because chart repositories are how teams share and reuse deployment packages across projects and environments.

Today, teams may also use OCI registries for chart distribution, but the repository model remains an important Helm concept.

## Hooks and Tests

Hooks and tests are important advanced topics.

### Hooks

Hooks let chart developers run resources at specific points in the release lifecycle. Common examples include:

- pre-install logic
- post-install logic
- pre-upgrade backup jobs
- post-upgrade verification jobs
- pre-delete cleanup work

Hooks are implemented using annotations such as `helm.sh/hook` in resource metadata. They are useful when normal templated resources are not enough and the release needs lifecycle-aware actions.

### Tests

Helm tests are chart-defined validation resources, often Jobs or Pods, that run after installation. They help answer questions such as:

- did the service start correctly
- can the app be reached on the expected port
- were values injected correctly

The practical command is:

- `helm test <release-name>`

This matters because successful installation does not always mean the deployed application is healthy. Helm tests provide a lightweight verification layer after the release is created.

These commands expose the external surface of Helm, while the templating and release tracking happen internally.

## Typical End-to-End Example

A practical Helm workflow might look like this:

1. A team creates a chart for a web application.
2. The chart contains templates for Deployment, Service, ConfigMap, and Ingress.
3. `values.yaml` defines a default image, replica count, and service port.
4. The production team provides a separate values file with higher replicas and a production domain.
5. Helm merges the values and renders the final manifests.
6. Helm sends them to the Kubernetes API server.
7. Kubernetes creates or updates the resources.
8. Helm records the release revision so the team can upgrade or roll back later.

This example shows the two layers clearly:

- internal layer: merge values, render templates, track release
- external layer: talk to Kubernetes, support operations, fit into CI/CD

## Strengths

- simplifies Kubernetes application packaging
- reduces repeated YAML across environments
- supports reusable templates and helper functions
- provides structured upgrade and rollback flow
- works well in CI/CD and GitOps environments

## Limitations

- complex templates can become hard to read and debug
- bad values design can make charts difficult to maintain
- Helm does not remove the need to understand Kubernetes itself
- runtime failures can still happen even if the chart renders successfully

A useful mental model is:

- Helm helps manage Kubernetes resources
- Helm does not replace Kubernetes behavior, scheduling, or cluster security

## Internal vs External Working Mechanism in One View

Internally, Helm loads chart metadata, merges values, renders templates, resolves dependencies, and stores release state. Externally, it interacts with Kubernetes clusters, chart repositories, CI/CD systems, and GitOps workflows so applications can be deployed and managed consistently across environments.

In short:

- internal mechanism explains how Helm transforms charts into manifests and tracks releases
- external mechanism explains how Helm is used by developers, pipelines, and clusters in real operations

That is the key architectural idea behind Helm. Inside, it is a templating and release-management engine. Outside, it is a practical deployment tool for Kubernetes platforms.
