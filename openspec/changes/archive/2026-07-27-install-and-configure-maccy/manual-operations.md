# Maccy Manual Acceptance Checkpoints

Use only the synthetic strings below. Do not copy passwords, credentials,
private keys, production values, or personal clipboard history while running
these checks. Stop if macOS requests any permission other than Accessibility
or Notifications for Maccy.

Current automated baseline:

- Maccy is installed and is the only running clipboard recorder.
- Paste remains installed but inactive.
- Maccy recording is on and its history is empty.
- Spotlight **Results from Clipboard** is off.
- The secure settings profile and retained exclusions are already configured.

## 1. Clear and disable Spotlight clipboard history

1. Open **System Settings > Spotlight > Spotlight search categories**.
2. Temporarily turn **Results from Clipboard** on.
3. Click **Clear Clipboard History** and confirm the destructive clear.
4. Turn **Results from Clipboard** off again.
5. Copy `MACCY_SPOTLIGHT_OFF_B`, then immediately copy
   `MACCY_NEUTRAL_C`.
6. Open Spotlight and search only for `MACCY_SPOTLIGHT_OFF_B`.

Pass when the marker is absent and **Results from Clipboard** remains off.

## 2. Prove Accessibility, automatic paste, and paste variants

1. Open a new unsaved TextEdit document.
2. Type `MACCY_PASTE_TARGET`, add a new line, and place the caret there.
3. Copy the synthetic rich-text phrase `MACCY_RICH_SOURCE` with visible bold
   formatting.
4. Open Maccy with **Control-Shift-Command-V**.
5. Select the rich-text item normally. It must paste into TextEdit
   automatically.
6. Undo, open Maccy again, hold **Option**, and select the item. It must copy
   without injecting text.
7. Paste manually once to prove the copy-only result is available.
8. Undo, open Maccy again, hold **Shift-Command**, and select the item. It must
   paste without the bold formatting.

Pass when default selection pastes, Option selection is copy-only, and
Shift-Command selection pastes plain text.

## 3. Verify cycle selection and page navigation

1. Copy at least twelve numbered synthetic items named
   `MACCY_CYCLE_01` through `MACCY_CYCLE_12`.
2. Hold **Control-Shift-Command**, press **V** repeatedly, and release the
   modifiers on the intended item.
3. Confirm exactly one selected item is inserted.
4. Reopen Maccy and use **Page Down** and **Page Up**.

Pass when cycle selection advances predictably, confirms once, and page
navigation moves through the list.

## 4. Verify pin, edit, delete, and clear behavior

Run this only while Maccy contains synthetic test items.

1. Pin `MACCY_SAFE_PIN` with **Option-P**.
2. Edit the pin title to `Safe acceptance pin` and its text to
   `MACCY_SAFE_PIN_EDITED`.
3. Add two unpinned synthetic items.
4. Clear unpinned history and confirm the edited pin remains.
5. Unpin the item, pin it again, then delete one other item with
   **Option-Delete**.
6. Run **Clear** and explicitly confirm the final all-item clear.

Pass when clear-unpinned preserves the edited pin, delete removes only its
target, and confirmed clear-all removes the remaining synthetic items and
empties the system clipboard.

## 5. Verify application ignore and ignore-next-copy

1. In **Maccy > Preferences > Ignore > Applications**, temporarily add
   TextEdit.
2. With TextEdit physically frontmost, copy `MACCY_APP_IGNORED`.
3. Open Maccy and search only for `MACCY_APP_IGNORED`.
4. Remove TextEdit from the ignored applications list.
5. Copy `MACCY_APP_CONTROL`; confirm it appears once.
6. Hold **Option-Shift** and click the Maccy menu icon to arm
   **ignore next copy**.
7. Copy `MACCY_IGNORE_NEXT`.
8. Copy `MACCY_IGNORE_CONTROL`.
9. Search separately for both markers.

Pass when the ignored-app and ignore-next markers are absent, while both
control markers appear once. Leave the ignored applications list empty.

## 6. Verify notifications, representative apps, and both displays

1. Confirm in **System Settings > Notifications > Maccy**:
   notifications and sounds are allowed, every visual destination is off, and
   previews are **Never**.
2. Select a synthetic Maccy item and confirm the configured sound occurs
   without a banner, lock-screen item, notification-center body, or clipboard
   title.
3. Test **Control-Shift-Command-V** in TextEdit, Finder, and a browser.
4. For a password-field conflict check, open a private browser window and
   navigate to:
   `data:text/html,<input type="password" autofocus>`
5. Type only `MACCY_PASSWORD_FIELD_TEST`; confirm the Maccy shortcut opens
   without inserting, exposing, or changing that text until an item is
   deliberately selected.
6. Move the pointer and the active test window to display 1 and open Maccy.
7. Repeat on display 2.

Pass when no shortcut conflict occurs, no visual notification body appears,
and the popup opens at the cursor on both displays.

## 7. Verify login continuity

1. Create and pin `MACCY_LOGIN_SAFE_PIN`.
2. Confirm Paste is quit and Spotlight **Results from Clipboard** is off.
3. Log out of macOS and log back in.
4. Confirm exactly one Maccy instance starts automatically.
5. Confirm the configured profile and safe pin remain.
6. Copy and automatically paste `MACCY_LOGIN_SMOKE`.
7. Remove the temporary safe pin and clear the synthetic history.

Pass when one Maccy instance starts, it remains the only recorder, settings
and pin persist, and capture/paste succeeds.

## 8. Rehearse rollback with Spotlight as the prior recorder

This avoids onboarding or modifying the preserved Paste installation.

1. In Maccy Advanced preferences, turn recording off, then quit Maccy.
2. Confirm Paste remains quit.
3. Enable Spotlight **Results from Clipboard** as the only recorder.
4. Copy `MACCY_ROLLBACK_SPOTLIGHT`, immediately followed by
   `MACCY_NEUTRAL_C`.
5. Search only for `MACCY_ROLLBACK_SPOTLIGHT`, select it, and paste it into the
   unsaved TextEdit test document.
6. Clear Spotlight Clipboard History and turn **Results from Clipboard** off.
7. Relaunch Maccy, turn recording back on, and confirm Paste is still quit.
8. Copy and automatically paste `MACCY_ROLLBACK_RETURN`.
9. Clear the synthetic Maccy history and system clipboard.

Pass when Spotlight alone captures and pastes its marker, and the final state
returns to one recording Maccy instance with Spotlight and Paste inactive.

## 9. Finish the soak

The three-day soak started at `2026-07-27T08:43:42Z` and cannot finish before
`2026-07-30T08:43:42Z`.

At or after that time:

1. Confirm one Maccy process, no Paste process, and Spotlight clipboard
   recording off.
2. Confirm no sustained CPU, memory, disk-growth, popup-latency, OCR,
   shortcut, or multi-display regression occurred.
3. Leave Paste installed but inactive. Permanent removal requires a separate
   destructive change.

## Result reply

Reply using this compact format; do not include copied content or screenshots
that show personal history:

```text
1 Spotlight clear/off: PASS|FAIL
2 Paste variants: PASS|FAIL
3 Cycle/page: PASS|FAIL
4 Pin/edit/clear: PASS|FAIL
5 App-ignore/ignore-next: PASS|FAIL
6 Notifications/apps/displays: PASS|FAIL
7 Login continuity: PASS|FAIL
8 Rollback rehearsal: PASS|FAIL
9 Three-day soak: PASS|FAIL|NOT DUE
Notes: redacted failure descriptions only
```
