#!/bin/bash
set +e
RPT=/var/log/lynis-report.dat
echo "HI=$(grep hardening_index= "$RPT" 2>/dev/null)"
echo "W=$(grep -c 'warning\[' "$RPT" 2>/dev/null)"
echo "S=$(grep -c 'suggestion\[' "$RPT" 2>/dev/null)"
grep 'suggestion\[' "$RPT" 2>/dev/null | head -10
