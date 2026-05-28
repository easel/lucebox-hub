# The agentic stack is the product, not the model

I spent a while thinking the model was the thing. Swap in a better model, get a better agent. After enough time staring at agent traces and serving configs, that stopped feeling true. A working coding agent is a stack of layers, and the quality you observe at the top is the product of every layer underneath, not the model in isolation. The best public agents seem to understand this and build accordingly. This post is the version of that argument I'd want to have read a year ago: what the layers are, why owning them together is an advantage, and where a local open-weights stack like lucebox actually sits in that picture.

This is a thinking piece more than a results piece. The numbers that ground it live in the other posts; I'll point at them.

## The stack, top to bottom

It helps to name the layers, because the usual conversation collapses all of them into "the model" and then argues about benchmarks. Roughly from the top of the loop down to the silicon:

1. Context. Deciding what work to do and assembling the right material for it: which files, what history, how the task is framed.
2. Guardrails. How you know the work was done correctly. Tests, type checks, a way to verify the change against something other than the model's own opinion of it.
3. Implementation. The change itself, the actual thing being built.
4. Self-discovery. The agent has to run things and check them, so it can correct its own output. This is where the loop closes on itself.
5. The harness. System prompts, the built-in tool set, the ability to extend that tool set, sandboxing, model selection, tuning, and routing.
6. The inference engine. Prompt caching, KV cache, prefix cache, prefill optimizations.
7. The model. Reasoning, streaming, prefill and decode performance, the pretraining corpus, and the reinforcement learning applied on top of it.

Listed out, it reads like seven separate concerns owned by seven separate teams. The interesting claim is that they aren't separable, and the agents that feel good to use are the ones where the seams between these layers were designed away.

Walk it from the top. Context is the part everyone now agrees matters, and it's mostly above the model: what the harness chooses to put in the prompt, in what order, with what framing, decides whether the model is even working on the right problem. Guardrails are how the work gets checked. A model that writes a plausible patch and a harness that runs the test suite are two very different products even with the same weights, because one of them can tell when it's wrong. Implementation is the patch. Self-discovery is the loop where the agent runs the tests, reads the failure, and tries again; this only works if the layers below can actually execute the tool calls and stream the results back fast enough that iterating is cheap. The harness is the glue: the prompts, the tools, the sandbox, the routing between models. The inference engine is what turns those prompts into tokens, and it's where caching lives. The model is the reasoning core at the bottom.

The reason output quality is a product and not a sum: a weak link anywhere shows up as a worse agent everywhere. A great model behind a harness that assembles bad context produces confident wrong patches. A great harness in front of an engine that re-prefills the whole conversation every turn produces an agent that's correct but too slow to iterate, which means in practice it iterates less, which means it's less correct. The multi-turn loop is where this compounds, and it's exactly the regime we tried to isolate in the [agentic-session work](<Multi-turn agentic loops as a benchmark target — what they look like, why they matter, what we've measured.md>): context grows monotonically, every turn pays for the engine's caching choices, and the cost of being slow is paid once per turn for the whole session.

## Why owning the whole thing is the advantage

Here's the part I think is underappreciated. The leading closed agents, Claude Code and OpenAI's Codex among them, own the entire stack. Same vendor builds the model, the inference engine that serves it, and the harness that drives it. That isn't a coincidence or a land grab. It's leverage, and there are two mechanisms in particular that are evident from what these vendors have publicly described, not from any inside knowledge.

The first is training the model on its own harness. When the same organization controls both the reinforcement learning that shapes the model and the harness that emits tool calls, the apparent strategy is to reinforce the exact tool-call patterns that harness produces. The model isn't trained to be good at tool use in the abstract; from what they've described, it's trained to be good at this tool protocol, this system prompt shape, these specific tools, the way the harness actually presents them. A model tuned against its own harness behaves like it was built for that harness, because it was. An open-weights model dropped into the same harness is using a tool protocol it was never specifically rewarded for, and you can see the cost of that mismatch directly in our forge numbers, where the same Gemma 4 26B that scores well behind a proper tool-use protocol on OpenRouter scores zero through a path that emits a tool-call syntax it wasn't trained to produce.

The second mechanism is caching co-design between the harness and the inference stack. Prompt caching, prefix caching, and KV reuse all pay off only when consecutive requests share a long common prefix. Whether that holds is a property of how the harness shapes prompts: where it puts the stable system content, whether it appends new context rather than rewriting earlier turns, how it orders tool results. It looks like the vertically integrated vendors shape their prompts so the cache underneath them actually hits, and tune the cache for the prompt shapes they know they'll send. The harness and the engine are optimized as one system, for performance and for cost at the same time. A harness that doesn't know its engine's caching rules, or an engine that can't see the harness's prompt structure, leaves that win on the floor. Owning both is how you collect it.

Neither of these requires secret sauce to understand. They're the obvious moves once one company controls all three layers, and the public descriptions of how these systems are built line up with both. The point isn't that the closed vendors did something clever and hidden. The point is that vertical integration makes a particular class of optimization available, and they took it.

## Where lucebox sits

This is where I should be plain about the open-weights position, because it's a real constraint and there's no use pretending the gap isn't there.

With open weights, we do not own the model's reinforcement learning. We download weights someone else trained. So the first mechanism, train the model on your harness, is simply off the table. We cannot reinforce luce-bench's tool protocol into the model, and the forge result above is the standing reminder of what that costs: the model is capable, but it wasn't tuned for our path, and we can't tune it.

What we can own is most of the lower stack, and we can co-design those layers as tightly as anyone.

The inference engine is ours. [lucebox](<Meet lucebox — a local AI inference engine optimized for consumer hardware.md>) is built around the caching and prefill machinery that the closed stacks lean on: prefix cache, KV cache with configurable dtypes, prefill via pFlash, and DFlash speculative decode. The whole reason multi-turn loops are interesting on a 24 GB card is that turn N's prompt is turn N-1's prompt plus a suffix, which is precisely the case prefix caching is built to win. We don't get to train the model to produce cache-friendly prompts, but we own the engine that reuses the prefix, and we can tune it for the prompt shapes the loop actually sends.

The eval and harness tooling is ours. [luce-bench](<Running the benchmarks — an intro to luce-bench.md>) is how we see the layers we control. The agent and forge areas check whether tool calls come out in the right shape; agentic-session replays a fixed tool-result history to isolate how the engine behaves as context grows. We can't reward the model for good tool calls, but we can measure exactly where the protocol mismatch bites and shape the harness around it.

The contract between the layers is ours, and this is the piece I'd argue we lean on hardest. The closed vendors close the harness-to-engine gap by owning both ends. We close it by making the engine describe its real config and the harness read that description. The [model card](<Model cards in lucebox — a typed sidecar for what the server actually needs.md>) is a typed sidecar that states what a model actually needs, and [`/props`](<What props tells you about a lucebox server.md>) lets the harness discover the engine's real running config, context limit, cache settings, and budgets, rather than guessing. The [autotuner](<How lucebox auto-tunes itself to your GPU.md>) tunes the engine to the specific hardware the loop runs on, so the cache and context defaults match the card you have in front of you instead of someone else's. That's a different route to the same goal the closed vendors reach by integration: get the harness and the engine to agree on reality, so the caching pays off and the loop stays responsive.

So the accounting has two columns. We give up the model's RL, which is a genuine advantage we can't replicate from outside the weights. We keep the inference engine, the eval tooling, and the interfaces between layers, and we co-design those as one system. A local open stack closes a real fraction of the gap by integrating tightly across the layers it does control, even without owning the training. The place that integration shows up most is the multi-turn loop, which is why the [agentic-session](<Multi-turn agentic loops as a benchmark target — what they look like, why they matter, what we've measured.md>) suite is where the harness-and-engine caching co-design has to prove itself, and where the next numbers I care about will come from.

The model was never the whole product. It's the bottom layer of a stack, and on the layers above it we can compete on equal footing.

---

This is opinion grounded in what we've built and measured; the supporting numbers live in the linked posts and in `Luce-Org/luce-bench-baselines`. The characterization of how vertically integrated vendors operate is read off their public descriptions of their own systems, not private knowledge. As always, scope it to what it is: one lab's view from the open-weights side of the line.

**Related**

- [Multi-turn agentic loops as a benchmark target: what they look like, why they matter, what we've measured](<Multi-turn agentic loops as a benchmark target — what they look like, why they matter, what we've measured.md>)
- [Meet lucebox: a local AI inference engine optimized for consumer hardware](<Meet lucebox — a local AI inference engine optimized for consumer hardware.md>)
- [How lucebox auto-tunes itself to your GPU](<How lucebox auto-tunes itself to your GPU.md>)
- [What `/props` tells you about a lucebox server](<What props tells you about a lucebox server.md>)
- [Model cards in lucebox: a typed sidecar for what the server actually needs](<Model cards in lucebox — a typed sidecar for what the server actually needs.md>)
- [Running the benchmarks: an intro to luce-bench](<Running the benchmarks — an intro to luce-bench.md>)
