# AstrBot #11284 review evidence

These unedited screenshots were captured from the actual dashboard artifact built by [run 44718383887](https://github.com/AstrBotDevs/AstrBot/actions/runs/44718383887), whose PR head is `eed3ef5f64ff4d9b10958165b04f1000f58f43df`, with the matching AstrBot backend and a fresh isolated configuration.

The provider points to a local HTTP protocol stub at `127.0.0.1:16186`. The fake model ID, placeholder key, configuration and chat prompts are synthetic. **No live model service was called; the success response is canned.**

- `cache-on-zh.jpg`: automatic prompt caching enabled (the default).
- `cache-off-zh.jpg`: automatic prompt caching disabled and saved.
- `cache-on-rejected.jpg`: actual ChatUI error when the local stub rejects the automatic cache marker.

The UI was used to create the provider, fetch and enable its test model, send a prompt, disable and save caching, and send a second prompt. Real Anthropic SDK requests reached the local stub. The attached request metadata records HTTP 400 with `cache_control` present in both non-streaming and streaming requests, followed by HTTP 200 with no `cache_control` in both modes after the option was disabled. ChatUI displayed the canned response for the second prompt.

The request log contains only time, local path, mode, cache-marker presence and HTTP status; no prompt, key or authentication header is recorded. The standalone stub source is included so its behavior can be inspected and reproduced. This evidence verifies local protocol handling and the UI workflow; it does not establish compatibility with an online Anthropic service or gateway.

AI assistance: Codex performed this setup, browser interaction and validation. No human review is asserted.
