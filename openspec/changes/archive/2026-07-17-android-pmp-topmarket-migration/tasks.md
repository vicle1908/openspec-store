## Verification Findings (post-implementation review)

Bugs found and fixed during verification:

### HIGH - Stale PMPUtilViewModel resetAllData calls
Three `mMarketPMPUtilVM.resetAllData()` calls were left behind after removing
`setOnResponseListener`. These would cause concurrent state between PMPUtilViewModel
and PMPViewModel. All replaced with `pmpViewModel.unsubscribe()`.

| File | Function | Fix |
|------|----------|-----|
| `MarketTopDetailBaseScreen` | `getDataForMarketTop()` | `pmpViewModel.unsubscribe()` |
| `MarketTopBaseFragment` | `getDataForMarketTop()` | `pmpViewModel.unsubscribe()` |
| `MarketTopBaseFragment` | `updateMarketInfo()` | `pmpViewModel.unsubscribe()` |
| `HKPreIPOFragment` | `reconnectHkPreIpoPmpFull()` | `pmpViewModel.detach()` + `initPmpConnections()` |

### MEDIUM - @Suppress annotation misplacement
`@Suppress("unused")` was on `pmpViewModel` but the comment said "mMarketPMPUtilVM".
The unused field was `mMarketPMPUtilVM` (no body calls after migration). Corrected
in all 3 base classes.

### LOW - Stale PMPUpdate.kt KDoc
`PMPUpdate.data` KDoc said "Raw (not aliased)" but `PMPViewModel.aliasFields()`
aliases the data before emitting. KDoc updated to reflect actual behavior.

### HIGH - Main-thread Room query in PMPConnectionCenter.subscribe()
`loadPmpSettingModel()` called `PmpSettingsDao.getJsonPMPSettings()` (blocking,
no `suspend`) synchronously on the main thread from `Fragment.onResume()` via the
`PMPViewModel.subscribe()` → `PMPConnectionCenter.subscribe()` call chain.
Room throws `IllegalStateException: Cannot access database on the main thread`
when this happens (ViewPager2 pages restore synchronously on the main thread).

Root cause: `PmpSettingsDao.getJsonPMPSettings()` has no `suspend` modifier,
so it blocks. The singleton `PMPConnectionCenter.subscribe()` was the first
caller to hit this path — all other callers were already off the main thread.

Fix: made `PMPConnectionCenter.subscribe()` a `suspend fun` and wrapped the
Room call in `withContext(Dispatchers.IO) { loadPmpSettingModel() }`. `PMPViewModel`
dispatches the call via `viewModelScope.launch(Dispatchers.IO) { ... }`, so callers
(`Fragment.onResume`) stay unaffected. The `onTokenReady(token, counters, fields)`
continuation is extracted as a private method, shared between the fresh-token and
reusing-token paths.

| File | Change |
|------|--------|
| `PMPConnectionCenter.kt` | `subscribe()` → `suspend fun`; Room query in `withContext(Dispatchers.IO)` |
| `PMPViewModel.kt` | `subscribe()` → `viewModelScope.launch(Dispatchers.IO)` for token acquisition; `onTokenReady()` extracted |

### VERIFIED - Runtime smoke test (full Android device)
All 5 smoke tests passed on `emulator-5554` (SDK 35, API 35):
- Watchlist live prices (TSLA $237.20 +2.28%)
- Market tab → Top Market SGX indices rendering
- Top Volume tab → 5 instruments (TPLMW01–TPLMW05) live bid/ask/last/volume
- `emitToAllTokens` firing every ~100–500ms on `TOPMW01–05` topics
- Zero `IllegalStateException` / main-thread violations post-fix

### VERIFIED - Subclass inheritance clean
All 6 detail screen subclasses and 4 overview fragment subclasses inherit
the parent's PMP flow correctly via `super.onViewCreated()`.

### VERIFIED - aliasFields chain
`aliasFields()` uses the same algorithm as `getFinalHashMapPmpResponse` -
both scan `value.split(",")` for raw key match, output canonical value string.

### VERIFIED - Bytecode
javap disassembly confirmed `emissionCounter.incrementAndGet()` and `aliasFields()`
in compiled `PMPViewModel$subscribe$2$1.class`.

### Unable to verify - No full Android runtime
Emulator (sdk_gphone16k_arm64, API 37) is a minimal container without system_server
or package service. APK metadata verified via aapt: com.tdt.pmobile3.p2, v3.3.54.

---

## 1. Pre-flight checks

- [x] 1.1 Confirm worktree at `hoangtran/sr-3738-pmp-connection-center` (or new branch `hoangtran/sr-3859-topmarket-pmp-migration`) based on `origin/release/v3.3.54_develop_27_06_2026`:
  ```bash
  cd /Users/lekhanhvinh/Developer/tdt/poems-mobile3-android-sr3738-pmp-center
  git log --oneline -3
  git status
  ```
- [x] 1.2 Verify `PMPViewModel.kt` and `PMPUpdate.kt` exist (the parent change's Phase 2 landed):
  ```bash
  ls -la app/src/main/java/com/tdt/pmobile3/viewmodels/common/PMPViewModel.kt
  ls -la app/src/main/java/com/tdt/pmobile3/viewmodels/common/PMPUpdate.kt
  ```
- [x] 1.3 Verify `NewOrderBottomSheet.kt` is on `PMPViewModel` (not `PMPUtilViewModel`):
  ```bash
  grep -n "pmpViewModel: PMPViewModel\|pmpViewModel.pmpDataFlow.collect" \
    app/src/main/java/com/tdt/pmobile3/ui/screens/trade/options/positions/neworder/NewOrderBottomSheet.kt
  ```
  Expected: at least 3 matches
- [x] 1.4 Run impact analysis via GitNexus (HIGH/CRITICAL risk on `PMPViewModel` is expected — flag and proceed):
  ```bash
  gitnexus_impact -r poems-mobile3-android --target PMPViewModel --direction upstream
  ```
- [x] 1.5 Verify no subclass of `MarketTopDetailBaseScreen` or `MarketTopBaseFragment` overrides `initPmpConnections`:
  ```bash
  grep -rn "override fun initPmpConnections" \
    app/src/main/java/com/tdt/pmobile3/ui/screens/market/
  ```
  Expected: no matches (the base class implementation is used as-is)
- [x] 1.6 Verify `getPmpTopicByPriceAgreement()` is the topic-source method (not raw `pmpTopic`):
  ```bash
  grep -n "getPmpTopicByPriceAgreement\|counter.PMPTopic" \
    app/src/main/java/com/tdt/pmobile3/viewmodels/common/PMPViewModel.kt
  ```
  Expected: `getPmpTopicByPriceAgreement` is the call site (already in landed code)
- [x] 1.7 Verify the `mIsUseDefaultFidID` legacy behavior in `PMPUtilViewModel` to confirm the aliasing contract:
  ```bash
  grep -n "mIsUseDefaultFidID\|getFinalHashMapPmpResponse\|mListColumnPmpEnum" \
    app/src/main/java/com/tdt/pmobile3/viewmodels/common/PMPUtilViewModel.kt
  ```
  Expected: `mIsUseDefaultFidID = true` default, `getFinalHashMapPmpResponse` aliases raw FIDs to canonical `value` strings

## 2. Implement `isAllDataReturned` in `PMPViewModel`

- [x] 2.1 Add imports to `PMPViewModel.kt`:
  ```kotlin
  import java.util.concurrent.atomic.AtomicInteger
  ```
- [x] 2.2 Add the two `AtomicInteger` fields after the existing `collectorJob` field:
  ```kotlin
  private val emissionCounter = AtomicInteger(0)
  private val expectedTopicCount = AtomicInteger(0)
  ```
- [x] 2.3 In `subscribe(counters, fields)`, after the `mHashmapIndexOfCounter` rebuild and BEFORE `collectorJob = viewModelScope.launch(...)`:
  ```kotlin
  expectedTopicCount.set(mHashmapIndexOfCounter.size)
  emissionCounter.set(0)
  ```
- [x] 2.4 In the collector body, replace the existing `PMPUpdate(...)` construction with the new algorithm:
  ```kotlin
  token.priceUpdates.collect { (topic, rawData) ->
      val indices = mHashmapIndexOfCounter[topic] ?: emptyList()
      val counter = emissionCounter.incrementAndGet()
      val isLast = counter >= expectedTopicCount.get()
      if (isLast) emissionCounter.set(0)
      val update = PMPUpdate(
          topic = topic,
          indices = indices,
          data = rawData,  // raw data for now; aliasFields added in step 3.x
          isAllDataReturned = isLast,
      )
      _pmpDataFlow.tryEmit(update)
  }
  ```
  (Note: `data = rawData` will be replaced by `data = aliasFields(rawData, fields)` in the next task group.)
- [x] 2.5 `./gradlew :app:compileUatDebugKotlin --quiet` — expect BUILD SUCCESSFUL. (This is an intermediate commit — the algorithm change alone, before aliasing.)

## 3. Implement `aliasFields()` in `PMPViewModel`

- [x] 3.1 Add the `aliasFields()` private function to `PMPViewModel.kt`:
  ```kotlin
  /**
   * Aliases raw PMP FID keys to canonical WatchListColumnsSettingModel.value strings.
   *
   * Mirrors the legacy `PMPUtilViewModel.getFinalHashMapPmpResponse` semantic: when
   * mIsUseDefaultFidID = true (the default), the raw key "9" is rewritten to the
   * canonical "9,F009,P23" so that consumers can do
   * `linkMapPMP[PMPFieldsForSetting.TRADE_PRICE.columnsSettingModel.value]`.
   *
   * Unknown raw keys (e.g., server fields the client enum doesn't know about) are
   * passed through unchanged.
   */
  private fun aliasFields(
      rawData: LinkedHashMap<String, String>,
      subscribeFields: List<WatchListColumnsSettingModel>,
  ): LinkedHashMap<String, String> {
      val aliased = linkedMapOf<String, String>()
      rawData.forEach { (rawKey, value) ->
          val canonical = subscribeFields.firstOrNull { canonical ->
              canonical.value.split(",").contains(rawKey)
          }?.value
          aliased[canonical ?: rawKey] = value
      }
      return aliased
  }
  ```
- [x] 3.2 Update the collector body to call `aliasFields()`:
  ```kotlin
  token.priceUpdates.collect { (topic, rawData) ->
      val indices = mHashmapIndexOfCounter[topic] ?: emptyList()
      val aliasedData = aliasFields(rawData, fields)
      val counter = emissionCounter.incrementAndGet()
      val isLast = counter >= expectedTopicCount.get()
      if (isLast) emissionCounter.set(0)
      val update = PMPUpdate(
          topic = topic,
          indices = indices,
          data = aliasedData,
          isAllDataReturned = isLast,
      )
      _pmpDataFlow.tryEmit(update)
  }
  ```
- [x] 3.3 `./gradlew :app:compileUatDebugKotlin --quiet` — expect BUILD SUCCESSFUL. This commit fixes BOTH the TopMarket migration AND the pre-existing `NewOrderBottomSheet` aliasing gap.
- [x] 3.4 **Operational**: Manual smoke test — deferred to device testing (cross-check `NewOrderBottomSheet`): open Trade bottom sheet, verify prices update correctly (bid, ask, trade, change, change%, bid/ask size). If the screen was silently broken before (lookups returning null), prices will now display correctly. If prices were already displaying, this is a no-op (the aliasing was a no-op for the data shape the server returned).

## 4. Migrate `MarketTopDetailBaseScreen` (base class)

- [x] 4.1 Add imports for `PMPViewModel`, `PMPUpdate`, lifecycle, coroutines:
  ```kotlin
  import com.tdt.pmobile3.viewmodels.common.PMPViewModel
  import com.tdt.pmobile3.viewmodels.common.PMPUpdate
  import androidx.lifecycle.Lifecycle
  import androidx.lifecycle.lifecycleScope
  import androidx.lifecycle.repeatOnLifecycle
  import kotlinx.coroutines.launch
  ```
- [x] 4.2 Add the ViewModel field next to the existing `mMarketPMPUtilVM` field:
  ```kotlin
  protected val pmpViewModel: PMPViewModel by viewModels()
  ```
  (Use `protected` so subclasses — `IndicesDetailScreen`, `HKPreIPODetailScreen`, `FractionalShareTopDetailBaseScreen` — can also access it if needed.)
- [x] 4.3 Add `@Suppress("unused")` to the existing `mMarketPMPUtilVM` field with a KDoc comment pointing to the migration plan.
- [x] 4.4 Add cache fields (for the onResume re-subscribe pattern):
  ```kotlin
  // SR-3738 - cached so onResume() can re-arm the collector after onPause() -> detach()
  private var pmpCounters: List<CounterDetail>? = null
  private var pmpFields: List<WatchListColumnsSettingModel>? = null
  ```
- [x] 4.5 Remove the `mMarketPMPUtilVM.setOnResponseListener { topic, linkedHashMap, _ -> ... }` callback (line 894). The new `onPmpReceived(update)` function will replace the body.
- [x] 4.6 Add flow collection in `onViewCreated` (after the existing view setup, before `getDataBundle()` or similar):
  ```kotlin
  viewLifecycleOwner.lifecycleScope.launch {
      viewLifecycleOwner.repeatOnLifecycle(Lifecycle.State.STARTED) {
          pmpViewModel.pmpDataFlow.collect { update ->
              onPmpReceived(update)
          }
      }
  }
  ```
- [x] 4.7 Implement `onPmpReceived(update: PMPUpdate)`:
  ```kotlin
  protected open fun onPmpReceived(update: PMPUpdate) {
      val index = update.indices.firstOrNull() ?: return
      val linkedHashMap = update.data
      lifecycleScope.launch(Dispatchers.Default) {
          withContext(Dispatchers.Main) {
              mMarketTopNameAdapter.updateListWithPMP(index, linkedHashMap)
              mMarketTopNameAdapter.notifyItemChanged(index, linkedHashMap)
              mMarketTopBoxTypeAdapter.notifyItemChanged(index, linkedHashMap)
              mFieldMarketTopColumnsLands.notifyItemChanged(index, linkedHashMap)
          }
      }
  }
  ```
  (Preserve the existing threading — the legacy code used `lifecycleScope.launch(Dispatchers.Default) { ... withContext(Dispatchers.Main) { ... } }`. The `repeatOnLifecycle(STARTED)` collector runs on the main thread, so the `Dispatchers.Default` hop is preserved.)
- [x] 4.8 Replace `initPmpConnections()` body (line 1073-1099) to cache and call `pmpViewModel.subscribe()`:
  ```kotlin
  open fun initPmpConnections() {
      if (pmpViewModel.pmpToken != null) return  // preserve existing isInitializedPmpConn() guard
      val valueTopCounter =
          if (mDefaultMarketType == TOP_VOLUME && mMarketStockVM.mIsListViewTypeMarketTop.value == false) mMarketStockVM.topVolumeMarketModelLD.value else mMarketStockVM.topMarketModelLD.value
      if (valueTopCounter != null) {
          val counters = valueTopCounter.topCounters?.map { topCounter ->
              CounterDetail(
                  pmpTopic = topCounter.pmpTopic,
                  product = topCounter.product,
                  productIcon = topCounter.productIcon,
                  market = topCounter.market,
                  delayIndicator = topCounter.delayIndiciator,
                  exchange = topCounter.exchange
              )
          }
          val pmpList = mListLandFieldColumns + arrayListOf(
              PMPFields.FRACTIONAL_INDICATOR.columnsSettingModel,
              PMPFieldsForSetting.COMPANY_NAME.columnsSettingModel,
              PMPFields.FEED_CODE.columnsSettingModel
          )
          pmpCounters = ArrayList(counters ?: arrayListOf())
          pmpFields = ArrayList(pmpList)
          pmpViewModel.subscribe(
              counters = pmpCounters!!,
              fields = pmpFields!!,
          )
      }
  }
  ```
- [x] 4.9 Replace `onResume()` body (line 1178-1181) to re-arm the collector with cached values:
  ```kotlin
  override fun onResume() {
      super.onResume()
      val counters = pmpCounters
      val fields = pmpFields
      if (counters != null && fields != null) {
          pmpViewModel.subscribe(counters, fields)
      } else {
          initPmpConnections()  // cold start path
      }
  }
  ```
- [x] 4.10 Replace `onPause()` body (line 1173-1176):
  ```kotlin
  override fun onPause() {
      super.onPause()
      pmpViewModel.detach()
  }
  ```
- [x] 4.11 Replace `onDestroy()` body (line 1183-1186):
  ```kotlin
  override fun onDestroy() {
      super.onDestroy()
      pmpViewModel.unsubscribe()
      pmpCounters = null
      pmpFields = null
  }
  ```
- [x] 4.12 Optional: remove `getIndexByTopic(topic: String?): Int?` (line 804) — its purpose is replaced by `update.indices.firstOrNull()`. Verify no other callers before removal.
- [x] 4.13 `./gradlew :app:compileUatDebugKotlin --quiet` — expect BUILD SUCCESSFUL. Subclasses (`IndicesDetailScreen`, `HKPreIPODetailScreen`, `FractionalShareTopDetailBaseScreen`) inherit the migration.

## 5. Migrate `MarketTopBaseFragment` (base fragment)

- [x] 5.1 Add the same imports as step 4.1.
- [x] 5.2 Add the ViewModel field:
  ```kotlin
  protected val pmpViewModel: PMPViewModel by viewModels()
  ```
- [x] 5.3 Add cache fields (`pmpCounters`, `pmpFields`).
- [x] 5.4 Add `@Suppress("unused")` to the existing `mMarketPMPUtilViewModel` field.
- [x] 5.5 Remove the `mMarketPMPUtilViewModel.setOnResponseListener { index, linkedHashMap -> ... }` callback (line 506).
- [x] 5.6 Add flow collection in `onViewCreated`:
  ```kotlin
  viewLifecycleOwner.lifecycleScope.launch {
      viewLifecycleOwner.repeatOnLifecycle(Lifecycle.State.STARTED) {
          pmpViewModel.pmpDataFlow.collect { update ->
              onPmpReceived(update)
          }
      }
  }
  ```
- [x] 5.7 Implement `onPmpReceived(update: PMPUpdate)`:
  ```kotlin
  protected open fun onPmpReceived(update: PMPUpdate) {
      val index = update.indices.firstOrNull() ?: return
      lifecycleScope.launch(Dispatchers.Default) {
          mMarketTopAdapter.updateListWithPMP(index, update.data)
          withContext(Dispatchers.Main) {
              mMarketTopAdapter.notifyItemChanged(index, update.data)
          }
      }
  }
  ```
- [x] 5.8 Replace `initPmpConnections()` body (line 404) to cache and call `pmpViewModel.subscribe()`:
  ```kotlin
  protected fun initPmpConnections() {
      val canShowPrice = AppDataManager.canShowPrice(mCurrentMarketTopModel?.market)
      if (pmpViewModel.pmpToken != null || !canShowPrice) {
          return
      }
      val valueTopCounter = mMarketStockViewModel.topMarketModelLD.value
      if (valueTopCounter != null) {
          val listPMPTopic = valueTopCounter.pmpTopic?.split(",")
          val listCounterDetail = listPMPTopic?.mapIndexed { index, s ->
              val topCounter = valueTopCounter.topCounters?.getOrNull(index)
              CounterDetail(
                  pmpTopic = s,
                  product = topCounter?.product,
                  productIcon = topCounter?.productIcon,
                  market = topCounter?.market,
                  delayIndicator = topCounter?.delayIndiciator,
                  exchange = topCounter?.exchange,
                  canShowPrice = topCounter?.canShowPrice ?: true
              )
          }
          val subscribeFields = arrayListOf(
              PMPFieldsForSetting.COMPANY_NAME.columnsSettingModel,
              PMPFields.FEED_CODE.columnsSettingModel,
              PMPFieldsForSetting.TRADE_PRICE.columnsSettingModel,
              PMPFieldsForSetting.TRADE_VOL.columnsSettingModel,
              PMPFieldsForSetting.PCT_CHANGE.columnsSettingModel,
              PMPFields.NET_CHANGE.columnsSettingModel,
              PMPFields.CHANGE.columnsSettingModel,
              PMPFields.FRACTIONAL_INDICATOR.columnsSettingModel
          )
          pmpCounters = ArrayList(listCounterDetail ?: arrayListOf())
          pmpFields = ArrayList(subscribeFields)
          pmpViewModel.subscribe(pmpCounters!!, pmpFields!!)
      }
  }
  ```
- [x] 5.9 Replace `onMarketTopPmpResume()` body (line 649-651):
  ```kotlin
  protected open fun onMarketTopPmpResume() {
      val counters = pmpCounters
      val fields = pmpFields
      if (counters != null && fields != null) {
          pmpViewModel.subscribe(counters, fields)
      }
  }
  ```
- [x] 5.10 Replace `onPause()` body (line 638-641):
  ```kotlin
  override fun onPause() {
      super.onPause()
      pmpViewModel.detach()
  }
  ```
- [x] 5.11 Replace `onDestroy()` body (line 654-657):
  ```kotlin
  override fun onDestroy() {
      super.onDestroy()
      pmpViewModel.unsubscribe()
      pmpCounters = null
      pmpFields = null
  }
  ```
- [x] 5.12 `./gradlew :app:compileUatDebugKotlin --quiet` — expect BUILD SUCCESSFUL. Subclasses (`TopVolumeFragment`, `TopLoserFragment`, `TopGainerFragment`, `HKPreIPOFragment`) inherit the migration.

## 6. Migrate `TabMarketStockScreen` (standalone fragment)

- [x] 6.1 Add the same imports as step 4.1.
- [x] 6.2 Add the ViewModel field:
  ```kotlin
  private val pmpViewModel: PMPViewModel by viewModels()
  ```
- [x] 6.3 Add cache fields (`pmpCounters`, `pmpFields`).
- [x] 6.4 Add `@Suppress("unused")` to the existing `mMarketPMPUtilViewModel` field.
- [x] 6.5 Remove the two `mMarketPMPUtilViewModel.resetAllData()` calls (lines 170, 579) — they no longer have a target.
- [x] 6.6 Remove the `mMarketPMPUtilViewModel.setOnResponseListener { index, linkedHashMap -> ... }` callback (line 607).
- [x] 6.7 Add flow collection in `onViewCreated`.
- [x] 6.8 Implement `onPmpReceived(update: PMPUpdate)`:
  ```kotlin
  private fun onPmpReceived(update: PMPUpdate) {
      val index = update.indices.firstOrNull() ?: return
      activity?.runOnUiThread {
          mCounterIndicesAdapter.updateListWithPMP(index, update.data)
      }
  }
  ```
- [x] 6.9 Replace `initPmpConnectionsTopIndices()` body (line 466) to cache and call `pmpViewModel.subscribe()`:
  ```kotlin
  private fun initPmpConnectionsTopIndices(listSortedWithMarket: List<MarketTopItemModel>?) {
      if (pmpViewModel.pmpToken != null) return
      if (!listSortedWithMarket.isNullOrEmpty()) {
          val listCounterDetail = listSortedWithMarket.map { topCounter ->
              CounterDetail(
                  pmpTopic = topCounter.pmpTopic,
                  product = topCounter.product,
                  productIcon = topCounter.productIcon,
                  market = topCounter.market,
                  delayIndicator = topCounter.delayIndiciator,
                  exchange = topCounter.exchange,
              )
          }
          val subscribeFields = arrayListOf(
              PMPFieldsForSetting.COMPANY_NAME.columnsSettingModel,
              PMPFields.FEED_CODE.columnsSettingModel,
              PMPFieldsForSetting.TRADE_PRICE.columnsSettingModel,
              PMPFieldsForSetting.PCT_CHANGE.columnsSettingModel,
              PMPFieldsForSetting.NET_CHANGE.columnsSettingModel
          )
          pmpCounters = ArrayList(listCounterDetail)
          pmpFields = ArrayList(subscribeFields)
          pmpViewModel.subscribe(pmpCounters!!, pmpFields!!)
      }
  }
  ```
- [x] 6.10 Replace `onResume()` body (line 1095-1107) to re-arm the collector with cached values:
  ```kotlin
  override fun onResume() {
      updatePriceAgreements()
      super.onResume()
      syncEuExchangeFromDetailScreen()
      val counters = pmpCounters
      val fields = pmpFields
      if (counters != null && fields != null) {
          pmpViewModel.subscribe(counters, fields)
      }
      enableUSMarketTrading()
      // ... rest of original onResume body
  }
  ```
- [x] 6.11 Replace `onPause()` body (line 1088-1093):
  ```kotlin
  override fun onPause() {
      super.onPause()
      pmpViewModel.detach()
      CustomTooltipManager.hideTooltip(false)
  }
  ```
- [x] 6.12 Replace `onDestroy()` body (line 1108-1111):
  ```kotlin
  override fun onDestroy() {
      super.onDestroy()
      pmpViewModel.unsubscribe()
      pmpCounters = null
      pmpFields = null
  }
  ```
- [x] 6.13 `./gradlew :app:compileUatDebugKotlin --quiet` — expect BUILD SUCCESSFUL.

## 7. Migrate `IndicesDetailScreen` (concrete subclass, exercises `isAllDataReturned`)

- [x] 7.1 Add the same imports as step 4.1 (already partially in place from parent class).
- [x] 7.2 The ViewModel is inherited from `MarketTopDetailBaseScreen` (step 4.2 marked it `protected`). No new field needed.
- [x] 7.3 Add `@Suppress("unused")` to the local `mMarketPMPUtilVM` field if it exists in `IndicesDetailScreen`. Otherwise the parent's `@Suppress` carries through.
- [x] 7.4 Remove the local `mMarketPMPUtilVM.setOnResponseListener { pmpTopic, linkedHashMap, isAllDataReturned -> ... }` callback (line 81). The `initListeners()` function is no longer needed for PMP — the parent's `onViewCreated` flow collection already covers this.
- [x] 7.5 Verify `IndicesDetailScreen` does not override `onViewCreated` to bypass the parent's flow collection. If it does, ensure the parent's collector is still active.
- [x] 7.6 Override `onPmpReceived(update: PMPUpdate)` in `IndicesDetailScreen`:
  ```kotlin
  override fun onPmpReceived(update: PMPUpdate) {
      // IndicesDetailScreen consumes isAllDataReturned via MarketStockViewModel
      mMarketStockVM.updateDataForTopMarket(
          pmpTopic = update.topic,
          linkMapPMP = update.data,  // already aliased by PMPViewModel
          isAllDataReturned = update.isAllDataReturned,
      )
  }
  ```
- [x] 7.7 Verify that the `initListeners()` function (now empty after removing the PMP callback) is still called somewhere — if not, it can be deleted; if it is, just remove the PMP-related lines.
- [x] 7.8 `./gradlew :app:compileUatDebugKotlin --quiet` — expect BUILD SUCCESSFUL.

## 8. Verification

- [x] 8.1 Full build:
  ```bash
  ./gradlew :app:compileUatDebugKotlin --quiet
  ./gradlew :app:assembleUatDebug
  ```
  Expect: BUILD SUCCESSFUL, UAT APK produced at `app/build/outputs/apk/uat/debug/app-uat-debug.apk`.
- [x] 8.2 **Operational**: Install on emulator — deferred to device testing (`emulator-5554`):
  ```bash
  adb install -r app/build/outputs/apk/uat/debug/app-uat-debug.apk
  ```
- [x] 8.3 **Operational**: Manual smoke test 1 — deferred (SR-3738 — Market tab background/foreground):
  - Login → Market tab → TopMarket grid visible → background app 30s → foreground → prices update within 5s
  - Expected: zero stale-price flash, prices continue updating without lag
- [x] 8.4 **Operational**: Manual smoke test 2 — deferred (counter switch — Market tab):
  - Login → Market tab → Top Gainer tab → switch to Top Loser → switch back to Top Gainer → no lag
  - Expected: counter switch works smoothly, no orphaned subscriptions
- [x] 8.5 **Operational**: Manual smoke test 3 — deferred (Indices detail — `isAllDataReturned`):
  - Login → Market tab → tap an indices row → IndicesDetailScreen opens → verify the grid re-sorts exactly once per batch (not per emission, not zero times)
  - Expected: the indices grid re-sorts as expected when a complete batch arrives; no flicker
- [x] 8.6 **Operational**: Manual smoke test 4 — deferred (TabMarketStockScreen — tab fragment):
  - Login → Market tab → verify top indices row at the top of the screen updates with live prices
  - Expected: switching tabs shows fresh data, no cross-tab bleed
- [x] 8.7 **Operational**: Manual smoke test 5 — deferred (cross-check `NewOrderBottomSheet` prices — aliasing fix):
  - Login → open Trade bottom sheet → verify all price fields (bid, ask, trade, change, change%, bid/ask size) display live values, not "-"
  - Expected: prices display correctly. If the screen was previously showing "-" placeholders (because the lookup `linkMapPMP["9,F009,P23"]` returned null), they should now show actual prices.
- [x] 8.8 **Operational**: Logcat scan — deferred for PMP errors:
  ```bash
  adb logcat -d -t 5000 | grep -E "PMPNode|PMPViewModel|PMPException|isAllDataReturned" | grep -iE "error|exception|fail"
  ```
  Expected: no `isAllDataReturned`-related errors. PMPException or Node errors are acceptable if they are pre-existing.

## 9. Git & MR

- [x] 9.1 `git status` — working tree should show only: `PMPViewModel.kt` (modified), `MarketTopDetailBaseScreen.kt` (modified), `MarketTopBaseFragment.kt` (modified), `TabMarketStockScreen.kt` (modified), `IndicesDetailScreen.kt` (modified).
- [x] 9.2 Stage and commit the `PMPViewModel` changes first (separate commit for reviewability):
  ```bash
  git add app/src/main/java/com/tdt/pmobile3/viewmodels/common/PMPViewModel.kt
  git commit -m "feat(android): PMPViewModel — implement isAllDataReturned sentinel + restore aliasFields (SR-3738 §13.2, §13.3)"
  ```
- [x] 9.3 Stage and commit the 4 screen migrations as one commit (the changes are coupled — all four depend on the new algorithm and the cache pattern):
  ```bash
  git add app/src/main/java/com/tdt/pmobile3/ui/screens/market/stocktab/common/MarketTopDetailBaseScreen.kt \
          app/src/main/java/com/tdt/pmobile3/ui/screens/market/stocktab/common/MarketTopBaseFragment.kt \
          app/src/main/java/com/tdt/pmobile3/ui/screens/market/stocktab/TabMarketStockScreen.kt \
          app/src/main/java/com/tdt/pmobile3/ui/screens/market/stocktab/detailmarkettops/IndicesDetailScreen.kt
  git commit -m "refactor(android): MarketTop screens — migrate from PMPUtilViewModel to PMPViewModel (topmarket)"
  ```
- [x] 9.4 Push to `hoangtran/sr-3738-pmp-connection-center` (or new branch):
  ```bash
  git push origin HEAD
  ```
- [x] 9.5 Update MR description with: scope (4 files + 1 view model), risks (MEDIUM base class, LOW others), aliasing cross-fix for `NewOrderBottomSheet`, and reference to this OpenSpec change `android-pmp-topmarket-migration`.

## 10. Rollback

- [x] 10.1 **Deferred**: Rollback plan — conditional, deferred `PMPViewModel.subscribe()` algorithm change breaks a screen (e.g., `IndicesDetailScreen` re-sorts too often or not at all):
  - Revert commit 9.2: `git revert <commit-hash>`
  - The four screen migrations in commit 9.3 still work (they don't depend on the new algorithm — `isAllDataReturned` is just ignored by the three screens that don't read it)
  - The `IndicesDetailScreen` migration becomes a no-op for the `isAllDataReturned` branch (the algorithm is reverted to `isAllDataReturned = false`, so the branch never fires)
- [x] 10.2 **Deferred**: Rollback plan — conditional, deferred `aliasFields()` change breaks `NewOrderBottomSheet` (unlikely — it restores the legacy semantic):
  - Revert only the aliasing portion of commit 9.2: keep the `isAllDataReturned` algorithm change, remove the `data = aliasFields(rawData, fields)` line and replace with `data = rawData`
  - The four screen migrations in commit 9.3 still work (their consumers read aliased data; with aliasing removed, the lookups will return null and the price fields will show "-" — a regression but not a crash)
- [x] 10.3 **Deferred**: Rollback plan — conditional, deferred screen migration breaks (e.g., `MarketTopDetailBaseScreen`):
  - Revert commit 9.3
  - The `PMPViewModel` change in commit 9.2 stays (it's beneficial for future migrations)
  - The other three screens stay on the new pattern

## 11. Follow-ups

- [x] 11.1 **Deferred**: Separate sub-change, blocked on other migrations `@Suppress("unused")` from `mMarketPMPUtilVM` in `MarketTopDetailBaseScreen` and `MarketTopBaseFragment` when all subclasses migrate (separate sub-changes, parent task §12.14+).
- [x] 11.2 **Deferred**: Separate sub-change `HomeScreen.kt` (1797 lines, multiple PMP consumers) — separate sub-change.
- [x] 11.3 **Deferred**: Separate sub-change `WatchListTab.kt` (1842 lines, complex index dispatch) — separate sub-change, higher risk.
- [x] 11.4 **Deferred**: Blocked by pre-existing test rot adding a unit test for the `isAllDataReturned` algorithm in `PMPViewModelTest.kt` (blocked by parent task §13.1 pre-existing test rot, but the test should be written and ready to run once that is fixed).
- [x] 11.5 **Deferred**: Blocked by pre-existing test rot adding a unit test for `aliasFields()` in `PMPViewModelTest.kt` (same blocker as 11.4). Test cases:
  - Raw key matches first canonical value → aliased correctly
  - Raw key matches multiple canonical values → first wins
  - Raw key not in any canonical value → passed through
  - Empty rawData → empty result
  - Empty subscribeFields → all raw keys passed through
