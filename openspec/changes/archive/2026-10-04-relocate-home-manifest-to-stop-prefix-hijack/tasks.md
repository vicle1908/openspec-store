# Tasks

## 1. Establish the Configuration and Its Consumers

- [x] 1.1 Confirm `npm prefix` resolves to `/Users/androidteam` from `~/Developer`
- [x] 1.2 Identify the sanctioned global npm prefix used by the workspace daily update script (`~/.npm-global`)
- [x] 1.3 Determine which packages are unique to the home manifest and which resolve elsewhere
- [x] 1.4 Confirm no workspace script invokes `bru`, `newman`, or `yaml-language-server` from a repo directory
- [x] 1.5 Demonstrate the hijack live (`npx bru --version` resolving from `~/Developer`)

## 2. Build the Relocation Target

- [x] 2.1 Create `~/.local/share/home-toolchain/`
- [x] 2.2 Copy `package.json` and `package-lock.json` to the new location
- [x] 2.3 Run `npm install` at the new location
- [x] 2.4 Record the pre-state manifest for rollback

## 3. Verify the Relocation Before Removal

- [x] 3.1 Verify `bru --version` → `4.2.0` at the new location
- [x] 3.2 Verify `yaml-language-server --version` → `1.24.0` at the new location
- [x] 3.3 Verify `newman-reporter-htmlextra` executes at the new location
- [x] 3.4 Verify `npm audit` at the new location reports the same 12 high advisories
- [x] 3.5 Verify the `@faker-js/faker` split resolution is preserved (`9.9.0` / nested `5.5.3`)

## 4. Remove the Home Manifest

- [x] 4.1 Remove `/Users/androidteam/package.json`
- [x] 4.2 Remove `/Users/androidteam/package-lock.json`
- [x] 4.3 Remove `/Users/androidteam/node_modules`
- [x] 4.4 Confirm the three paths no longer exist

## 5. Verify the Hijack Is Eliminated

- [x] 5.1 Confirm `npm prefix` from `~/Developer` reports `~/Developer`
- [x] 5.2 Confirm `npm prefix` from `~/Developer/platform` reports that directory
- [x] 5.3 Confirm `npm prefix` from an unrelated directory resolves to that directory

## 6. Preserve Usability and Unrelated Installations

- [x] 6.1 Add `~/.local/bin` symlinks for `bru`, `yaml-language-server`, `newman-reporter-htmlextra`
- [x] 6.2 Confirm each resolves and reports its version when invoked by name
- [x] 6.3 Confirm `gitnexus --version` still reports `1.6.12`
- [x] 6.4 Confirm `~/.npm-global` is untouched
- [x] 6.5 Confirm no repository under `~/Developer` was affected

## 7. Evidence and Spec Sync

- [x] 7.1 Author `evidence.md` in the change directory from output read back from disk
- [x] 7.2 Run `openspec validate --all` and confirm the delta spec validates
- [x] 7.3 Sync the delta spec into the main `npm-audit-remediation` spec at archive time
- [x] 7.4 Archive the change and commit the store
