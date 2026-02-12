# AI-Powered On-Call Training

SkillOps uses AI to generate personalized debugging incidents with spaced repetition learning (SRS).

## Features

### 🤖 Adaptive AI Generation

Incidents are generated based on:
- **Past performance**: Reviews your resolution history
- **Weak areas**: Focuses on systems you struggle with
- **Skill level**: Adapts difficulty (beginner/intermediate/advanced)
- **Recent chaos events**: Creates incidents related to systems you've tested

### 💡 Progressive Hints System

Get help when stuck with 3 levels of hints:

1. **Socratic Question** (FREE): A guiding question to direct your thinking
2. **Direction Hint** (-1 point): Points you to the right component/log file
3. **Specific Command** (-2 points): Gives you the exact command to run

Each hint costs points, so try to solve without them!

### 📝 Validation Questions

After resolving an incident, the AI asks 2-3 questions to verify:
- You understand the **root cause**
- You know **why your fix works**
- You can explain **how to prevent it**

This prevents copy-paste solutions and ensures real learning.

### 📅 Spaced Repetition System (SRS)

- **Score 0-2**: Review in 1 day (needs practice)
- **Score 3**: Review in 3 days (good understanding)
- **Score 4**: Review in 7 days (solid)
- **Score 5**: Review in 14 days (mastered)

Low-scoring incidents return sooner until you master them.

## Setup

### 1. Get Gemini API Key

```bash
# Get free key from Google AI Studio
# Visit: https://aistudio.google.com/app/apikey

export GEMINI_API_KEY="your-api-key-here"

# Or add to ~/.bashrc
echo 'export GEMINI_API_KEY="your-key"' >> ~/.bashrc
```

### 2. Start On-Call Training

```bash
skillops oncall
```

## Workflow

### New Incident

```bash
$ skillops oncall

🚨 On-Call Incident Dashboard (AI-Powered)

🤖 Generating AI incident based on your history...

╭─ 🚨 Incident #15 ─────────────────────────────────╮
│ P2 - High memory usage on Redis nodes             │
│                                                    │
│ 📅 Time: 2026-02-11T14:30:00                       │
│ 🎯 System: Redis                                   │
│ 📊 Status: OPEN                                    │
│ ⭐⭐ Difficulty: 2/5                               │
│                                                    │
│ Description:                                       │
│ Redis memory usage at 85% and climbing. Cache     │
│ evictions increasing. Performance degrading.       │
│                                                    │
│ Symptoms:                                          │
│ redis-cli INFO shows high memory, evicted_keys    │
│ metric spiking, slow query response times          │
│                                                    │
│ Your mission:                                      │
│ 1. Investigate the root cause                     │
│ 2. Implement a fix                                │
│ 3. Verify the system is healthy                   │
│ 4. Answer validation questions                    │
│                                                    │
│ 💡 Type 'hint' to get progressive help (costs points) │
╰────────────────────────────────────────────────────╯
```

### Request Hints

```bash
What would you like to do? investigate, hint, resolve, new, quit: hint
Enter incident ID for hint: 15

💡 Requesting hint level 1/3...

Socratic Question:
What Redis configuration controls memory eviction behavior?
```

### Resolve with Validation

```bash
What would you like to do? resolve
Enter incident ID to resolve: 15

Describe your resolution:
What did you do to fix the issue?
> Checked maxmemory policy, set maxmemory-policy allkeys-lru,
> increased maxmemory to 4GB, restarted Redis

📝 Validation Questions

Q1: Why did changing the eviction policy help?
Your answer: > LRU evicts least recently used keys, making room for new data

Q2: What would happen if you set maxmemory too low?
Your answer: > Redis would constantly evict keys, causing cache misses

Base score: 4/5
Hints penalty: -1
Final score: 3/5

✅ Good! Next review in 3 days

💡 Write a post-mortem: skillops post-mortem
```

## Scoring System

Your final score determines when you'll see similar incidents again:

| Score | Meaning | Next Review |
|-------|---------|-------------|
| 0 | Failed | Immediate retry |
| 1-2 | Needs work | 1 day |
| 3 | Good | 3 days |
| 4 | Solid | 7 days |
| 5 | Mastered | 14 days |

**Score Calculation:**
- Base score: 4/5 (if you answer validation questions)
- Subtract 1 point per hint used
- Minimum score: 0

## Advanced Features

### Review Due Incidents

When you run `skillops oncall`, it checks for incidents due for review:

```bash
📅 2 incident(s) due for review (spaced repetition)
These are similar to incidents you struggled with before
```

### Difficulty Progression

As you improve:
- **Beginner**: Difficulty 1-2 (basic issues, clear symptoms)
- **Intermediate**: Difficulty 3 (multi-component issues)
- **Advanced**: Difficulty 4-5 (complex distributed systems)

### Context-Aware Generation

The AI learns from:
- Your **post-mortems** (sees what root causes you've documented)
- Your **chaos events** (knows what systems you've tested)
- Your **resolution scores** (understands weak areas)
- Your **hint usage** (adapts difficulty accordingly)

## Best Practices

1. **Try without hints first**: Builds real debugging skills
2. **Write detailed resolutions**: Helps AI generate better validation questions
3. **Answer validation questions thoroughly**: Ensures SRS schedules appropriately
4. **Review regularly**: Check for due incidents daily
5. **Link to post-mortems**: Document learnings for future reference

## Troubleshooting

### "AI generation failed: GEMINI_API_KEY required"

Set your API key:
```bash
export GEMINI_API_KEY="your-key"
```

### Incident too easy/hard

The system adapts based on your scores. Complete more incidents to calibrate difficulty.

### Want to reset SRS schedule

```sql
-- Reset all incidents for immediate review
UPDATE incidents SET next_review_date = DATE('now') WHERE status = 'resolved';
```

## Examples

### Scenario 1: First-Time User (Beginner)

```
Difficulty: 1/5
Title: "Container not starting"
Symptoms: "docker ps shows container exited with code 1"
Expected: Check logs, find config error, fix and restart
```

### Scenario 2: Intermediate User

```
Difficulty: 3/5
Title: "Kubernetes pod evictions"
Symptoms: "Nodes under memory pressure, pods evicting"
Expected: Check resource limits, analyze metrics, add resources or limits
```

### Scenario 3: Advanced User

```
Difficulty: 5/5
Title: "Intermittent service mesh timeouts"
Symptoms: "5% of requests timeout, no pattern, envoy logs show circuit breaker"
Expected: Deep dive into service mesh config, traffic patterns, circuit breaker tuning
```

## Related Commands

- `skillops post-mortem`: Document incident learnings
- `skillops chaos`: Create realistic failure scenarios

## Architecture

```
User Request
    ↓
oncall.py (UI layer)
    ↓
oncall_ai.py (AI generation)
    ↓
Gemini API ←→ Database (context)
    ↓
Generated Incident (personalized)
```

The system:
1. Queries your history from SQLite
2. Builds context (weak areas, skill level)
3. Sends prompt to Gemini with constraints
4. Parses JSON response
5. Stores incident with SRS metadata

## Data Privacy

All incidents and resolutions are stored **locally** in SQLite. The AI only receives:
- Aggregated statistics (average scores, system names)
- No personal information
- No sensitive data from your environment

## Future Enhancements

- [ ] Multi-incident scenarios (cascading failures)
- [ ] Team mode (collaborative debugging)
- [ ] Custom incident templates
- [ ] Export/import incident sets
- [ ] Offline batch generation
- [ ] Performance analytics dashboard
