# Meet lucebox: a local AI inference engine optimized for consumer hardware

*May 2026 · by [Davide Ciffa](https://x.com/davideciffa) and [Erik LaBianca](https://x.com/easel)*

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

## Requirements

lucebox runs as a Docker container with GPU passthrough, so the host needs four
things:

- Linux with an NVIDIA GPU, sm_75 or newer (see the coverage table below). 24 GB
  of VRAM comfortably fits the default Qwen3.6-27B at Q4_K_M.
- The NVIDIA proprietary driver, 525 or newer (CUDA 12).
- Docker Engine.
- The NVIDIA Container Toolkit, so `docker run --gpus all` reaches the card.

The driver is a host kernel component you install once. Docker and the NVIDIA
Container Toolkit are the two pieces `lucebox check` verifies. On Ubuntu 24.04
this script installs both (we ran it in a clean 24.04 container to confirm the
repos, keys, and package names are current):

```bash
#!/usr/bin/env bash
# lucebox prerequisites on Ubuntu 24.04: Docker Engine + the NVIDIA Container
# Toolkit. The NVIDIA driver is a host kernel component and is checked, not
# installed, at the end.
set -euo pipefail
export DEBIAN_FRONTEND=noninteractive
SUDO=""; [ "$(id -u)" -ne 0 ] && SUDO="sudo"
. /etc/os-release
[ "${ID:-}" = "ubuntu" ] || echo "warning: tuned for Ubuntu; found '${ID:-unknown}'." >&2

# Docker Engine apt repo
$SUDO apt-get update -qq
$SUDO apt-get install -y -qq ca-certificates curl gnupg
$SUDO install -m 0755 -d /etc/apt/keyrings
$SUDO curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
$SUDO chmod a+r /etc/apt/keyrings/docker.asc
echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu ${VERSION_CODENAME} stable" \
  | $SUDO tee /etc/apt/sources.list.d/docker.list >/dev/null

# NVIDIA Container Toolkit apt repo
curl -fsSL https://nvidia.github.io/libnvidia-container/gpgkey \
  | $SUDO gpg --batch --yes --dearmor -o /usr/share/keyrings/nvidia-container-toolkit-keyring.gpg
curl -fsSL https://nvidia.github.io/libnvidia-container/stable/deb/nvidia-container-toolkit.list \
  | sed 's#deb https://#deb [signed-by=/usr/share/keyrings/nvidia-container-toolkit-keyring.gpg] https://#g' \
  | $SUDO tee /etc/apt/sources.list.d/nvidia-container-toolkit.list >/dev/null

# install both
$SUDO apt-get update -qq
$SUDO apt-get install -y -qq \
  docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin \
  nvidia-container-toolkit

# wire the NVIDIA runtime into Docker
if command -v systemctl >/dev/null 2>&1 && [ -d /run/systemd/system ]; then
  $SUDO nvidia-ctk runtime configure --runtime=docker
  $SUDO systemctl restart docker
fi

# the driver is separate; check for it
command -v nvidia-smi >/dev/null \
  || echo "no NVIDIA driver found: run 'sudo ubuntu-drivers install' (>= 525 for CUDA 12), then reboot" >&2
```

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
[INFO]  Resolved draft → models/draft/dflash-draft-3.6-q4_k_m.gguf
[backend_factory] detected arch=qwen35
ggml_cuda_init: found 1 CUDA devices (Total VRAM: 24462 MiB):
  Device 0: NVIDIA GeForce RTX 5090 Laptop GPU, compute capability 12.0, VRAM: 24462 MiB
[model_card] probing sidecar: share/model_cards/qwen3.6-27b.json (from general.name='Qwen3.6-27B')

[server] ╭─── Configuration ───────────────────────────────────╮
[server] │  model           = models/Qwen3.6-27B-Q4_K_M.gguf
[server] │  draft           = models/draft/dflash-draft-3.6-q4_k_m.gguf
[server] │  max_ctx         = 65536
[server] │  model_card      = share/model_cards/qwen3.6-27b.json
[server] │  max_tokens      = 32768
[server] │  think_max_tokens= 15488
[server] │  hard_limit_reply= 4096
[server] │  effort tiers    = low=4032 medium=16128 high=32256 x-high=56832 max=61440
[server] │  ddtree_budget   = 16
[server] │  prefix_cache    = 0 slots
[server] │  cache_type_k/v  = tq3_0 (auto)
[server] │  pflash          = off
[server] │  lazy_draft      = off
[server] ╰─────────────────────────────────────────────────────╯
[server] level-2 force-close (sidecar-hint, 116 chars → 24 tokens, hard_limit_reply_budget = 4096)
[server] listening on http://0.0.0.0:8080
```

The banner is the resolved config: the target and DFlash draft it loaded, the
model card it matched by `general.name`, the budget envelope and effort tiers,
the KV cache types, and the level-2 force-close it built from the card's
terminator hint (covered in
[Putting Qwen's thinking on a budget](<Putting Qwen's thinking on a budget — counting tokens and forcing the close.md>)).
The same picture is available over HTTP from
[`/props`](<What props tells you about a lucebox server.md>).

Then point any OpenAI client at it:

```bash
curl http://localhost:8080/v1/models
```

To run it as a background service instead of foreground, install the user
systemd unit:

```text
❯ lucebox install
[OK]    Installed /home/erik/.config/systemd/user/lucebox.service
[WARN]  Linger is off for erik — the service will stop when you log out
        To enable (requires sudo): sudo loginctl enable-linger "erik"

Next:
         lucebox start            # start now
         lucebox enable           # start at every login
         lucebox logs             # follow the journal
```

The linger warning matters for a headless box: without `enable-linger`, a
user service is torn down when you log out, so a server you meant to leave
running stops with your session. `lucebox enable` plus linger is the
set-and-forget combination.
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
- What /props tells you about a lucebox server
- How lucebox auto-tunes itself to your GPU
- Model cards in lucebox: a typed sidecar for what the server actually needs
- Sampling parameters on a lucebox model card: what the knobs mean
- Multi-turn agentic loops as a benchmark target: what they look like, why they matter, what we've measured
