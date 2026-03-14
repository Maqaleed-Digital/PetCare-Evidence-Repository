# Shared — Backend Service Shared Assets

## Purpose

This directory contains shared configuration, registries, and contracts used by all backend
services in the petcare platform foundation.

## Contents

| File                   | Description                                                        |
|------------------------|--------------------------------------------------------------------|
| `SERVICE_REGISTRY.json` | Canonical list of all platform services with discovery metadata  |

## Usage

All services must:
1. Register themselves in `SERVICE_REGISTRY.json` at scaffold time.
2. Use the registry for peer discovery rather than hard-coding service URLs.
3. Never modify another service's registry entry directly — submit a PR with both the service
   owner and platform-foundation as required reviewers.

## Adding a New Service

Add an entry to `SERVICE_REGISTRY.json` following the existing schema. Required fields:
- `service_id`, `name`, `version`, `base_path`, `health_path`, `owner_team`

## Phase

PH-FND-2 — Backend Service Skeleton
