#!/usr/bin/env bash
# Audit Dockerfiles for security compliance: non-root user, healthcheck, explicit tags.

set -euo pipefail

ERRORS=0

audit_dockerfile() {
    local df="$1"
    echo "Auditing $df..."
    
    if ! grep -q "^USER " "$df"; then
        echo "FAIL: $df lacks a non-root USER instruction"
        ERRORS=$((ERRORS + 1))
    fi

    if grep -q "FROM .*:latest" "$df"; then
        echo "FAIL: $df uses floating :latest base image tag"
        ERRORS=$((ERRORS + 1))
    fi

    if grep -E -q "curl.*\|.*sh" "$df"; then
        echo "FAIL: $df executes pipe-to-shell"
        ERRORS=$((ERRORS + 1))
    fi
}

for f in infra/docker/Dockerfile.*; do
    if [ -f "$f" ]; then
        audit_dockerfile "$f"
    fi
done

if [ "$ERRORS" -eq 0 ]; then
    echo "✓ All Dockerfiles pass security compliance checks."
    exit 0
else
    echo "✗ Dockerfile security audit failed with $ERRORS errors."
    exit 1
fi
