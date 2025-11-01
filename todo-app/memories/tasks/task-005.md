---
id: task-005
title: Fix memory leak in background worker
date: 2025-11-08
status: blocked
priority: critical
created: 2025-11-01T08:30:00Z
project: web-platform
tags: bug, performance
---

Background worker process consuming excessive memory over time.

Blocked by:
- Waiting for profiling tools access on production
- Need DevOps approval for heap dump

Investigation steps:
- [ ] Reproduce locally
- [ ] Profile memory usage
- [ ] Identify leak source
- [ ] Implement fix
