---
name: ai-features
description: "Patterns for building product features that call external AI APIs — OpenAI (chat, embeddings), Whisper / speech-to-text, ElevenLabs / text-to-speech, vision. Use whenever you add, integrate, or call one of these to transcribe, summarize, generate, embed, classify, or synthesize — and ESPECIALLY when the input or the output may be larger than the model's context window or the endpoint's size limit. Covers measuring payloads, the two ways to make oversized work fit (split-and-combine vs. reduce-input), per-provider limits, and engineering the calls."
---

# Building features with AI APIs

Every call to an external AI model runs against **hard capacity limits**: a maximum
input/context size, a maximum output size, and for media a maximum file size or
duration. The input *or* the output can be bigger than the model can handle. Plan for
that from the start — don't discover it at runtime with a `400`.

## Measure, then fit — the rule for every call

1. **Know the limit for the exact model/endpoint you call** — context window in tokens,
   max output tokens, max upload size or audio duration, max characters for TTS. Limits
   differ per model and change over time. Look them up for the model you actually use;
   don't assume.
2. **Measure the payload before you send it** — count tokens (e.g. `tiktoken` for OpenAI
   models), measure audio duration / file size, count characters for TTS.
3. **Leave headroom.** For chat models the input and output share one window, and you
   must reserve room for the output plus your instructions. Never fill the window to 100%.
4. If it fits with margin → call directly. If it doesn't → apply one of the two
   strategies below.

## When it doesn't fit: two strategies

### Strategy 1 — Split and combine (PREFERRED for most cases)

Break the work into parts that each fit, process the parts (in parallel where safe), then
combine the partial results into the final output — map/reduce. **Prefer this**, because
it keeps the entire input: nothing is thrown away.

- **Split on natural boundaries, never mid-unit** — paragraphs / sections / sentences for
  text, silence or scene boundaries for audio, whole records for data. Cutting mid-unit
  corrupts meaning at the seams.
- **Size chunks well under the limit** and reserve room for the output and per-chunk
  instructions/overhead.
- **Add overlap** between chunks when a chunk needs its neighbours to be understood
  (sliding window) so context isn't lost at the boundaries.
- **The combine step can overflow too.** Merging the partial results may itself exceed the
  window — then reduce recursively: combine in batches, then combine the combinations.
- **Track parts individually.** Key each part by index so you can retry a single failed
  part instead of redoing the whole job, and only declare success once *all* parts finished.
- **Output too big?** When the *output* is the constraint (max output tokens), split the
  generation task — produce the result section by section, paginate, or stream — and
  assemble the pieces.

### Strategy 2 — Reduce the input

Shrink what you send so a single call fits: retrieve and send only the relevant portion
(RAG), filter/dedupe, pre-summarise, drop low-value content, or downsample/compress media.

Use this when **splitting would break global coherence** (the model must see everything at
once to answer), when **most of the input is irrelevant** to the task, or when the latency
and cost of many calls is unacceptable. The tradeoff is that you lose information — guard
against dropping something that mattered.

### Choosing — and when to ask

Default to **Strategy 1** for most cases; it preserves the full input. Reach for
**Strategy 2** only when the task genuinely needs the whole input in one call, or when most
of the input is noise. **If the right strategy isn't clear for the specific feature, ask
before committing** — the wrong choice is expensive to unwind after the code is built.

## Per-provider gotchas

- **OpenAI chat / embeddings.** Input + output count against one window, with a *separate*
  max-output-tokens cap — reserve output room. Count tokens with `tiktoken` before sending.
  Embeddings have a per-input token cap and a per-request batch cap; chunk long documents
  and store one vector per chunk (this is Strategy 1 for RAG). Use JSON / structured
  outputs and **validate the parsed result** — never trust the shape blindly.
- **Whisper / speech-to-text.** Hard upload-size limit (currently ~25 MB on OpenAI's
  endpoint — verify the current value) plus practical duration limits. For long audio,
  split **on silence** so you never cut a word, transcribe each segment, then concatenate
  the transcripts; carry a little tail context if continuity matters. Downsampling to mono
  / lower bitrate is the Strategy-2 lever to get under the size cap. Naive fixed-time
  slicing cuts words in half — always prefer silence-based boundaries.
- **Text-to-speech (ElevenLabs / OpenAI TTS).** Per-request character limits. Split long
  text on sentence/paragraph punctuation, synthesise each chunk, then stitch the audio.
  For prosody continuity across chunks pass the neighbouring text as context (e.g.
  ElevenLabs `previous_text` / `next_text`) and keep the same voice and settings so the
  seams aren't audible. Splitting mid-sentence produces unnatural pauses.

## Engineering the calls

- **Run AI calls in background jobs.** They're slow, external, and rate-limited — don't
  block a web request on one. Enqueue and report progress; model each split part as its own
  unit of work with its own retry. (See `async-jobs` for job design.)
- **Handle rate limits and transient failures** with retry + exponential backoff.
  Parallelise split parts *within* the provider's rate limit, not beyond it.
- **Make it idempotent.** A retried chunk must not double-produce — key partial results by
  `(job, chunk index)` so a re-run overwrites rather than appends.
- **Budget cost and latency deliberately.** More chunks = more calls = more cost and
  latency. Cache results (and use prompt caching where the provider offers it), and pick a
  chunk size that balances "fits" against "how many calls".
- **Treat model output as untrusted.** Validate its structure, handle refusals and empty
  responses, set an explicit max-output-tokens, and never drop raw output into a shell,
  SQL, or HTML without the usual safeguards.
- **Keep API keys in config/secrets**, never hardcoded.
- **Test without hitting the live API.** Mock the provider client and assert on *your*
  chunking/combining logic — boundary selection, overlap, reassembly order, single-part
  retry. That's where the bugs live. Test behaviour ("a 3×-over-limit input yields ≥3 parts
  that reassemble in order"), not exact model strings.
