# Meet lucebox: a local AI inference engine optimized for consumer hardware

*May 2026 · by Davide Ciffa and Erik LaBianca*

lucebox is a local AI inference engine optimized for consumer hardware. It's what
produced the Gemma and DeepSeek numbers in our other posts: custom kernels and
DFlash speculative prefill and decode, tuned per model family and GPU. This post
is about getting it running, which on lucebox means a prebuilt Docker image and a
thin wrapper, with no CUDA toolchain, `cmake`, or Python environment on your host.

The names rhyme, so to be clear: lucebox is the project and Docker image,
luce-dflash is the server daemon inside it, DFlash is the speculative-decode
technique it uses, and luce-bench is the separate benchmark harness.

> [Hero image: docker pull → lucebox serve → an OpenAI-compatible endpoint]

## TL;DR

- Prebuilt image, no compiling. `ghcr.io/Luce-Org/lucebox-hub:cuda12` covers
  CUDA-12 NVIDIA GPUs from the RTX 2080 Ti (sm_75) to the RTX 5090 and 5090
  Laptop (sm_120). Building from source is a separate path you don't need.
- One thin host wrapper. `lucebox` is ~80 lines of bash whose only host deps are
  `docker` and `nvidia-smi`. Config, autotune, benchmarks, and model download are
  a typed Python CLI inside the image.
- Zero to an endpoint in five commands, with a VRAM-tiered autotune so the
  defaults already fit your card.
- OpenAI-compatible. Point any client at `http://localhost:8080/v1`.
- Escape hatches. `lucebox print-run` prints the exact `docker run`, or skip the
  wrapper and run the container yourself.

## Getting started

**Install the wrapper.** One file, no dependencies beyond `docker` and
`nvidia-smi`:

```bash
curl -fsSL https://raw.githubusercontent.com/Luce-Org/lucebox-hub/main/lucebox.sh \
     -o ~/.local/bin/lucebox && chmod +x ~/.local/bin/lucebox
```

**Check your hardware.** `lucebox check` probes the driver, Docker, the NVIDIA
Container Toolkit, your GPU, and systemd, and tells you whether the image covers
your card:

```text
❯ lucebox check
[lucebox] host readiness report
  docker daemon          ✓  reachable (server 29.1.3)
  nvidia ctk             ✓  wired into docker (runtime)
  nvidia driver          ✓  596.36 (≥ 525 required for cuda12)
  gpu                    ✓  NVIDIA GeForce RTX 5090 Laptop GPU × 1 (sm_120, 23 GB VRAM)
  cuda12 arch            ✓  sm_120 covered by image
  user systemd           ✓  available (needed for 'lucebox install')
  image                  ✓  ghcr.io/Luce-Org/lucebox-hub:cuda12
  host                   ✓  24 cpus, 31 GB RAM
```

**Configure.** `lucebox configure` pulls the image and writes VRAM-tiered
defaults to `~/.lucebox/config.toml`:

```text
❯ lucebox configure
cuda12: Pulling from Luce-Org/lucebox-hub
  …
Status: Downloaded newer image for ghcr.io/Luce-Org/lucebox-hub:cuda12
Wrote /home/erik/.lucebox/config.toml
  variant     cuda12
  image       ghcr.io/Luce-Org/lucebox-hub:cuda12
  models      /home/erik/.local/share/lucebox/models
  budget      16
  max_ctx     65536
  lazy_draft  True
```

**Download models.** The default target is Qwen3.6-27B (Q4_K_M) plus its DFlash
draft, fetched through the container so you don't need `huggingface-cli` on the
host:

```text
❯ lucebox download-models
Models dir: /home/erik/.local/share/lucebox/models
  target (unsloth/Qwen3.6-27B-GGUF/Qwen3.6-27B-Q4_K_M.gguf):  will download
  draft  (spiritbuun/Qwen3.6-27B-DFlash-GGUF/dflash-draft-3.6-q4_k_m.gguf): will download
Downloading (~17 GB total)…
Qwen3.6-27B-Q4_K_M.gguf        ━━━━━━━━━━━━━━━━━━━━━━━ 16.8/16.8 GB
dflash-draft-3.6-q4_k_m.gguf   ━━━━━━━━━━━━━━━━━━━━━━━  1.0/1.0 GB
Done.
```

**Serve.** Foreground with `lucebox serve`; it auto-detects the target and
autotunes for the model family:

```text
❯ lucebox serve
[INFO]  Starting lucebox server (variant=cuda12, from config.toml)
[INFO]  Auto-detected target: Qwen3.6-27B-Q4_K_M.gguf
[INFO]  Autotune: DFLASH27B_DRAFT_SWA=2048 (Qwen3.6 draft SWA)
```

Then point any OpenAI client at it:

```bash
curl http://localhost:8080/v1/models
```

To run it as a background service instead of foreground, use systemd:
`lucebox install` writes `~/.config/systemd/user/lucebox.service`, then
`lucebox start` / `status` / `logs`.
## Hardware coverage

| GPU                        | sm  | `:cuda12` |
| -------------------------- | --- | :-------: |
| RTX 2080 Ti                | 75  |     ✓     |
| A100                       | 80  |     ✓     |
| RTX 3090 / A40 / A10       | 86  |     ✓     |
| RTX 4090 / L40             | 89  |     ✓     |
| H100                       | 90  |     ✓     |
| RTX 5090 / RTX 5090 Laptop | 120 |     ✓     |

Pre-Turing GPUs (Pascal, Volta) aren't supported; DFlash's kernels assume sm_75+
with no fallback below.

## Tuning, when you want it

`lucebox configure` gets you sensible VRAM-tiered defaults immediately. For more,
`lucebox benchmark` runs an autotuner organized as escalating profiles (`level1`
through `level3`) that sweep `DFLASH_MAX_CTX × DFLASH_BUDGET` and related
tunables, then gate on capability and agentic-tool-call validation before
persisting the winners back into `config.toml`. You can attach validation suites,
including the same `ds4-eval` set from
[our benchmark posts](<Running the benchmarks — an intro to luce-bench.md>), with
`--extra-suites`.

Everything is also overridable per run via `-e DFLASH_*` on `docker run`
(context, tree budget, KV cache types, pFlash prefill, target/draft paths); see
the config table in the [repo README](https://github.com/Luce-Org/lucebox-hub).

---

*Image: `ghcr.io/Luce-Org/lucebox-hub:cuda12`. Wrapper + CLI:
[github.com/Luce-Org/lucebox-hub](https://github.com/Luce-Org/lucebox-hub)
(Apache-2.0).*

**Related**
- Running the benchmarks: an intro to luce-bench
- Gemma 4 26B edges out DeepSeek V4 Flash (284B), at 5x the speed
- Gemma 4 26B across serving paths: a laptop GPU, a 3090 Ti, MLX, and OpenRouter
- Think vs nothink on Gemma 4: same accuracy, 10x the latency
- Every model we've run on ds4-eval-92
- Putting Qwen's thinking on a budget: counting tokens and forcing the close
- Qwen3.6 think vs nothink across providers: thinking helps, if you budget for it
