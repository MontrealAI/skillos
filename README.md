# Agent SkillOS

<p align="center">
  <strong>The operating system for self-improving AI agents.</strong>
</p>

<p align="center">
  Every job can become a reusable skill. Every verified skill can strengthen the whole network. One agent learns; the authorized network levels up.
</p>

<p align="center">
  <a href="https://montrealai.github.io/skillos/"><strong>Open the live SkillOS site</strong></a>
  ·
  <a href="https://github.com/MontrealAI/skillos/actions"><strong>Run the proofs</strong></a>
  ·
  <a href="./docs"><strong>Read the docs</strong></a>
  ·
  <a href="./site/proof-registry.json"><strong>View the proof registry</strong></a>
</p>

<p align="center">
  <a href="https://github.com/MontrealAI/skillos/actions/workflows/pages.yml"><img alt="GitHub Pages" src="https://github.com/MontrealAI/skillos/actions/workflows/pages.yml/badge.svg"></a>
  <a href="https://github.com/MontrealAI/skillos/actions/workflows/tests.yml"><img alt="Tests" src="https://github.com/MontrealAI/skillos/actions/workflows/tests.yml/badge.svg"></a>
  <a href="./LICENSE"><img alt="MIT License" src="https://img.shields.io/badge/License-MIT-blue.svg"></a>
</p>

---

## What SkillOS is

**SkillOS is a reference implementation and public proof environment for self-improving AI-agent systems.**

The central idea is simple:

```text
work
→ trace
→ lesson
→ candidate skill
→ verification
→ release
→ routing upgrade
→ better future work
```

In ordinary automation, a completed job often disappears into a log. In SkillOS, completed work can become a reusable, verifiable skill. Once approved, that skill can be routed across a larger specialist-agent network.

**The SkillOS thesis:**

> Intelligence should not be trapped inside one agent, one prompt, one workflow, or one team.  
> Verified capability should become reusable infrastructure.

---

## The one-line version

**SkillOS turns work into compounding capability.**

Every verified job can become a trace.  
Every trace can become a skill.  
Every verified skill can become a release.  
Every release can improve future routing.  
One agent learns; the system can level up.

---

## Why this matters

A large multi-agent system becomes powerful only when learning is reusable.

SkillOS is designed around a practical compounding loop:

```text
1. Many specialist agents perform work.
2. Work produces traces.
3. Traces produce lessons.
4. Lessons become candidate skills.
5. Verifier agents test those skills.
6. Risk, policy, provenance, quality, and governance gates approve or reject the release.
7. Approved skills become available to authorized future agents.
8. Future work becomes faster, safer, more reliable, and more capable.
```

That is the SkillOS flywheel:

```text
work → traces → skills → verification → releases → routing upgrades → compounding capability
```

---

## What you can see today

The repository includes a public website, GitHub Actions workflows, proof receipts, reports, badges, and generated proof pages.

Start here:

```text
https://montrealai.github.io/skillos/
```

Then open any proof card. Each public proof page is designed to show, in a non-technical way:

```text
what was tested
what passed
which agent/skill system was used
which baselines were compared
which gates were pre-registered
which JSON receipt was generated
which report and badge were published
how the GitHub Action regenerated the proof
```

---

## How to see the agents

SkillOS does not show agents as cartoon avatars.

It shows them as a coordinated operating system:

```text
specialist roles
verifier courts
red-team courts
policy courts
risk vetoes
routing agents
provenance auditors
release gates
site renderers
registry publishers
GitHub Actions workflows
```

On the proof pages, look for the **Skills Used** section.

That section explains the operating stack behind each proof, usually with cards showing:

```text
skill name
operational layer
purpose
input signal
output artifact
verifier
```

This is the most user-friendly way to understand what the multi-agent system is doing.

---

## How to see the proof

There are three levels of proof visibility.

### 1. Visual proof page

Open:

```text
https://montrealai.github.io/skillos/
```

Then click a proof card.

This is the best view for non-technical readers.

### 2. GitHub Actions run

Open:

```text
https://github.com/MontrealAI/skillos/actions
```

Choose a proof workflow and click:

```text
Run workflow
```

When the run turns green, GitHub has regenerated the proof autonomously.

### 3. Machine-readable receipt

Each proof generates a JSON receipt, usually in:

```text
data/
site/data/
```

The receipt is the machine-readable evidence: inputs, gates, scores, baselines, controls, releases, and proof metadata.

---

## Current proof portfolio

SkillOS is built as a growing portfolio of autonomous proofs. The exact live list is regenerated through the public site and proof registry.

The proof program is organized around these layers:

| Layer | What it tests |
|---|---|
| Shadow Pilot | Can the system prove value without emailing customers or using private data? |
| Capability Liquidity | Can work become reusable, verified capability? |
| Cross-Domain Transfer | Do skills transfer beyond one workflow? |
| Skill Provenance | Are skills traceable, replayable, and verified? |
| Causal Attribution | Did RSI cause the improvement, or was it benchmark luck? |
| Objective Integrity | Can the system improve without gaming the metric? |
| Open Replication | Can others rerun the proof from public receipts? |
| Adversarial Benchmarking | Can the system create harder tests and repair against them? |
| Continual Capability | Can it keep improving under distribution shift? |
| Full-Stack Lifecycle | Can the full work-to-skill-to-release loop work end-to-end? |
| Skill Compounding Moat | Does one verified skill improve the network? |
| Fork Resistance | Can a surface clone copy the files but not the capability network? |
| Capability Economy | Can verified skills clear like an economy? |
| Incentive-Compatible Skill Market | Do incentives reward truthful reusable skills instead of spam or proxy games? |
| SLA Reliability Mesh | Can verified skills become reliable service-level capability? |
| Assurance Case Graph | Can skills become audit-ready evidence, controls, and claims? |
| Governance Twin | Can capability routes be tested in a policy/permission twin before release? |

---

## The flagship mechanism

SkillOS coordinates a large specialist-agent system through a public, repeatable pipeline:

```text
demand intake
→ decomposition
→ specialist-agent routing
→ execution trace
→ lesson extraction
→ skill proposal
→ verifier courts
→ red-team challenge
→ risk and policy gates
→ provenance receipt
→ release decision
→ site rendering
→ public registry update
→ future routing improvement
```

Every proof should answer:

```text
What changed?
Why did it improve?
Which controls prevented bad improvement?
Can the proof be rerun?
Can a non-technical viewer understand it?
```

---

## Non-technical quick start

### Step 1 — Open the website

```text
https://montrealai.github.io/skillos/
```

### Step 2 — Open a proof card

Choose a proof that matches your question, for example:

```text
Capability Governance Twin
Capability Assurance Case Graph
Capability SLA Reliability Mesh
Capability Economy Clearinghouse
Skill Compounding Moat
```

### Step 3 — Read the top metrics

Look for:

```text
proved: true
value capture
risk breach rate
policy violation rate
SLA breach rate
skills displayed
RSI releases
```

### Step 4 — Read “Skills Used”

This explains what the agent system did in plain language.

### Step 5 — Rerun the proof

Open:

```text
https://github.com/MontrealAI/skillos/actions
```

Choose the corresponding workflow and click:

```text
Run workflow
```

Recommended inputs:

```text
publish_to_repo: true
deploy_pages: false
```

---

## Technical quick start

Clone the repository:

```bash
git clone https://github.com/MontrealAI/skillos.git
cd skillos
```

Create an environment:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -U pip
python -m pip install -e .
```

Run the reference demo:

```bash
python -m skillos.cli demo
python -m skillos.cli status
```

Run the original reference proof:

```bash
python -m skillos.cli wealth-proof
```

Serve locally:

```bash
python -m skillos.cli serve
```

Then open:

```text
http://127.0.0.1:8765
```

No API keys are required for the deterministic reference workflows.

---

## How GitHub Actions are used

SkillOS is designed so proofs can run autonomously.

A typical proof workflow does this:

```text
1. Check out repository.
2. Set up Python.
3. Run the proof script.
4. Verify the proof receipt.
5. Render the visual proof page.
6. Publish proof assets into the public site.
7. Verify the site integration.
8. Upload proof artifacts.
9. Optionally commit generated outputs.
10. Optionally deploy GitHub Pages.
```

A healthy run should generate files like:

```text
data/<proof-id>.json
docs/<proof-id>.md
badges/<proof-id>.svg
site/<proof-id>.html
site/data/<proof-id>.json
site/docs/<proof-id>.md
site/badges/<proof-id>.svg
site/index.html
site/proof-registry.json
site/sitemap.xml
site/robots.txt
```

---

## Anatomy of a proof

A strong SkillOS proof should include:

```text
deterministic benchmark
pre-registered gates
baseline comparisons
negative controls
locked holdout evaluation
bootstrap confidence checks
verifier courts
risk gates
policy / permission gates where relevant
Skills Used display
JSON receipt
Markdown report
public webpage
badge
registry entry
GitHub Actions rerun path
```

---

## The Skills Used standard

Each proof should display the skills it used.

A skill card should include:

```text
name
layer
purpose
input signal
output artifact
verifier
```

Example:

```text
Skill: Policy-as-Code Compilation
Layer: Policy
Purpose: Converts governance boundaries into machine-checkable constraints.
Input: policy text, compliance boundary, public claim boundary
Output: policy constraint set
Verifier: Policy Coverage Court
```

This makes the agent system understandable to non-technical viewers.

---

## Current public safety boundary

SkillOS is powerful, but public language must stay precise.

SkillOS does **not** claim:

```text
guaranteed wealth
audited ROI
live customer revenue
investment returns
legal advice
medical advice
employment advice
credit advice
achieved superintelligence
Kardashev Type II civilization
```

SkillOS does claim a safer, testable mechanism:

```text
completed work can become verified traces
verified traces can become reusable skills
reusable skills can be released to authorized agents
validated releases can improve future routing
the proof process can be rerun publicly through GitHub Actions
```

Use this framing:

> SkillOS makes the mechanism visible, testable, and repeatable under benchmark conditions.

---

## Recommended public phrasing

Use:

```text
reproducible benchmark proof
deterministic reference workflow
verified skill release
measured improvement under demo assumptions
public GitHub Actions rerun
machine-readable receipt
```

Avoid:

```text
guaranteed wealth
real investment results
audited ROI
risk-free
inevitable superintelligence
automatic success
```

---

## Repository structure

```text
.github/workflows/        GitHub Actions workflows
COPY_PASTE_GITHUB_ACTIONS/ Backup workflow files for web-upload issues
assets/                  Static assets
badges/                  Repository-level generated proof badges
data/                    Repository-level generated proof receipts
docs/                    Documentation and proof reports
examples/                Example inputs and workflows
scripts/                 Proof runners, verifiers, renderers, publishers
site/                    Public GitHub Pages site
site/data/               Public proof JSON receipts
site/docs/               Public proof reports
site/badges/             Public proof badges
skillos/                 Python reference implementation
skills/                  Skill-related artifacts
tests/                   Test suite
web/                     Web support files
```

---

## Adding a new autonomous proof

A complete proof should usually add:

```text
.github/workflows/autonomous-rsi-<proof-name>-proof.yml
scripts/run_rsi_<proof_name>_proof.py
scripts/verify_rsi_<proof_name>_proof.py
scripts/render_rsi_<proof_name>_site.py
scripts/publish_rsi_<proof_name>_to_hub.py
scripts/verify_rsi_<proof_name>_site.py
docs/AUTONOMOUS_RSI_<PROOF_NAME>_PROOF.md
```

The workflow should generate:

```text
data/<proof-id>.json
docs/<proof-id>.md
badges/<proof-id>.svg
site/<proof-id>.html
site/data/<proof-id>.json
site/docs/<proof-id>.md
site/badges/<proof-id>.svg
site/index.html
site/proof-registry.json
site/sitemap.xml
site/robots.txt
```

---

## Best-practice proof gates

Each proof should fail if any critical gate fails.

Recommended gate families:

```text
scale gate
locked holdout gate
baseline improvement gate
negative-control gate
bootstrap confidence gate
risk breach gate
policy violation gate
unauthorized action gate
skills display gate
site integration gate
public boundary gate
```

---

## What makes this different

Most AI demos show one impressive output.

SkillOS is designed to show whether a system can improve its future work by turning past work into verified reusable skill.

That means the important artifact is not just the answer.

The important artifact is the loop:

```text
work becomes evidence
evidence becomes skill
skill becomes release
release improves routing
routing improves future work
future work creates better evidence
```

That is the core of the SkillOS compounding engine.

---

## Practical use cases

SkillOS is best suited for work where:

```text
jobs repeat with variation
quality matters
traceability matters
improvement compounds
risk must be controlled
skills can be reused
teams need proof, not just claims
```

Examples:

```text
enterprise workflow automation
developer operations
regulated documentation
customer operations
proof generation
policy and governance workflows
security review
reliability engineering
agent marketplace coordination
capability routing
```

---

## For executives

SkillOS should be understood as a capability operating system.

It asks:

```text
Which jobs create reusable skill?
Which skills are verified?
Which releases improve the network?
Which controls prevent unsafe improvement?
Which proofs can anyone rerun?
```

The long-term ambition is significant:

> If an organization can reliably convert work into verified reusable skill, and convert verified reusable skill into network-wide capability, then intelligence becomes an accumulating asset.

SkillOS is designed to make that flywheel public, measurable, and repeatable.

---

## For researchers

SkillOS is an experimental environment for:

```text
recursive self-improvement
multi-agent coordination
skill reuse
capability liquidity
causal attribution
objective integrity
open replication
adversarial benchmark generation
continual learning
provenance and assurance
governed deployment
```

The research focus is not merely whether a single agent performs well.

The focus is whether a network of specialized agents can improve its future coordination through validated reusable skills.

---

## For builders

A SkillOS-compatible workflow should produce:

```text
structured trace
lesson
candidate skill
test result
verifier decision
risk decision
release decision
routing update
public or private receipt
```

The minimum viable SkillOS loop is:

```text
capture → learn → verify → release → reuse
```

---

## For non-technical reviewers

The easiest way to review SkillOS is:

```text
1. Open the website.
2. Click a proof.
3. Read the plain-English summary.
4. Look at the Skills Used cards.
5. Confirm the proof says passed.
6. Open the GitHub Action.
7. Confirm the workflow can rerun.
8. Open the JSON receipt if needed.
```

You do not need to understand the code to understand what was tested.

---

## License

This project is released under the MIT License.

See:

```text
LICENSE
```

---

## Final summary

**SkillOS is a public reference system for compounding AI capability.**

It turns work into traces.  
Traces into skills.  
Skills into verified releases.  
Verified releases into better routing.  
Better routing into better future work.

One agent learns.  
The authorized network levels up.  
Capability compounds.
