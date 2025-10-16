#!/bin/bash
# Demo script showing gyt workflow

set -e

echo "=== Gyt Demo ==="
echo ""

# Create a fresh test directory
rm -rf /tmp/gyt-demo
mkdir /tmp/gyt-demo
cd /tmp/gyt-demo

echo "1. Initialize repository"
gyt init
echo ""

echo "2. Configure user"
gyt config user.name "Demo User"
gyt config user.email "demo@example.com"
echo ""

echo "3. Add some milestones"
gyt add "Completed morning workout"
gyt add "Read for 30 minutes"
gyt add "Practiced guitar"
echo ""

echo "4. Check status"
gyt status
echo ""

echo "5. Commit milestones"
gyt commit -m "Productive morning routine"
echo ""

echo "6. Add more milestones"
gyt add "Cooked healthy dinner"
gyt commit -m "Evening achievements"
echo ""

echo "7. View commit log"
gyt log
echo ""

echo "8. View statistics"
gyt stats
echo ""

echo "9. Check configuration"
gyt config
echo ""

echo "=== Demo Complete ==="
echo "Repository created at: /tmp/gyt-demo"
echo "Try: cd /tmp/gyt-demo && gyt log"
