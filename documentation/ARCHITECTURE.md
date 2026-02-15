# Architecture

Last Updated: 2026-02-15

## Overview

{Описание архитектуры проекта}

## Layers

```
{Handlers/Pages} → {Services/API} → {Repositories/Models}
```

## Components

| Компонент | Директория | Ответственность |
|-----------|------------|-----------------|
| {Handlers} | `src/handlers/` | {Routing, validation} |
| {Services} | `src/services/` | {Business logic} |
| {Models} | `src/models/` | {Data models} |

## Data Flow

```
{Request} → {Handler} → {Service} → {Repository} → {DB}
                                         ↓
{Response} ← {Handler} ← {Service} ← {Result}
```

## Infrastructure

| Компонент | Технология | Назначение |
|-----------|------------|------------|
| {App} | {Framework} | {Main application} |
| {DB} | {Database} | {Data storage} |
| {Cache} | {Redis/etc} | {Caching/sessions} |

## Environments

See [../_status/](../_status/) for current environment state.
