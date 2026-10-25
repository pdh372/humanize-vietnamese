#!/usr/bin/env bash
# Symlink every skill in skills/ into the personal skill folders of Claude Code and GitHub Copilot.
# Use this instead of the plugin install if you want `git pull` to update the skill in place,
# or if your Copilot (e.g. VS Code chat) reads ~/.copilot/skills but not CLI plugins.
#
#   ./install.sh              install
#   ./install.sh --uninstall  remove the symlinks
set -euo pipefail

repo_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
targets=("$HOME/.claude/skills" "$HOME/.copilot/skills")
mode="${1:-install}"

for skill in "$repo_dir"/skills/*/; do
  name="$(basename "$skill")"
  for target in "${targets[@]}"; do
    link="$target/$name"
    if [[ "$mode" == "--uninstall" ]]; then
      if [[ -L "$link" ]]; then
        rm "$link"
        echo "removed  $link"
      fi
      continue
    fi
    mkdir -p "$target"
    if [[ -e "$link" && ! -L "$link" ]]; then
      echo "skipped  $link (a real folder is already there, remove it first)"
      continue
    fi
    ln -sfn "${skill%/}" "$link"
    echo "linked   $link -> ${skill%/}"
  done
done
