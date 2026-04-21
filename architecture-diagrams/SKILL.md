---
name: architecture-diagrams
description: Create architecture diagrams when the user asks for system topology, technical architecture, deployment layout, physical architecture, node relationships, network zones, traffic paths, or environment structure. This skill is specifically for requests that should produce both a physical architecture diagram and a deployment architecture diagram in the same response, unless the user explicitly asks for only one.
---

# Architecture Diagrams

## Overview

Use this skill when the user wants architecture diagrams rather than prose-only explanation. The default deliverable is a pair of diagrams: one physical architecture diagram and one deployment architecture diagram.

## Output Contract

Unless the user explicitly opts out, always provide both:

- A `Physical Architecture Diagram`
- A `Deployment Architecture Diagram`

Each diagram should be self-contained, readable, and consistent in naming. If the source material is incomplete, make the smallest reasonable assumptions, label them clearly, and keep the diagrams internally consistent.

## Recommended Format

- Default to Mermaid for text-based diagram output
- Use `flowchart LR` unless the structure is unusually tall
- Quote node labels when they contain spaces or punctuation
- Keep node labels short enough to stay readable
- Group by zone, host, cluster, environment, or network boundary when useful
- Show traffic direction and major dependencies explicitly

If the user asks for an image file, generate the image after drafting the Mermaid structure first. Before finalizing, check that labels fit inside nodes, wrap naturally, and do not overlap.

## Image Output Rules

When the task requires an image file, follow these defaults unless the user explicitly overrides them:

- Prefer `PNG`
- Save images under `/Users/edy/Downloads/AI/images`
- Create the output directory before saving if it does not exist
- Use a semantic English filename, adding a date or timestamp when needed to avoid overwriting
- Always return the absolute image path in the response
- Do not include source citations or reference notes inside the image

For diagrams with boxes and text:

- Ensure all text stays inside its box
- Wrap text by default
- Avoid overlap, clipping, crowding, line collisions, or text extending beyond the canvas

Before delivering any laid-out image, perform a self-check. If text is too dense, overlapping, out of bounds, or hard to read, adjust font size, line height, card height, spacing, or canvas size first and only then finalize the image.

## Diagram Roles

### Physical Architecture Diagram

Use this to show what the system is made of and where it lives.

Include the most relevant physical or infrastructure-oriented elements such as:

- Users, clients, or edge entry points
- CDN, WAF, load balancer, gateway, or ingress
- VPC, subnet, AZ, IDC, office, rack, host, VM, or bare metal grouping
- Kubernetes clusters, nodes, or server groups
- Databases, caches, queues, object storage, and third-party dependencies
- Key network links and security boundaries

Focus on topology and placement. Do not overload this diagram with rollout strategy details.

### Deployment Architecture Diagram

Use this to show how software is deployed and promoted.

Include the most relevant deployment-oriented elements such as:

- Environments like dev, test, staging, prod
- Regions, clusters, namespaces, node pools, or hosts
- Deployable units such as services, pods, containers, jobs, or sidecars
- Deployment controllers, CI/CD path, image registry, config or secret sources
- Service-to-service calls that matter at runtime
- High availability or scaling shape when it changes deployment behavior

Focus on runtime placement and release structure. Do not duplicate every physical detail unless it matters to deployment understanding.

## Workflow

### 1. Extract the architecture nouns

Identify:

- Entry points
- Core services
- Data stores
- Infrastructure boundaries
- Environments
- Deployment targets
- External systems

Normalize names before drawing. Use one canonical name per component.

### 2. Separate physical concerns from deployment concerns

Ask of each item:

- Is this about where the system lives or what network boundary it crosses
- Or is this about how software units are packaged, deployed, scaled, or promoted

Put shared concepts in both diagrams only when they help orientation.

### 3. Reduce clutter

- Merge repeated nodes when they are identical at the chosen level of abstraction
- Omit incidental implementation details
- Prefer one clear edge over many redundant edges
- Keep each diagram to the smallest faithful slice of the system

### 4. Annotate assumptions

If information is missing, add a short `Assumptions` list after the diagrams. Keep it short and concrete.

## Quality Bar

Before finalizing, check:

- Both diagrams are present
- Names are consistent between diagrams
- Arrows have clear direction
- Network or environment boundaries are visible where relevant
- Important data stores and external dependencies are not floating without context
- The deployment diagram shows deployable units, not just boxes copied from the physical view
- The physical diagram shows topology, not just a service list

## Prompt Shapes

- `Use $architecture-diagrams to draw the current system. Output both a physical architecture diagram and a deployment architecture diagram.`
- `Use $architecture-diagrams based on this service list and deployment notes.`
- `Use $architecture-diagrams to turn this README into physical and deployment architecture diagrams.`

## Resources

- Read [references/diagram-rules.md](references/diagram-rules.md) when the system is large, ambiguous, or needs clearer abstraction boundaries
