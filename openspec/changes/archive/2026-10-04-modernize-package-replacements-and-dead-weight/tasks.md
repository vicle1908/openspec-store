# Tasks

## 1. Realtime Frontend Dead Weight Elimination and Utility Modernization

- [x] 1.1 Remove `@babel/preset-env`, `@babel/preset-react`, `@babel/preset-typescript`, `html2canvas`, and `@types/html2canvas` from `tdt/realtime/frontend/package.json`
- [x] 1.2 Remove unused `tdt/realtime/frontend/babel.config.cjs`
- [x] 1.3 Install `clsx` and remove `classnames` in `tdt/realtime/frontend/package.json`
- [x] 1.4 Update imports from `classnames` to `clsx` in `Avatar.tsx` and `Modal.tsx`
- [x] 1.5 Run `npm install` and verify `npm run type-check`, `npm run build`, and `vitest`

## 2. Legacy Kafka Microservices Tooling Modernization

- [x] 2.1 Upgrade `markdownlint-cli2` to `^0.23.3` in `legacy/kafka-microservices/package.json`
- [x] 2.2 Run `npm install` and verify `npm run lint:md`

## 3. Workstation Root Manifest Modernization

- [x] 3.1 Add `@usebruno/cli` to `/Users/androidteam/package.json`
- [x] 3.2 Run `npm install` and verify `bru --version`

## 4. Verification and Audit

- [x] 4.1 Re-run `npm audit` across updated repositories and record residual states
- [x] 4.2 Author `evidence.md` with verifiable output
