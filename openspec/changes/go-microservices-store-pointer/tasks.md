# Tasks

## 1. Create go-microservices/openspec/config.yaml

Create the directory and file:

```bash
mkdir -p ~/Developer/go-microservices/openspec
echo "store: openspec-store" > ~/Developer/go-microservices/openspec/config.yaml
```

## 2. Verify

```bash
cat ~/Developer/go-microservices/openspec/config.yaml
cd ~/Developer/go-microservices && openspec context
openspec store doctor
```

## 3. Commit

```bash
cd ~/Developer/go-microservices
git add openspec/config.yaml
git commit -m "chore: add openspec store pointer for guide compliance"
```
