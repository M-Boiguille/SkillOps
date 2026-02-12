# Phase 5: Performance Profiling & Optimization

**Status**: ✅ Complete
**Priority**: High
**Estimated Effort**: 2-3 sprints (delivered)

## Objective

Optimize SkillOps for production workloads by profiling, measuring, and reducing resource consumption across the tracking pipeline, database operations, and dashboard rendering.

## Implementation Summary

**Modules delivered:**
- `src/lms/performance_profiling.py`
- `src/lms/metrics.py`
- `src/lms/database_optimization.py`
- `src/lms/cache.py`
- `src/lms/tracking_optimization.py`
- `src/lms/performance_monitor.py`

**CLI additions:**
- `skillops perf-profile`

**Tests delivered:** 32 tests across Phase 5 modules

## Rationale

With Phases 1-4 complete, SkillOps has:
- Functional training pipeline (code/train/review)
- Passive tracking infrastructure (git hooks + WakaTime)
- Analytics dashboard with historical data
- Comprehensive test coverage

However, production readiness requires:
- **Memory efficiency**: Long-running tracking processes
- **Query performance**: Dashboard loading with large datasets
- **Disk I/O optimization**: SQLite query patterns
- **Terminal rendering**: Dashboard refresh speed with many rows

## Phase 5 Roadmap

### Sprint 5.1: Profiling Infrastructure

#### Objective
Establish baseline performance metrics and identify bottlenecks.

#### Deliverables

1. **Performance Profiling Module** (`src/lms/performance_profiling.py`)
   - Memory profiler integration (memory_profiler)
   - CPU profiler for function-level hotspots
   - Database query analyzer (SQLite EXPLAIN QUERY PLAN)
   - Terminal rendering timer
   - Report generation in JSON/CSV

2. **Metrics Collection** (`src/lms/metrics.py`)
   - Tracking operation metrics:
     - Time to collect daily tracking data
     - Git hook execution time
     - WakaTime API call latency
   - Database metrics:
     - Query execution times
     - Lock contention
     - Index effectiveness
   - Dashboard metrics:
     - Data retrieval time
     - Rendering time per component
     - Memory footprint

3. **Baseline Report Generation**
   - Current-state performance report
   - Bottleneck identification
   - Recommendations for optimization

#### Test Suite (8 tests)
```python
test_memory_profiler_integration()
test_cpu_profiler_integration()
test_query_explain_plan()
test_metrics_collection_accuracy()
test_profiling_overhead_acceptable()
test_report_generation()
test_csv_export()
test_json_export()
```

#### Dependencies
- memory_profiler
- cProfile (stdlib)
- line_profiler

---

### Sprint 5.2: Database Optimization

#### Objective
Optimize SQLite queries and schema for faster dashboard loads.

#### Deliverables

1. **Query Optimization** (`src/lms/database_optimization.py`)
   - Index review and creation:
     - (date, activity_level) composite index on tracking_summary
     - (date, git_commits) for commit-based queries
     - (date) for time-range queries
   - Query rewriting:
     - Replace N+1 queries with JOINs
     - Aggregate queries using GROUP BY
     - Cursor optimization for large result sets
   - Connection pooling:
     - Reduce connection overhead
     - Reuse connections for dashboard
     - Implement connection timeout management

2. **Schema Analysis**
   - Review current schema for optimization opportunities
   - Denormalization candidates (if applicable)
   - Compression strategies for large datasets
   - Archival strategy for old data

3. **Caching Layer** (`src/lms/cache.py`)
   - In-memory cache for:
     - Daily aggregations (30-min TTL)
     - Weekly summaries (1-hour TTL)
     - Trend calculations (1-hour TTL)
   - Cache invalidation on new tracking data
   - Cache statistics for monitoring

#### Test Suite (10 tests)
```python
test_index_effectiveness()
test_query_rewrite_performance()
test_connection_pooling()
test_cache_hit_rate()
test_cache_invalidation_correctness()
test_large_dataset_performance()
test_concurrent_query_handling()
test_backup_performance()
test_vacuum_operation()
test_query_plan_analysis()
```

#### Performance Targets
- Dashboard load: < 500ms (from tracking_summary)
- Daily aggregation: < 100ms
- Cache hit rate: > 90% for dashboard views
- Query execution: < 50ms per query

---

### Sprint 5.3: Memory & CPU Optimization

#### Objective
Reduce resource consumption for long-running processes.

#### Deliverables

1. **Tracking Pipeline Optimization** (`src/lms/tracking_optimization.py`)
   - Batch commit processing:
     - Process commits in batches instead of individually
     - Reduce database round-trips
     - Memory pooling for commit objects
   - Generator-based data processing:
     - Stream data instead of loading entire dataset
     - Lazy evaluation for recommendations
     - Streaming JSON export
   - WakaTime integration optimization:
     - HTTP connection reuse
     - Response compression
     - Minimal data transfer

2. **Passive Tracking Efficiency** (`src/lms/git_hooks_optimization.py`)
   - Reduce post-commit hook overhead:
     - Async writes (optional, if safe)
     - Batch metric updates
     - Throttling for frequent commits
   - Pre-commit hook optimization:
     - Fast-path for unchanged code
     - Selective file scanning

3. **Dashboard Rendering** (`src/lms/dashboard_optimization.py`)
   - Lazy loading:
     - Load trends only when requested
     - Progressive rendering of tables
   - Virtual scrolling for large datasets
   - Incremental updates (show new data first)
   - Memory-efficient table generation

#### Test Suite (8 tests)
```python
test_batch_processing_speedup()
test_memory_usage_tracking()
test_generator_memory_efficiency()
test_post_commit_hook_overhead()
test_waka_time_optimization()
test_dashboard_rendering_memory()
test_concurrent_tracking_efficiency()
test_memory_leak_detection()
```

#### Performance Targets
- Post-commit hook: < 100ms
- Daily tracking collection: < 1s
- Dashboard rendering: < 200ms
- Memory footprint (idle): < 50MB
- Memory per tracked day: < 5MB

---

### Sprint 5.4: Monitoring & Alerting

#### Objective
Production readiness with performance monitoring.

#### Deliverables

1. **Performance Monitor** (`src/lms/performance_monitor.py`)
   - Real-time metric collection
   - Performance degradation detection
   - Alert thresholds:
     - Dashboard load time > 1s
     - Post-commit hook > 200ms
     - Memory usage > 100MB
     - Database lock contention > 10%

2. **Metrics Export**
   - Prometheus-compatible metrics
   - InfluxDB integration (optional)
   - Local SQLite metrics table
   - CSV export for analysis

3. **Performance Report Generator**
   - Weekly performance summary
   - Trend analysis (improving/degrading)
   - Bottleneck identification
   - Recommendations for further optimization

#### Test Suite (6 tests)
```python
test_metric_collection_continuous()
test_alert_threshold_detection()
test_prometheus_export()
test_metrics_table_creation()
test_report_accuracy()
test_performance_trend_detection()
```

---

## Integration Strategy

### Phase 5 -> Phase 4 (Dashboard)
- Performance metrics displayed in dashboard footer
- Real-time performance indicators
- Cache hit rate badge

### Phase 5 -> Phase 3 (Passive Tracking)
- Hook execution time monitoring
- WakaTime latency tracking
- Batch optimization benefits

### Phase 5 -> Phase 2 (Quiz/Chaos)
- Quiz rendering time optimization
- Chaos template generation efficiency

## Success Criteria

✅ All 32 new tests passing
✅ Performance report generated for baseline
✅ Dashboard load < 500ms
✅ Post-commit hook < 100ms
✅ Idle memory < 50MB
✅ Cache hit rate > 90%
✅ No performance regressions in existing tests

## Estimated Timeline

- **Sprint 5.1 (Profiling)**: 4-5 days
- **Sprint 5.2 (Database)**: 5-6 days
- **Sprint 5.3 (Memory/CPU)**: 4-5 days
- **Sprint 5.4 (Monitoring)**: 3-4 days
- **Total**: ~18-20 days development

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|-----------|
| Over-optimization (premature) | Wasted effort | Focus on identified bottlenecks first |
| Cache invalidation bugs | Data inconsistency | Comprehensive cache tests + monitoring |
| Performance regression | Production issue | Regression tests in CI/CD |
| Database lock contention | Concurrent access issues | Lock timeout monitoring + alerts |

## Files to Create/Modify

```
✨ src/lms/performance_profiling.py (250 lines)
✨ src/lms/metrics.py (150 lines)
✨ src/lms/database_optimization.py (200 lines)
✨ src/lms/cache.py (180 lines)
✨ src/lms/tracking_optimization.py (200 lines)
✨ src/lms/performance_monitor.py (200 lines)
✨ tests/lms/test_performance.py (400 lines)
✨ tests/lms/test_database_optimization.py (350 lines)
✨ tests/lms/test_monitoring.py (250 lines)
🔧 src/lms/dashboard.py (add metrics display)
🔧 src/lms/passive_tracking.py (add hook profiling)
🔧 src/lms/main.py (add perf-report command)
📊 docs/PERFORMANCE_BASELINES.md
📊 docs/OPTIMIZATION_GUIDE.md
```

## Next Phase (Phase 6) Teaser

**Phase 6: Machine Learning Integration & Predictive Analytics**

After Phase 5's performance optimization, Phase 6 will add intelligent features:
- Learning pattern prediction (when to study)
- Difficulty level detection (struggling areas)
- Study schedule recommendations
- Progress velocity forecasting
- Anomaly detection (unusual patterns)

---

## How to Execute Phase 5

```bash
# When ready to start Phase 5:
git checkout -b phase-5-performance

# Run profiling to establish baseline:
skillops perf-profile

# Implement optimizations sprint by sprint
# Commit after each sprint:
git commit -m "Phase 5.1: Profiling Infrastructure"
git commit -m "Phase 5.2: Database Optimization"
git commit -m "Phase 5.3: Memory & CPU Optimization"
git commit -m "Phase 5.4: Monitoring & Alerting"

# Merge when complete:
git checkout main
git merge phase-5-performance
```

---

## Questions for Requirements Refinement

1. **Priority**: Should we optimize for speed, memory, or both equally?
2. **Datasets**: What's the expected dataset size after 6-12 months of tracking?
3. **Deployment**: Single machine or distributed deployment considerations?
4. **Alerting**: Should alerts be sent to external services (Slack, PagerDuty)?
5. **Monitoring**: Real-time dashboard for performance metrics?

---

**Document Version**: 1.0
**Created**: 2024 (Post-Phase 4 Delivery)
**Status**: Ready for Sprint Planning
