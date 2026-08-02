# Tasks: Initialize OpenSpec Store as Git Repository

## Section 1: Create .gitignore

- [ ] 1.1 Create ~/Developer/openspec-store/.gitignore with .DS_Store, logs, temp patterns
- [ ] 1.2 Verify .DS_Store files are excluded from staging

## Section 2: Initialize Git Repository

- [ ] 2.1 Run `git init` in ~/Developer/openspec-store/
- [ ] 2.2 Run `git add -A` to stage all content
- [ ] 2.3 Verify: `git status` shows all openspec/ content staged, .DS_Store excluded

## Section 3: Initial Commit

- [ ] 3.1 Create initial commit with descriptive message
- [ ] 3.2 Verify: `git log --oneline -1` shows commit
- [ ] 3.3 Verify: `git status` shows clean working tree

## Section 4: Validation

- [ ] 4.1 `openspec store doctor` shows "Git: ok"
- [ ] 4.2 `openspec validate --all --store openspec-store` passes
- [ ] 4.3 `make validate-agent-guidance` passes

## Section 5: Update Documentation

- [ ] 5.1 Update ~/Developer/AGENTS.md with store git tracking info
- [ ] 5.2 Update go-microservices/AGENTS.md to reference store practices
