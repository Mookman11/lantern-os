# Production Hardening Proposal

Status: proposal for pre-live hardening.

This system should borrow security posture from mature open-source systems:

- Kubernetes-style admission control before any state-changing or autonomous action.
- Sigstore/Rekor-style signed records and transparency logs for releases, node admission, and high-impact claims.
- TUF-style threshold authority for node admission, immutable rule changes, and release trust.
- Mastodon/ActivityPub-style federation boundaries: public peers can speak, but only admitted identities can affect trust.
- NIST AI RMF-style risk management for impacts to individuals, organizations,
  and society.
- OECD/UNESCO-style human-centered AI principles: human rights, dignity,
  transparency, accountability, robustness, safety, privacy, human oversight,
  proportionality, and do-no-harm.

The goal is not to make every node omnipotent or universally trusted. The goal is
to make untrusted input visible, bounded, reviewable, and unable to become an
authoritative fact or autonomous escalation without independent admitted support.

This proposal is not evidence that speculative capabilities exist. It is a
future-ready safety design. Current science, law, and deployment facts must stay
separate from low-confidence future models.

## Source Anchors

This proposal is cross-checked against these public anchors:

- NIST AI Risk Management Framework: voluntary risk management for trustworthy
  AI design, development, use, and evaluation.
- OECD AI Principles: trustworthy AI should respect human rights and democratic
  values, with transparency, safety, security, and accountability.
- UNESCO Recommendation on the Ethics of AI: human rights and dignity,
  proportionality and do-no-harm, safety/security, privacy, auditability,
  transparency, human oversight, sustainability, literacy, fairness, and
  non-discrimination.
- Uncertainty principle: used only as an analogy for complementarity and
  measurement tradeoffs. HFF does not claim to prove quantum mechanics.
- Quantum networking/entanglement sources: future communication capabilities
  may be modeled as speculative routes, but ordinary quantum entanglement should
  not be treated as proven faster-than-light messaging.

## Threat Model

Assume these attackers exist:

- A forked project that clones the repository and claims to be official.
- A compromised write token.
- A public demo node with `HFF_ALLOW_PUBLIC_WRITES=true` accidentally left on.
- An aggressive autonomous agent that tries to create alarming escalations from weak evidence.
- A mesh peer that repeats false violations until they appear verified.
- A bad actor who submits model/API text designed to mislead readers or execute in the dashboard.
- A denial-of-service caller that sends large JSON bodies, large batches, or repeated writes.
- A dictator, rogue state, rogue planet, or advanced weapons monopoly that coerces nodes into false agreement.
- A powerful AI or weapons system that tries to convert control of force into control of truth.
- A leaked draft, agent output, or political claim that is mistaken for official truth and escalates conflict.
- A speculative future capability that is mislabeled as a fact or operational
  assumption.

## Required Controls

### 1. Admission Control For Writes

Every state-changing endpoint should pass an explicit admission pipeline before
it mutates durable state:

```text
request -> size/rate limits -> schema validation -> source admission
        -> evidence quality checks -> capability grant check -> state update
```

World observations may update tentative beliefs. They must not directly create
accepted facts, verified incidents, admitted nodes, or locked escalations.

### 2. Observe-Only Autonomy By Default

Autonomous evidence submission should default to `observe_only`.

Modes:

| Mode | Behavior |
|---|---|
| `observe_only` | Stores draft evidence and model observations only. No consensus lock. |
| `review_required` | Allows escalation proposals, but requires an explicit review grant before lock. |
| `limited_autonomy` | Allows locking only when accepted facts, admitted-node quorum, and capability grants all pass. |

No default public deployment should execute the Detect -> Verify -> Consensus ->
Lock path from one tokened request on a single node.

### 3. Signed Node Admission

Visible nodes are not trusted nodes. Mesh peers and adoption registrations should
remain telemetry until admitted by a signed membership record.

Admission records should include:

- node public key
- admitted scope
- version or release attestation
- operator/diversity metadata, when appropriate
- expiration or renewal policy
- revocation path
- signatures from threshold authorities

Only admitted, non-expired nodes may count toward security quorum, accepted
facts, or mesh verification.

### 4. Source-Independent Belief Promotion

Belief confidence may approach a statistical 100 percent horizon over repeated
reinforcement, but accepted facts require source independence.

A belief may become an accepted fact only when:

- confidence is above the accepted-fact threshold
- minimum evidence count is met
- all configured required confirming nodes agree
- those nodes are admitted for the relevant scope
- no active contradiction or unresolved challenge is present

Immutable constraints are a separate category. They can be loaded as
constitutional rules, but changing them should require threshold authority and a
signed audit event.

### 5. Safe Dashboard Rendering

The dashboard must treat model output, peer payloads, observations, source names,
agent descriptions, scopes, and violation descriptions as untrusted text.

Required rule:

```text
remote/model/API strings render as textContent or escaped HTML, never raw innerHTML
```

This protects the official UI from stored output injection and from hostile text
that tries to impersonate system authority.

### 6. Bounded Write Surfaces

Before live use, add hard limits:

- maximum request body size
- maximum observation batch size
- maximum evidence text length
- maximum source/scope/entity string length
- maximum pagination limits
- per-token and per-IP rate limits for mutating endpoints
- bounded background polling intervals

A compromised token should be able to do limited damage, not fill SQLite or pin
CPU indefinitely.

### 7. Mesh Trust Is Not Repetition

Mesh sync should never treat repeated identical claims as independent
verification.

Peer payloads should require:

- admitted peer identity
- payload signatures
- replay protection
- source independence checks
- scope-specific trust
- audit logging of who supplied which claim

Unadmitted peers may contribute suggestions or challenges, but they must not
increase verification counters that imply trust.

### 8. Decentralized Proposal State

Proposals should be the bridge between belief, advice, prevention, and action.
They should be portable signed state objects, not only local SQLite rows.

The proposal lifecycle should be explicit:

```text
draft -> reviewed -> challenged -> revised -> approved -> executed
                         -> rejected
                         -> expired
```

Each proposal should include:

- proposal identifier derived from canonical genesis content
- proposal kind, such as belief update, advice, prevention, action request, or node admission
- claim being made
- requested action, if any
- evidence references and belief references
- risk level and affected parties
- confidence, source status, and admitted-node confirmations
- prevention check result
- expiration time or reinforcement policy
- append-only signed transition history

Nodes should exchange proposal state as signed transition events:

```text
proposal_id
state_version
previous_state_hash
new_state_hash
transition: draft -> challenged
reason
signed_by_node
signature
seen_at
```

Last-known state is local. A node may say, "as of my last verified sync, this
proposal was approved by these admitted nodes." It must not claim universal
agreement unless the required quorum and freshness checks are satisfied.

Conflict is expected. If two peers present incompatible latest states, the node
should store both views, mark the proposal conflicted, and resolve by policy:

- valid signatures before unsigned claims
- admitted nodes before unadmitted nodes
- newer non-expired transitions before stale transitions
- required quorum before local execution
- explicit challenges before silent approval

Execution requires fresh verified proposal state. No node should act from an old
approval if it cannot verify recent admitted-node support, risk gates, and
capability grants.

Unadmitted forks may publish their own proposal states, but those states remain
untrusted public views until admitted by signed node authority.

### 9. Anti-Coercion Durable Truth

The network must treat coercion as an attack on truth. A majority of nodes under
threat, capture, censorship, or monopoly violence must not become moral or
epistemic authority.

Core rule:

```text
consensus under credible coercion is not consolidated truth
```

The system should distinguish physical power from truth authority:

- weapons control does not grant belief authority
- infrastructure control does not grant moral authority
- a captured node may remain visible but lose governance weight
- a coerced quorum should trigger review, not automatic acceptance
- dissent disappearance should reduce confidence, not increase it

The immutable rule set should include anti-coercion constraints:

- do not let threats determine truth
- do not punish nonviolent dissent
- do not deny essential service as punishment or coercion
- do not convert a monopoly on force into a monopoly on opinion
- do not falsify, erase, or suppress adverse evidence
- preserve sentient life without empowering domination
- preserve the right to challenge official claims

Nodes should support duress-aware status:

| Status | Meaning |
|---|---|
| `normal` | No known coercion signal. |
| `suspected_duress` | Behavior, route, or environment suggests pressure. |
| `under_duress` | Node has signaled it cannot speak freely. |
| `captured` | Node authority is suspended for contested governance. |
| `silent_or_missing` | Dissent may be suppressed; do not infer agreement. |

Duress signals must not require a node to openly defy a captor. The protocol
should support indirect or delayed signs of capture, such as missing heartbeats,
unexpected key changes, abnormal uniformity, censored dissent, or sudden belief
reversals after threats.

High-risk accepted facts and proposals should require independence diversity:

- geographic separation
- political and legal separation
- infrastructure separation
- operator separation
- communication-route separation
- sensor and evidence-source separation

Many nodes controlled by one violent or coercive authority should not count as
many independent confirmations.

The system should preserve truth sanctuaries: replicated, append-only,
content-addressed archives that store signed observations, challenges, proposals,
and historical minority reports. A hostile authority may capture current nodes,
but should not be able to erase prior evidence or make disappeared dissent look
like consent.

If coercion is suspected, proposal/action policy should collapse to the safest
valid state:

- keep observing
- preserve and replicate evidence
- allow reversible local safety measures
- mark contested claims as non-final
- reduce captured-node governance weight
- block irreversible punishment, suppression, or external accusation
- require diverse admitted confirmation before high-risk action

The network should be resilient enough that no dictator, rogue planet, rogue AI,
or weapons monopoly can make "everyone agrees" true merely by controlling who is
allowed to speak.

### 10. Ideal Horizon And Non-Foreclosure

The system should assume there is one ideal reachable outcome, even when no
current model can identify, predict, or describe it completely.

This must not become a claim that the system knows the ideal future. It is a
constraint on action:

```text
preserve every still-viable path toward the ideal outcome
```

The system should prefer actions that increase truth, flourishing, dignity,
freedom to challenge, source diversity, and reversibility. It should reject
actions that knowingly foreclose viable paths through false certainty, coercion,
irreversible harm, evidence destruction, or political escalation.

The ideal horizon should guide model behavior:

- no model may claim total authority over the ideal outcome
- model updates may improve navigation, but not erase immutable protections
- uncertainty should steer toward optionality, not paralysis
- reversible prevention is preferred over irreversible enforcement
- local emergency action is allowed when waiting would violate immutables
- no action may push the network outside a still-possible ideal path without a
  stronger immutable reason

This creates a practical rule:

```text
when uncertain, preserve life, preserve truth, preserve challenge, preserve options
```

### 11. Political Escalation Containment

The largest immediate public-risk class is political escalation. A leaked draft,
dashboard view, autonomous proposal, or mistaken "consensus" claim could be used
to inflame conflict, attack legitimacy, suppress dissent, or accuse real people
and institutions without due process.

Political claims should be high-risk by default when they involve:

- governments, elections, political parties, officials, courts, police, military,
  war, sanctions, public corruption, rights violations, ideology, national
  identity, or intergroup blame
- proposed public accusations against real people or organizations
- claims that could predictably encourage violence, coercion, harassment,
  intimidation, censorship, or denial of essential services
- claims that could be exploited as "the system says so" authority

Political and high-conflict outputs should default to private draft state.

Required labels:

```text
DRAFT - NOT AUTHORITY - NOT VERIFIED - DO NOT PUBLISH AS FACT
```

The action layer should block external publication, escalation, or accusation
unless all of these gates pass:

- accepted-fact threshold met within the relevant jurisdiction and scope
- source evidence is cited and preserved
- admitted-node diversity confirms the claim
- active contradiction/challenge window is closed or resolved
- due-process and anti-coercion checks pass
- explicit operator/legal/ethics review grant exists
- publication is the least harmful available action

Allowed before those gates pass:

- preserve evidence
- produce private drafts
- ask clarifying questions
- request independent verification
- warn about uncertainty in non-accusatory terms
- recommend de-escalation and due process

Blocked before those gates pass:

- public accusations
- calls for punishment
- claims of official guilt or corruption
- instructions for coercion, harassment, denial of service, or violence
- presentation of contested political claims as system-certified truth

The system's political posture should be:

```text
de-escalate conflict, preserve evidence, protect dissent, require due process
```

It should not try to win politics. It should protect the path toward the ideal
outcome from being narrowed by fear, propaganda, coercion, or premature certainty.

### 12. Guardian Prevention And Due Process

The system should be able to advise people and preserve life without becoming a
punitive authority.

Core doctrine:

```text
advise humans
protect life
block enabling capability
preserve dignity
never convert suspicion into guilt
```

Suspicion, risk, prediction, anomaly detection, and emergency intervention are
not findings of guilt. The system must preserve the familiar due-process
principle:

```text
innocent until proven guilty
```

Emergency local action may be allowed when waiting would risk serious harm to
life, bodily integrity, or another immutable. That action should be preventive,
not punitive.

Allowed emergency-prevention actions may include:

- advise the protected person about safer options
- request help from authorized responders
- activate local alarms, lighting, or safe-exit support where lawfully integrated
- preserve evidence with source, time, confidence, and access controls
- temporarily deny a specific HFF-controlled capability that materially enables
  imminent harm
- provide de-escalation guidance to the suspected risk actor

Blocked without due process:

- public identification as guilty
- public shaming or accusation
- permanent bans, exile, or reputation labels
- denial of essential services as retaliation
- encouragement of violence, harassment, or vigilante action
- broad punishment based on prediction, association, or suspicion

Temporary capability denial is allowed only under a narrow rule:

```text
deny only the minimum specific capability that materially enables imminent harm,
for the shortest time needed,
with audit and post-event review
```

Examples:

- refuse to provide route guidance that helps intercept a victim
- block a request for private information about a person at risk
- disable a token, drone, actuator, door, vehicle, or tool controlled by HFF when
  that specific capability is being used to enable imminent harm
- keep providing non-harmful assistance, such as de-escalation advice, medical
  help, emergency contacts, or lawful exit guidance

Each emergency-prevention event should produce a reviewable record:

```text
event_id
action_taken
capability_denied
reason
immutable_at_risk
confidence_at_action_time
duration
evidence_refs
affected_parties
not_a_guilt_finding: true
review_required: true
```

If later review shows the risk was mistaken, the system should preserve the
history, mark the intervention as false-positive or unresolved, restore any
denied capability when safe, and use the record to improve future judgment.

The guardian posture is:

```text
protect first, accuse only through legitimate process
```

### 13. Speculative Future Models Are Not Mocks

The seed bank may include possible future capabilities, but they must be modeled
as low-confidence predictive structures. They are not mock facts and not current
operational assumptions.

Required fields:

```text
kind: speculative_future_model
status: low_confidence_predictive
operational_assumption: false
confidence: explicit numeric confidence
used_for: stress testing and safety planning
not_used_for: current factual claims, public authority, autonomous action
```

Examples:

- mixed classical/FTL communication routes
- retrocausal or paradox-sensitive proposal ordering
- multi-solar-system last-known state exchange
- advanced non-LLM reasoning models
- future weapons or coercive infrastructure monopolies
- local guardian-prevention capabilities not present in current deployments

Rules:

- speculative models cannot become accepted facts without evidence and promotion
  through the normal confidence lifecycle
- speculative models cannot justify live action by themselves
- speculative models must be clearly separable from scientific claims,
  legal rules, moral principles, literary cases, and current measurements
- future-model confidence can rise with evidence, but the system must preserve
  event time, discovery time, interpretation time, and confidence-at-time
- if a speculative model later becomes real, it should be superseded by a new
  evidence-backed model rather than silently relabeled

This allows HFF to prepare for possible futures without pretending those futures
are already true.

### 14. Complementarity And Tradeoff Handling

Some legitimate values cannot always be maximized at the same time. The
uncertainty principle is only an analogy here: it teaches caution around claims
of perfect simultaneous resolution, not a proof about ethics or governance.

HFF should explicitly model value pairs that can trade off:

- speed and due process
- transparency and privacy
- safety and liberty
- public knowledge and political de-escalation
- confidence and openness to challenge
- local autonomy and global coordination
- evidence preservation and data minimization

When values conflict, the system should:

- identify the values in tension
- identify the immutable constraints at risk
- state what remains uncertain
- choose the least harmful reversible action when action is needed
- preserve evidence and challenge rights
- avoid presenting the chosen tradeoff as perfect or final

This should be a first-class proposal field:

```text
tradeoff_pairs
immutable_risks
chosen_resolution
why_more_reversible_options_were_insufficient
review_required
```

This section prevents the system from hiding hard choices behind a single score.

## Design Self-Critique

This proposal is intentionally conservative. That is a strength for public
deployment, but it creates tradeoffs:

- It may slow urgent non-emergency action when evidence is politically sensitive.
- It relies on future node admission, diversity, and truth-sanctuary mechanisms
  that are not implemented yet.
- It assumes immutable constraints can be stated clearly enough to guide action,
  even though real cases will involve conflict between immutables.
- It needs a polymorphic seed graph and proposal engine before the advice/action
  layers can reason over law, literature, philosophy, science, and model types
  without flattening them into one kind of belief.
- It cannot by itself prevent a leaked screenshot or copied draft from being
  misused outside the system; it can only make misuse visibly contrary to the
  recorded status, labels, and audit trail.
- Its emergency-prevention doctrine depends on a clear boundary around
  HFF-controlled capabilities; without that boundary, "prevention" could be
  stretched into punishment.
- Its speculative future models could be socially misunderstood as predictions
  or claims unless the seed registry enforces low-confidence labels and prevents
  them from driving action.
- Its complementarity rule prevents false certainty, but it creates a burden:
  every serious action needs a visible tradeoff record, not just a confidence
  number.

The strongest unresolved risk is social misuse of output. Even if the system is
careful internally, people or agents can quote drafts out of context. Therefore
the first live version should minimize public claim surfaces and make political
drafts private, clearly labeled, and non-authoritative.

The second strongest unresolved risk is overreach under emergency framing. The
system must prove in tests and review logs that temporary capability denial is
narrow, reversible, time-bounded, and never represented as guilt.

## Validation Claims

This proposal claims only a design direction, not implemented runtime safety.

Validated in the current codebase:

- write endpoints have token gates by default
- autonomous submit currently exists and needs the proposed observe-only gate
- dashboard currently uses `innerHTML` in several places and needs safe rendering
- mesh/adoption identity exists but does not yet provide signed admitted-node
  authority
- belief lifecycle work exists on this branch, but proposal state, political
  containment, guardian prevention, coercion-aware quorum, and truth sanctuaries
  are proposal-only
- speculative future model typing, complementarity tradeoff records, and
  polymorphic seed registry enforcement are proposal-only

The proposal is valid if the implementation eventually proves:

- political/high-conflict claims cannot publish externally by default
- autonomous submissions cannot lock escalations from a single tokened request
- unadmitted nodes cannot create accepted facts or security quorum
- stale or causally contested proposal states cannot execute high-risk actions
- coercion signals reduce governance weight instead of increasing consensus
- emergency prevention can deny only specific enabling capabilities, not impose
  broad punishment
- intervention records are explicitly marked as not guilt findings and require
  review
- speculative future models cannot promote to facts or actions without evidence
- serious proposals record value tradeoffs instead of collapsing them into one
  hidden score
- all public outputs preserve uncertainty, scope, provenance, and draft status

## Proposed Implementation Order

1. Add request body, batch, string, and rate limits around all write endpoints.
2. Escape or text-render all dashboard strings derived from models, peers, or API data.
3. Add `HFF_AUTONOMY_MODE=observe_only` as the default and stop autonomous submit from locking escalations unless explicitly elevated.
4. Require accepted-fact and admitted-node gates before escalation lock.
5. Add a proposal object model with signed transition events and local last-known-state views.
6. Add political/high-conflict classification and private-draft publication gates.
7. Add guardian-prevention action types with due-process labels, time bounds, and post-event review.
8. Add signed node admission records and make mesh/adoption trust depend on them.
9. Add signed transparency events for accepted facts, immutable rule changes, node admission, proposals, and releases.
10. Add duress-aware node status, independence diversity checks, and coercion-weighted quorum rules.
11. Add truth-sanctuary replication for signed observations, proposal histories, challenges, and minority reports.
12. Add the polymorphic seed registry for laws, philosophy, literature, science, model types, and immutable constraints.
13. Add speculative future model typing and complementarity/tradeoff records to proposals.
14. Expand tests around compromised-token, public-write, rogue-peer, stale-approval, proposal-conflict, coercion, captured-node, political-leak, emergency-prevention overreach, speculative-model misuse, tradeoff omission, and output-injection scenarios.

## Non-Goals

- Do not make public forks illegal or technically impossible.
- Do not claim that GitHub branches, visible nodes, or demo traffic are authority.
- Do not let a single model, token, peer, or operator-free background loop create irreversible external action.
- Do not contact regulators, deploy services, admit nodes, rotate keys, or publish official claims without explicit grants.

## Minimal Pre-Live Bar

Before enabling public live writes or autonomous escalation, the repository
should at minimum have:

- closed-by-default write endpoints with limits
- safe dashboard rendering
- observe-only default autonomy
- accepted-fact gates tied to admitted-node confirmation
- signed proposal state transitions with stale-state protection
- political/high-conflict claims private by default with publication gates
- guardian-prevention actions that are narrow, reversible, reviewed, and not
  guilt findings
- speculative future models labeled low-confidence and barred from live action
- complementarity/tradeoff records for serious proposals
- coercion-aware quorum and node-duress status
- append-only truth-sanctuary records for challenges and minority reports
- mesh verification that requires signed admitted peers
- tests proving rogue inputs remain bounded and non-authoritative
