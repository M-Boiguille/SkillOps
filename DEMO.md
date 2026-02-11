# Quick Demo: AI-Powered On-Call Training

## Setup (30 seconds)

1. **Get your free Gemini API key**:
   - Visit: https://aistudio.google.com/app/apikey
   - Click "Create API Key"
   - Copy the key

2. **Set environment variable**:
   ```bash
   export GEMINI_API_KEY="your-api-key-here"

   # Or add to ~/.bashrc for persistence:
   echo 'export GEMINI_API_KEY="your-key"' >> ~/.bashrc
   source ~/.bashrc
   ```

3. **Verify installation**:
   ```bash
   skillops version
   skillops doctor
   ```

## Demo 1: Your First AI Incident

```bash
skillops oncall
```

**Expected output**:
```
🚨 On-Call Incident Dashboard (AI-Powered)

🤖 Generating AI incident based on your history...

╭─ 🚨 Incident #1 ─────────────────────────────────╮
│ P2 - High CPU usage on Docker containers         │
│                                                   │
│ 📅 Time: 2026-02-11T15:30:00                      │
│ 🎯 System: Docker                                 │
│ 📊 Status: OPEN                                   │
│ ⭐ Difficulty: 1/5                                │
│                                                   │
│ Description:                                      │
│ CPU usage at 90% on web-app container.          │
│ Service responding slowly. Need to investigate.  │
│                                                   │
│ Symptoms:                                         │
│ docker stats shows high CPU%, slow HTTP          │
│ response times, users reporting lag               │
│                                                   │
│ Your mission:                                     │
│ 1. Investigate the root cause                    │
│ 2. Implement a fix                               │
│ 3. Verify the system is healthy                  │
│ 4. Answer validation questions                   │
│                                                   │
│ 💡 Type 'hint' to get help (costs points)        │
╰───────────────────────────────────────────────────╯

💡 Actions: 'investigate' to view | 'hint' for help | 'resolve' when fixed
```

## Demo 2: Request Progressive Hints

```bash
# When stuck, ask for a hint
skillops oncall
# Choose: hint
# Enter incident ID: 1
```

**Level 1 (Socratic Question - FREE)**:
```
💡 Requesting hint level 1/3...

Socratic Question:
What Docker command would show you the running processes inside a container?
```

**Level 2 (Direction - costs 1 point)**:
```
💡 Requesting hint level 2/3...
(This will cost -1 points from final score)

Direction:
Check the logs of the web-app container using docker logs
```

**Level 3 (Specific Command - costs 2 points)**:
```
💡 Requesting hint level 3/3...
(This will cost -2 points from final score)

Specific Command:
docker logs web-app --tail 100 | grep ERROR
```

## Demo 3: Resolve with Validation

```bash
# After fixing the issue
skillops oncall
# Choose: resolve
# Enter incident ID: 1
```

**Interactive resolution**:
```
Describe your resolution:
What did you do to fix the issue?
> Found memory leak in application code. Restarted container
> and added memory limit. Deployed fix to prevent recurrence.

📝 Validation Questions

Answer these to demonstrate your understanding...

Q1: Why did restarting the container fix the immediate problem?
Your answer: > Cleared the accumulated memory leak, gave app fresh start

Q2: What would happen if you didn't add the memory limit?
Your answer: > Container could consume all host memory and crash other services

Q3: How would you prevent this issue in the future?
Your answer: > Add monitoring for memory usage, set up alerts, fix the leak in code

Base score: 4/5
Hints penalty: -3
Final score: 1/5

⚠️ Needs practice. Next review in 1 day

💡 Write a post-mortem: skillops post-mortem
```

## Demo 4: Spaced Repetition

After resolving several incidents, run oncall again:

```bash
skillops oncall
```

**With due reviews**:
```
🚨 On-Call Incident Dashboard (AI-Powered)

📅 2 incident(s) due for review (spaced repetition)
These are similar to incidents you struggled with before

⚠️ You have 0 active incident(s)

What would you like to do? investigate, hint, resolve, new, quit:
```

The system remembers:
- ✅ Incidents you scored low on (< 3)
- ✅ Systems you struggle with
- ✅ When to re-present similar challenges
- ✅ Your improvement over time

## Demo 5: Check Your Progress

```bash
# View all incidents (SQL query)
sqlite3 ~/.local/share/skillops/lms.db "
  SELECT
    id,
    severity,
    title,
    resolution_score,
    hints_used,
    next_review_date
  FROM incidents
  WHERE status = 'resolved'
  ORDER BY timestamp DESC
  LIMIT 10;
"
```

**Example output**:
```
1|P2|High CPU usage|1|3|2026-02-12
2|P1|Database connection pool|4|1|2026-02-18
3|P3|Certificate expiring|5|0|2026-02-25
```

## Demo 6: Write Post-Mortem

After resolving an incident:

```bash
skillops post-mortem
```

**Interactive prompts**:
```
Select incident to document:
1. P2 - High CPU usage on Docker containers [resolved]

What happened?
> Memory leak in web application causing high CPU usage

When was it detected?
> 2026-02-11 15:30 UTC - Monitoring alert

What was the impact?
> Slow response times, 10% of requests timing out

What was the root cause?
> Memory leak in request handler accumulating over time

How was it resolved?
> Restarted container, added memory limits, deployed fix

How will we prevent this?
> Added memory usage monitoring, set up alerts, code review

Action items (comma separated):
> Fix memory leak in code, Add memory alerts, Update runbook

✅ Post-mortem saved and linked to incident #1
```

## Tips for Best Experience

1. **Start without hints**: Try to solve incidents yourself first
2. **Write detailed resolutions**: Better validation questions
3. **Answer questions thoroughly**: Ensures proper SRS scheduling
4. **Review regularly**: Check for due incidents daily
5. **Link post-mortems**: Document learnings for future reference

## Scoring Strategy

To maximize your score:
- 🎯 **Aim for 5/5**: No hints, perfect validation answers
- 📚 **Learn from mistakes**: Low scores mean more practice
- 🧠 **Build real understanding**: Don't just copy-paste commands
- 📈 **Track progress**: Watch your average score improve

## Common Scenarios

### Scenario: Low Score (0-2)
**What it means**: Need more practice
**What happens**: Similar incident tomorrow
**What to do**: Study the topic, review documentation

### Scenario: Good Score (3)
**What it means**: Decent understanding
**What happens**: Review in 3 days
**What to do**: Keep practicing

### Scenario: Excellent Score (4-5)
**What it means**: Mastered the concept
**What happens**: Review in 1-2 weeks (or archived)
**What to do**: Celebrate! 🎉

## Troubleshooting

### "AI generation failed: GEMINI_API_KEY required"
```bash
export GEMINI_API_KEY="your-key"
# Get key from: https://aistudio.google.com/app/apikey
```

### Incident too easy/hard
The system adapts based on your scores. Complete more incidents to calibrate difficulty.

### Want to reset progress
```bash
# Clear resolved incidents (keeps open ones)
sqlite3 ~/.local/share/skillops/lms.db "
  DELETE FROM incidents WHERE status = 'resolved';
"
```

## Next Steps

1. **Generate 5 incidents** and practice the workflow
2. **Track your scores** and see how they improve
3. **Write post-mortems** to document learnings
4. **Enable chaos mode** to create real incidents: `skillops chaos`
5. **Integrate with workflow**: `skillops start --mode=engineering` (includes oncall)

## Summary

The AI-powered oncall system:
- 🤖 Generates **personalized** incidents
- 💡 Provides **progressive hints**
- 📝 Validates **comprehension**
- 📅 Schedules **reviews** via SRS
- 📈 Tracks **improvement** over time

Just like Anki for vocabulary, but for **debugging skills**! 🚀
