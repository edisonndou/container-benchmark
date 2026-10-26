# Git workflow (3 people, one repo)

## Rules
1. **Nobody commits directly to `main`.** Work on your own branch, open a Pull Request, one teammate reviews, then merge (squash is fine).
2. **Branch names:** `<name>/<topic>`, e.g. `bleron/setup-docker`, `donart/security-scan`, `edison/diagnostics`.
3. **Small, frequent commits:** one logical change per commit, at least one commit per working day. Commit history is evidence of each member's contribution.
4. **Before you start work:** `git switch main && git pull --rebase`, then branch. **Before you push:** `git pull --rebase origin main`.
5. Never `git push --force` to `main`. Never commit tokens, passwords or personal data.
6. Raw measurement data goes in `results/` (CSV/JSON); pilot and main runs in separate folders.

## Commit message format
`<type>(<scope>): <what, imperative, ≤ 72 chars>`

| type | use for |
|---|---|
| `docs` | proposal, README, runbook |
| `feat` | new functionality (endpoint, script) |
| `fix` | bug or wrong tag/version |
| `chore` | setup, config, cleanup |
| `data` | committing result files |
| `test` | tests, checks |

Examples:
- `docs(proposal): add research questions and baseline`
- `fix(docker): use existing node tag for alpine build`
- `feat(scripts): add startup measurement loop`
- `data(results): add pilot startup.csv`

## Daily routine
```bash
git switch main && git pull --rebase
git switch -c <name>/<topic>        # first time on a topic
# ... work ...
git add <files> && git commit -m "docs(proposal): ..."
git pull --rebase origin main
git push -u origin <name>/<topic>   # then open a Pull Request on GitHub
```
