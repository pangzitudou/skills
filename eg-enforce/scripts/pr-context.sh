#!/usr/bin/env bash
# pr-context.sh — gather the PR context eg-enforce needs (diff + Yunxiao PR
# metadata) for one repo. References yunxiao-pr-manage for the PR query; it does
# NOT re-implement the Codeup API. Read-only: no push, no branch mutation.
#
# Output (stdout, and --output-path): JSON
#   {repo, source, target, prUrl, prStatus, prTitle, diffPath, diffFiles}
# Feed prUrl/prTitle to notify.py and diffPath to the review subagents.
set -o pipefail

REPO="" SOURCE="" TARGET="" OUTPUT_PATH="" DIFF_PATH=""
WORKSPACE_ROOT="/home/zenia/projects/gnzs"
ORG="68761da7cdc0e9db90ae14de" GROUP="saleforteAI"
API="https://openapi-rdc.aliyuncs.com"

while [ $# -gt 0 ]; do case "$1" in
  --repo) REPO="$2"; shift 2;;
  --source) SOURCE="$2"; shift 2;;
  --target) TARGET="$2"; shift 2;;
  --workspace-root) WORKSPACE_ROOT="$2"; shift 2;;
  --output-path) OUTPUT_PATH="$2"; shift 2;;
  --diff-path) DIFF_PATH="$2"; shift 2;;
  -h|--help) echo "Usage: pr-context.sh --repo NAME --target BRANCH [--source BRANCH]" >&2; exit 0;;
  *) echo "unknown arg: $1" >&2; exit 2;;
esac; done

[ -n "$REPO" ]   || { echo "missing --repo" >&2; exit 2; }
[ -n "$TARGET" ] || { echo "missing --target" >&2; exit 2; }
command -v jq  >/dev/null || { echo "jq required" >&2; exit 2; }
command -v git >/dev/null || { echo "git required" >&2; exit 2; }

REPO_PATH="$WORKSPACE_ROOT/$REPO"
[ -d "$REPO_PATH/.git" ] || [ -d "$REPO_PATH" ] || { echo "repo not found: $REPO_PATH" >&2; exit 1; }

# source defaults to the repo's current branch
[ -n "$SOURCE" ] || SOURCE="$(git -C "$REPO_PATH" rev-parse --abbrev-ref HEAD 2>/dev/null)"
[ -n "$SOURCE" ] || { echo "cannot resolve source branch; pass --source" >&2; exit 1; }
[ "$SOURCE" = "HEAD" ] && { echo "repo is detached; pass --source" >&2; exit 1; }

# refresh the diff base; fall back to cached ref if offline
git -C "$REPO_PATH" fetch -q origin "$TARGET" 2>/dev/null \
  || echo "WARN: fetch origin/$TARGET failed; using cached ref" >&2
git -C "$REPO_PATH" rev-parse --verify -q "origin/$TARGET^{commit}" >/dev/null \
  || { echo "FAILED_GIT_REMOTE: no origin/$TARGET" >&2; exit 1; }

# diff = changes introduced on source since its merge-base with target
[ -n "$DIFF_PATH" ] || DIFF_PATH="$(mktemp /tmp/eg-enforce-diff.XXXXXX.patch)"
git -C "$REPO_PATH" -c core.quotepath=false diff "origin/$TARGET...$SOURCE" >"$DIFF_PATH"
DIFF_FILES="$(git -C "$REPO_PATH" diff --name-only "origin/$TARGET...$SOURCE" | grep -c . || true)"

# PR metadata via yunxiao-pr-manage --query-only (read-only reuse)
YX="$WORKSPACE_ROOT/.agents/skills/yunxiao-pr-manage/scripts/yunxiao-pr-manage.sh"
PR_URL="" PR_STATUS="UNKNOWN" PR_TITLE=""
if [ -n "$YUNXIAO_TOKEN" ] && [ -f "$YX" ]; then
  MANIFEST="$(mktemp /tmp/eg-enforce-manifest.XXXXXX.json)"
  jq -n --arg o "$ORG" --arg g "$GROUP" --arg a "$API" --arg w "$WORKSPACE_ROOT" \
     --arg repo "$REPO" --arg s "$SOURCE" --arg t "$TARGET" \
     '{organizationId:$o, groupPath:$g, apiBaseUrl:$a, workspaceRoot:$w,
       items:[{repo:$repo, source:$s, target:$t, integration:($s+"-"+$t)}]}' >"$MANIFEST"
  RES="$(bash "$YX" --manifest "$MANIFEST" --query-only --output-json 2>/dev/null)"
  if [ -n "$RES" ] && jq -e . >/dev/null 2>&1 <<<"$RES"; then
    PR_URL="$(jq -r '.[0].prUrl // ""' <<<"$RES")"
    PR_STATUS="$(jq -r '.[0].status // "UNKNOWN"' <<<"$RES")"
    PR_TITLE="$(jq -r '.[0].title // ""' <<<"$RES")"
  fi
  rm -f "$MANIFEST"
else
  PR_STATUS="NO_TOKEN_OR_TOOL"
fi

# fallback title: latest commit subject on source
[ -n "$PR_TITLE" ] || PR_TITLE="$(git -C "$REPO_PATH" log -1 --pretty=%s "$SOURCE" 2>/dev/null)"

CTX="$(jq -n --arg repo "$REPO" --arg source "$SOURCE" --arg target "$TARGET" \
  --arg prUrl "$PR_URL" --arg prStatus "$PR_STATUS" --arg prTitle "$PR_TITLE" \
  --arg diffPath "$DIFF_PATH" --argjson diffFiles "${DIFF_FILES:-0}" \
  '{repo:$repo, source:$source, target:$target, prUrl:$prUrl, prStatus:$prStatus,
    prTitle:$prTitle, diffPath:$diffPath, diffFiles:$diffFiles}')"

[ -n "$OUTPUT_PATH" ] && printf '%s\n' "$CTX" >"$OUTPUT_PATH"
printf '%s\n' "$CTX"
