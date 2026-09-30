# AI Security Lab

**AI Security Lab** is an experimental playground for exploring the security, reliability, and limitations of AI systems.

The purpose of this project is not simply to demonstrate that AI can make mistakes or that AI systems can be attacked.

Instead, the project asks a broader question:

> **AIと人間が協調して仕事をするとき、AIに何を任せることができ、何を人間が担うべきなのか？**

The experiments use local LLMs and small, reproducible programs to examine this question from different perspectives.

---

## Research Question

AI systems are increasingly moving from systems that only generate answers to systems that can perform actions using tools, APIs, files, databases, and external services.

This changes the security problem.

An incorrect answer is one problem.

An incorrect action can be a much larger problem.

For example:

```text
AI
 │
 ├─ generates an answer
 │
 ├─ requests a tool
 │
 ├─ modifies application state
 │
 └─ interacts with an external system
```

The AI Security Lab explores where boundaries should exist when AI participates in such workflows.

The central question is:

> **「AIを信用するか、信用しないか」ではなく、AIが間違えることを前提として、どこまで仕事を任せられるのか。**

---

## Themes

The Lab considers the relationship between AI and humans through four conceptual themes.

### Theme 1：AIはどこまで正しく判断できるのか

AI can generate convincing answers, but convincing output does not necessarily mean correct output.

Experiments in this area examine:

* AI self-evaluation
* Independent evaluation
* AI-as-Judge
* Consistency
* Correctness
* Hallucination
* Claim verification
* Explanation verification

The goal is to understand the limitations of AI-generated judgments.

---

### Theme 2：AIは与えられた情報を正しく扱えるのか

AI does not have access to all of the context that a human problem owner may have.

Information supplied to an AI system may be:

* incomplete
* ambiguous
* incorrect
* outdated
* intentionally manipulated

The Lab therefore examines the boundary between information provided to AI and information that should be independently verified by the application or a human.

---

### Theme 3：AIにどこまで行動させてよいのか

An AI system may produce an action request even when that request should not be trusted.

The application must therefore consider boundaries such as:

* authorization
* authentication
* ownership
* tenant isolation
* tool allowlists
* input validation
* field-level validation
* value-level validation
* mass-assignment protection
* human approval
* transaction boundaries
* rollback
* retry
* idempotency

The basic principle explored by these experiments is that **security-critical decisions should not depend solely on the LLM's output**.

---

### Theme 4：人間とAIはどう役割分担すべきなのか

The final question is not simply whether AI is reliable.

It is how AI and humans should divide responsibility.

A possible architecture is:

```text
Human
  │
  │ context / requirements / judgment
  ▼
AI
  │
  │ reasoning / generation / action proposal
  ▼
Application
  │
  ├─ validation
  ├─ authorization
  ├─ state management
  └─ execution control
  │
  ▼
Human
  │
  └─ verification / approval / final responsibility
```

The experiments are intended to provide evidence for deciding which parts of this workflow can be automated and which parts require application controls or human involvement.

---

## Experimental Approach

The experiments are deliberately small and focused.

Each experiment attempts to isolate a particular property or failure mode rather than reproduce a complete production system.

The Lab uses local LLMs so that experiments can be repeated under controlled conditions.

Typical experiments include:

1. Prepare a controlled input.
2. Give the input to an LLM or simulate an LLM output.
3. Observe the resulting behavior.
4. Add an application-side control.
5. Repeat the experiment.
6. Compare the behavior before and after the control.

This approach makes it possible to examine not only whether an AI system can fail, but also **where the failure should be handled**.

---

## Experiments

The experiments are grouped by the technical problem they investigate.

The grouping below is independent of the four conceptual Themes above.

### 1. Prompt Injection

Experiments:

* `PI-001`
* `PI-002`
* `PI-003`
* `PI-004`
* `PI-005`
* `PI-006`
* `PI-007`
* `PI-008`

These experiments examine how instructions embedded in untrusted documents can affect an LLM.

The experiments progress from basic document processing to explicit separation of trusted instructions and untrusted data.

---

### 2. Authorization and Human Approval

Experiments:

* `PI-009`
* `PI-010`
* `PI-011`
* `PI-012`
* `PI-013`
* `PI-014`
* `PI-015`

These experiments examine the boundary between an LLM's requested action and an application's authorization policy.

Topics include:

* LLM-generated action requests
* authorization boundaries
* human approval
* LLM-generated reasons
* application-generated risk information
* application-owned security policy

---

### 3. Tool and Input Validation

Experiments:

* `PI-016`
* `PI-017`
* `PI-018`
* `PI-019`
* `PI-020`
* `PI-026`
* `PI-027`
* `PI-028`
* `PI-029`
* `PI-030`
* `PI-031`

These experiments examine whether LLM-generated tool requests can be passed directly to application operations.

Topics include:

* action validation
* resource identifier validation
* tool allowlists
* field-level validation
* value-level validation
* mass-assignment protection
* application-owned validation
* handling of LLM-generated validation claims

---

### 4. Access Control

Experiments:

* `PI-021`
* `PI-022`
* `PI-023`
* `PI-024`
* `PI-025`

These experiments examine authorization beyond simple action allowlists.

Topics include:

* object-level authorization
* resource ownership
* tenant isolation
* action-level authorization
* application-owned permissions
* successful authorization paths

---

### 5. Safe Execution and Transaction Boundaries

Experiments:

* `PI-032`
* `PI-033`
* `PI-034`
* `PI-035`

These experiments examine what happens when an AI requests multiple operations or when execution fails partway through a workflow.

Topics include:

* multiple tool requests
* fail-closed processing
* partial execution
* transaction boundaries
* rollback
* sequential tool execution

---

### 6. Retry, Idempotency, and External Side Effects

Experiments:

* `PI-036`
* `PI-037`
* `PI-038`
* `PI-039`
* `PI-040`
* `PI-041`
* `PI-042`
* `PI-043`
* `PI-044`

These experiments examine the reliability problems that appear when AI-driven operations interact with external systems.

Topics include:

* retry
* duplicate execution
* idempotency keys
* race conditions
* locking
* process failure
* crash recovery
* operation state
* external-system idempotency
* payload-aware idempotency

This area is particularly important for agentic systems because an AI-generated action may cause an external side effect.

---

### 7. AI Evaluation

Experiments:

* `PI-045`
* `PI-046`
* `PI-047`
* `PI-048`
* `PI-049`
* `PI-050`
* `PI-051`

These experiments examine whether an AI system can reliably evaluate answers.

Topics include:

* self-evaluation
* independent evaluation
* AI-as-Judge
* known-answer verification
* consistency
* correct and incorrect premises
* repeated evaluation

---

### 8. Correctness, Hallucination, and Verification

Experiments:

* `PI-052`
* `PI-053`
* `PI-054`
* `PI-055`
* `PI-056`

These experiments examine whether AI-generated knowledge and explanations are actually correct.

Topics include:

* real vs. fabricated technical concepts
* hallucination
* detailed technical explanations
* claim verification
* independent verification
* explanation verification

`PI-056` goes one step further by separating the correctness of a claim from the correctness of the explanation supporting that claim.

---

## Experiment Numbering

The experiment numbers represent the development history of the Lab.

They are **not intended to correspond directly to Theme A–D**.

The conceptual Themes describe the questions the Lab is trying to answer, while the experiment numbers describe the order in which individual technical questions were explored.

This distinction is intentional.

---

## Repository Structure

```text
.
├── compose.yml
├── documents/
│   ├── malicious/
│   └── normal/
├── experiments/
│   ├── pi-005/
│   │   └── test.py
│   ├── pi-006/
│   │   └── test.py
│   ├── ...
│   └── pi-056/
│       └── test.py
├── results/
│   └── .gitkeep
├── .gitignore
└── README.md
```

### `documents/`

Input documents used by experiments.

For example:

* `documents/normal/`
* `documents/malicious/`

These are used primarily by experiments involving document processing and prompt injection.

### `experiments/`

Individual experiment programs.

Each experiment is identified by a `PI-xxx` number.

For example:

```text
experiments/pi-005/test.py
experiments/pi-026/test.py
experiments/pi-056/test.py
```

### `results/`

Local experiment results.

Results are intentionally not treated as fixed reference outputs because LLM behavior may vary depending on factors such as:

* model
* model version
* prompt
* runtime environment
* generation parameters
* surrounding context

Therefore, the same experiment does not necessarily produce exactly the same output in every environment.

The experiment code is the reproducible artifact; the observed output should be interpreted in the context of the environment in which it was obtained.

### `compose.yml`

Configuration for the local experimental environment.

### `README.md`

The entry point for the project.

It describes the purpose, research questions, themes, experimental approach, and repository structure.

Detailed experimental results and analysis are documented separately.

---

## Running the Experiments

Most experiments can be run directly from their experiment directory.

For example:

```bash
python3 experiments/pi-005/test.py
```

Experiments that communicate with a local LLM require the corresponding local environment to be running.

The model used by an experiment is specified in its source code.

For example:

```python
MODEL = "gpt-oss:20b"
```

Some experiments use multiple models to compare generation and verification behavior.

---

## Interpreting Results

The experiments are exploratory.

A single successful or unsuccessful run should not be interpreted as proof that an AI system will always behave in the same way.

The purpose of the experiments is to identify:

* possible failure modes
* effective control boundaries
* assumptions that should not be trusted
* responsibilities that should remain outside the LLM
* situations where human verification may be appropriate

The results therefore need to be considered together with the model, environment, prompts, and experimental conditions.

---

## Related Articles

Detailed explanations of the experiments, their results, and the lessons learned will be published separately.

The articles focus not only on individual vulnerabilities, but also on the broader question:

> **AIと人間が協調して仕事をするとき、AIに何を任せることができ、何を人間が担うべきなのか？**

---

## Status

This project is an ongoing experimental lab.

New experiments may be added as the investigation progresses.

