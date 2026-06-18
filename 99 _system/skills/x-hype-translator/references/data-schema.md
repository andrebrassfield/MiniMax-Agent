# Data Schema — x-hype-translator

The raw capability extraction the chief (Mavis) builds from the
top 1-3 source posts BEFORE dispatching the Scribe. The Scribe
doesn't see x.com directly — it gets the chief's extraction as
task-spec input.

## Per-source-post fields

For each of the top 1-3 source posts:

| Field | Type | Required |
|---|---|---|
| `tool_name` | string | yes |
| `tool_slug` | string (kebab-case) | yes — used in filename |
| `capability_one_liner` | string | yes — what the tool does, in one sentence |
| `source_url` | string | yes |
| `source_handle` | string | yes |
| `source_post_text` | string | yes — full post text |
| `source_engagement` | object | yes — `{replies, reposts, likes, views}` |
| `launch_context` | string | yes — "just released" / "preview" / "available now" |
| `captured_at` | ISO timestamp | yes |

## The "capability_one_liner" discipline

The one-sentence description is the load-bearing input to the Scribe.
It must:
- Be in the source post's own words (paraphrase if needed, but stay
  anchored to what the post actually said)
- Be specific (not "AI tool" but "real-time voice agent that handles
  post-call CRM notes across 50 calls a day")
- Be falsifiable (the Scribe's 4-step implementation must follow
  from this sentence, not from invented features)

If the source post is vague, mark `capability_one_liner` as `unclear`
and let the Scribe flag the gap. Do NOT invent a capability to fill
the field.

## The "source_post_text" discipline

Capture the full post text verbatim, including any quoted tweets.
The Scribe may need to reference a specific claim in the post.

If the post is a thread, capture the first tweet + summary of the
thread. The Scribe gets the load-bearing claim, not a paraphrased
summary.
