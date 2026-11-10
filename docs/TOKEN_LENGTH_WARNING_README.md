# Understanding the token-length warning

This note explains the warning:

```text
Token indices sequence length is longer than the specified maximum sequence length
for this model (736 > 384). Running this sequence through the model will result
in indexing errors
```

## What it means

`736` is a token count, not a character or word count. The recommendation assessor
uses the `all-mpnet-base-v2` Sentence-Transformers model, whose configured maximum
sequence length in this project is 384 tokens.

In `backend/services/recommendation_pipeline.py`, long text is first converted to
token IDs and then split into chunks that fit the model. The warning was raised
during that initial full-text tokenization, before chunking. It made the situation
sound more dangerous than it was: that 736-token sequence was not itself passed
through MPNet. The resulting chunks were the model inputs.

The warning is still worth addressing because it obscures real overlength model
inputs. It is not safe to interpret every occurrence as harmless without checking
which code path produced it.

## The fix in this project

The assessor now passes `verbose=False` for its intentional full-text tokenization
step, suppressing the tokenizer's warning for that call only. The tokenizer still
produces the complete token-ID sequence. The assessor then splits the IDs into
chunks sized to fit the configured model limit, accounting for special tokens,
and embeds those chunks separately.

This keeps the full text available to the recommendation assessment; it does not
raise the model's 384-token limit or simply discard everything after token 384.
A regression test checks that long input produces multiple chunks and that their
combined content retains all input tokens.

## The two model paths are different

- **Recommendation assessment:** uses `all-mpnet-base-v2` with a 384-token limit.
  Long assessment text is split into model-sized chunks.
- **SDG classification:** uses the LUKE tokenizer with a 512-token limit.
  `backend/services/inference.py` sets `MAX_LENGTH = 512` and requests
  `truncation=True`, so text beyond that limit is truncated for this classifier.

Do not increase a model's maximum length just to suppress a warning. A model's
configured limit is not arbitrary, and sending a longer sequence may fail or
change behavior. Likewise, truncation is not a substitute for chunking when the
goal is to assess all of a long document.

## Validation

From the repository root, run the focused regression suite:

```powershell
pytest backend/tests/test_recommendation_pipeline.py
```
