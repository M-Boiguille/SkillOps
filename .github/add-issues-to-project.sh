#!/bin/bash
# Script to add all Sprint 1 issues to GitHub Project

PROJECT_NUMBER=2
OWNER="M-Boiguille"
REPO="SkillOps"

# Get project ID
PROJECT_ID=$(gh api graphql -f query='
  query($owner: String!, $number: Int!) {
    user(login: $owner) {
      projectV2(number: $number) {
        id
      }
    }
  }
' -f owner=$OWNER -F number=$PROJECT_NUMBER --jq '.data.user.projectV2.id')

echo "Project ID: $PROJECT_ID"

# Get all open issues
ISSUES=$(gh issue list --repo $OWNER/$REPO --state open --limit 100 --json number --jq '.[].number')

echo "Adding issues to project..."

for issue_number in $ISSUES; do
  # Get issue node ID
  ISSUE_ID=$(gh api graphql -f query='
    query($owner: String!, $repo: String!, $number: Int!) {
      repository(owner: $owner, name: $repo) {
        issue(number: $number) {
          id
        }
      }
    }
  ' -f owner=$OWNER -f repo=$REPO -F number=$issue_number --jq '.data.repository.issue.id')
  
  # Add issue to project
  gh api graphql -f query='
    mutation($project: ID!, $item: ID!) {
      addProjectV2ItemById(input: {projectId: $project, contentId: $item}) {
        item {
          id
        }
      }
    }
  ' -f project=$PROJECT_ID -f item=$ISSUE_ID > /dev/null
  
  echo "  ✓ Added issue #$issue_number"
done

echo ""
echo "✓ All issues added to project!"
echo "✓ View project: https://github.com/users/$OWNER/projects/$PROJECT_NUMBER"
