#!/data/data/com.termux/files/usr/bin/bash
# Push FixtureLens to GitHub from an Android phone using Termux + SSH.
# No password is ever asked for or stored by this script.
set -euo pipefail

OWNER="WMiliya"
REPO="pytest-fixture-lens"

say() { printf '\n\033[1;36m==> %s\033[0m\n' "$1"; }
warn() { printf '\033[1;33m%s\033[0m\n' "$1"; }

say "Checking required tools"
for tool in git ssh ssh-keygen; do
  if ! command -v "$tool" >/dev/null 2>&1; then
    echo "Missing: $tool"
    echo "Run: pkg install -y git openssh"
    exit 1
  fi
done

say "Creating an SSH key if you do not have one"
if [ ! -f "$HOME/.ssh/id_ed25519" ]; then
  mkdir -p "$HOME/.ssh"
  chmod 700 "$HOME/.ssh"
  ssh-keygen -t ed25519 -C "termux-android" -f "$HOME/.ssh/id_ed25519" -N ""
  echo "New SSH key created."
else
  echo "Existing SSH key found."
fi

say "YOUR PUBLIC KEY - copy the whole line below"
echo "------------------------------------------------------------"
cat "$HOME/.ssh/id_ed25519.pub"
echo "------------------------------------------------------------"
cat <<'GUIDE'

Add it on GitHub (phone browser):
  Settings -> SSH and GPG keys -> New SSH key
  Title: Android Termux
  Key type: Authentication Key
  Paste the line above -> Add SSH key

Create the empty repository too (no README, no license, no .gitignore):
  https://github.com/new
  Repository name: pytest-fixture-lens

GUIDE
read -r -p "Press Enter once the key is added and the repo exists... " _

say "Testing the SSH connection"
ssh -o StrictHostKeyChecking=accept-new -T git@github.com || true

say "Setting your git identity"
if ! git config --global user.name >/dev/null 2>&1; then
  git config --global user.name "$OWNER"
fi
if ! git config --global user.email >/dev/null 2>&1; then
  printf 'Your GitHub email (or press Enter for the noreply address): '
  read -r EMAIL
  if [ -z "$EMAIL" ]; then
    EMAIL="${OWNER}@users.noreply.github.com"
  fi
  git config --global user.email "$EMAIL"
fi
echo "name : $(git config --global user.name)"
echo "email: $(git config --global user.email)"

say "Preparing the repository"
git init -q
git add .
if git diff --cached --quiet; then
  echo "Nothing new to commit."
else
  git commit -q -m "Initial FixtureLens MVP"
fi
git branch -M main

if git remote get-url origin >/dev/null 2>&1; then
  git remote set-url origin "git@github.com:${OWNER}/${REPO}.git"
else
  git remote add origin "git@github.com:${OWNER}/${REPO}.git"
fi

say "Pushing to GitHub"
if git push -u origin main; then
  say "Done"
  echo "https://github.com/${OWNER}/${REPO}"
else
  warn "Push failed. Common causes:"
  echo "  Permission denied (publickey) -> SSH key not added to GitHub yet"
  echo "  Repository not found          -> create https://github.com/new first"
  echo "  failed to push some refs      -> repo is not empty (has a README)"
  exit 1
fi
