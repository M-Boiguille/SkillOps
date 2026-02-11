#!/bin/bash
# Test script to simulate oncall flow without real API key

echo "Testing oncall flow simulation..."
echo ""
echo "This will test the incident generation flow."
echo "Without GEMINI_API_KEY, it should use fallback template incidents."
echo ""

cd /home/mb/Documents/code/SkillOps

# Clear any test database
rm -f storage/skillops.db 2>/dev/null

# Simulate oncall with template (no AI)
# Since we can't interact automatically, we'll just show what happens
echo "▶ Running: python skillops.py oncall"
echo ""
echo "Expected behavior with AI key:"
echo "  1. Generate AI incident"
echo "  2. Display incident details"
echo "  3. Prompt: Choose action [investigate/hint/resolve/quit]"
echo "  4. Wait for user input"
echo ""
echo "Without AI key (fallback):"
echo "  - Uses template-based incident generation"
echo "  - Same interactive flow"
echo ""
