## ADDED Requirements

### Requirement: Canonical eFootball 2026 playing-style list

The content SHALL cover the canonical set of the 22 position-activated eFootball
2026 Playing Styles, each mapped to the pitch zone it belongs to: Forwards,
Midfield creators, Midfield engines, Wingers, Defenders, Full-backs, and
Goalkeepers. No style in the canonical list MAY be silently omitted from the deck.
The authoritative list and per-style position activations are recorded in the
change's `data-reference.md`.

#### Scenario: All styles represented

- **WHEN** the deck content is assembled
- **THEN** all 22 position-activated styles from the canonical eFootball 2026 list appear on a slide, grouped under their pitch zone

#### Scenario: Zone grouping

- **WHEN** a style is presented
- **THEN** it is placed under exactly one pitch-zone grouping consistent with its primary activatable position

### Requirement: AI Playing Styles distinguished from position styles

The content SHALL acknowledge that eFootball 2026 defines a separate category of
7 AI Playing Styles (Trickster, Mazing Run, Speeding Bullet, Incisive Run, Long
Ball Expert, Early Crosser, Long Ranger) that govern on-the-ball AI behavior and
are distinct from the 22 position-activated Playing Styles. The deck MUST NOT
conflate the two categories.

#### Scenario: Categories kept distinct

- **WHEN** the deck references AI Playing Styles
- **THEN** they are presented as a separate category from the position-activated Playing Styles, not mixed into the same canonical count

### Requirement: Six-bucket stat taxonomy

The content SHALL define a six-bucket stat taxonomy — Attacking, Technique,
Passing, Defending, Physical, and Aerial — that maps eFootball 2026 outfield
attributes into groups. Every outfield playing style's key stats MUST be
expressible as an emphasis across these six buckets. Goalkeeper styles are the
explicit exception: their GK-specific attributes (GK Awareness, GK Catching, GK
Parrying, GK Reflexes, GK Reach) do not map to the six outfield buckets and SHALL
be presented via a dedicated GK stat grouping. The attribute-to-bucket mapping is
recorded in the change's `data-reference.md`.

#### Scenario: Buckets introduced before use

- **WHEN** the audience first encounters a stat dial
- **THEN** the six buckets have already been defined on an earlier "decoder" slide

#### Scenario: Style stats map to buckets

- **WHEN** an outfield style's key stats are shown
- **THEN** each listed stat belongs to one of the six defined buckets

#### Scenario: Goalkeeper stats use GK grouping

- **WHEN** a goalkeeper style is presented
- **THEN** its stats are shown via the dedicated GK grouping rather than forced into the six outfield buckets

### Requirement: Per-style activation and key stats

Each playing style entry SHALL specify its activatable position(s) as defined by
eFootball 2026 and the key attributes that most drive that style's behavior.

#### Scenario: Position activation stated

- **WHEN** a style is presented
- **THEN** its compatible/activatable position(s) (e.g., Goal Poacher → CF) are stated

#### Scenario: Key stats stated

- **WHEN** a style is presented
- **THEN** the two-to-four attributes most important to that style are listed

### Requirement: Famous-player exemplars spanning eras

Each playing style SHALL be illustrated with at least one famous-player exemplar,
and the exemplar set across the deck MUST include both modern and historical
players to aid recall. Player numeric stats, if shown, MUST be illustrative unless
an explicit source is cited.

#### Scenario: Exemplar per style

- **WHEN** a style slide is shown
- **THEN** it names at least one well-known player who exemplifies that style

#### Scenario: Modern and historical coverage

- **WHEN** the full deck is reviewed
- **THEN** the exemplar set includes both contemporary players and players from earlier eras

#### Scenario: Illustrative stats disclaimed

- **WHEN** a specific numeric player stat is displayed without a cited source
- **THEN** it is presented as illustrative rather than as an authoritative in-game value

### Requirement: Rights-safe player imagery

Each famous-player exemplar SHALL be illustrated with a real player photograph
that is sourced only from rights-safe licenses: Wikimedia Commons images under
CC-BY, CC-BY-SA, CC0, or public domain. Copyrighted press/agency photographs
(e.g. Getty, AP, Reuters) MUST NOT be embedded. The image source URL, license,
and author for every embedded photo SHALL be recorded in the change's
`data-reference.md`.

#### Scenario: Only rights-safe licenses embedded

- **WHEN** a player photo is embedded in the deck
- **THEN** its license is one of CC-BY, CC-BY-SA, CC0, or public domain, and never a copyrighted all-rights-reserved image

#### Scenario: Image provenance recorded

- **WHEN** a photo is embedded for an exemplar
- **THEN** its source URL, license short-name, and author are recorded in `data-reference.md`

### Requirement: Deterministic fallback for missing photos

Because a rights-safe photo does not exist for every exemplar, the deck SHALL
provide a deterministic generated placeholder (derived from the player's name) for
any exemplar lacking a rights-safe image, so that no exemplar slot is ever blank
or shows a broken image. The fallback MUST render offline with no network access.

#### Scenario: Exemplar without a rights-safe photo

- **WHEN** an exemplar has no available CC-BY/CC-BY-SA/CC0/public-domain photo
- **THEN** a deterministic name-derived placeholder is shown in its place, not a blank space or broken-image icon

#### Scenario: Fallback is offline-safe

- **WHEN** the deck is opened with no network connection
- **THEN** every exemplar shows either its embedded photo or its generated placeholder, with no outbound image requests

### Requirement: Photo attribution

Embedded CC-BY and CC-BY-SA photos require visible credit. The deck SHALL include
a credits/attribution region (a dedicated slide and/or per-image credit) that
lists, for every embedded photo, the author and license.

#### Scenario: Attribution present for embedded photos

- **WHEN** the deck embeds one or more CC-BY / CC-BY-SA photos
- **THEN** an in-deck credits area lists each such photo's author and license name

### Requirement: Chemistry and sample XI

The content SHALL include a section explaining how styles combine (complementary
vs. clashing pairings) and a sample starting XI assembled purely from playing
styles to demonstrate the framework end to end.

#### Scenario: Chemistry guidance present

- **WHEN** the audience reaches the "putting it together" act
- **THEN** at least one slide explains which styles complement or conflict with each other

#### Scenario: Sample XI present

- **WHEN** the audience reaches the "putting it together" act
- **THEN** a sample XI is shown mapping each of the 11 positions to a chosen playing style

### Requirement: Real per-exemplar key attributes in the peek panel

The peek panel for an exemplar SHALL display that player's real eFootball 2026 key
attributes. To keep the numbers readable and aligned with the teaching model, the
panel SHALL show one representative attribute per stat bucket for outfield players
(Attacking → Finishing, Technique → Dribbling, Passing → Low Pass, Defending →
Defensive Awareness, Physical → Speed, Aerial → Heading) and the GK-specific
attributes for goalkeepers. The real attributes SHALL be shown alongside the
style's illustrative 0–5 dial, not as a replacement for it. The attribute-to-source
mapping and every player's captured values are recorded in the change's
`data-reference.md`.

#### Scenario: Representative attributes shown per bucket

- **WHEN** an outfield exemplar's peek panel is opened
- **THEN** it lists one real attribute value for each of the six buckets, paired with the style's 0–5 dial

#### Scenario: Goalkeeper peek uses GK attributes

- **WHEN** a goalkeeper exemplar's peek panel is opened
- **THEN** it shows the GK-specific attributes rather than the six outfield representative attributes

### Requirement: Real stats are pinned, dated, and sourced

Because community stat values change across game patches, every real attribute
shown SHALL be captured once at authoring time as a pinned snapshot, stamped with
the fetch date, and attributed to its source. The card version used for each player
SHALL be identified so a peak/special-card rating is never presented as a neutral
base rating. Modern players SHALL use their base/current card; retired legends
(who have no base card) SHALL use their special/Epic card, labelled as such.

#### Scenario: Fetch date shown

- **WHEN** a peek panel displays real attribute values
- **THEN** it shows the date the values were captured (e.g. "stats as of Jul 2026") rather than implying a live feed

#### Scenario: Source attributed

- **WHEN** a peek panel displays real attribute values
- **THEN** the source of those values is credited on the panel

#### Scenario: Card version labelled

- **WHEN** a peek panel shows a player whose values come from a special/Epic card rather than a base card
- **THEN** the card type is labelled so the rating is not mistaken for a neutral base rating
