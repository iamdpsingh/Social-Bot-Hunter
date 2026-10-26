# ADR-0005: Store content fingerprints, never raw text

**Status:** accepted

**Context.** Repeated-content and timing signals need to compare posts. Keeping post text is a privacy
and legal liability and is not necessary for those signals.

**Decision.** On import, text becomes (a) a SHA-256 of normalised text, (b) a 64-bit SimHash over
3-word shingles with URLs and mentions replaced by placeholders, and (c) a length. The text is then
discarded. Quarantined rows replace `text` with a length marker. Tests assert that distinctive post
text appears nowhere in the database or in logs.

**Alternatives.** Store text behind access control. Deferred until there is a reviewed need.

**Consequences.** Duplicate detection is limited to what the fingerprints can express (documented in
the methodology). Analysts cannot read the posts from this system; they must go to the source. If
text is ever stored, it needs a legal basis, a retention rule, and an ADR of its own.
