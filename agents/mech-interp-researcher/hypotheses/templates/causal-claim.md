# Template: Causal Claim

## Hypothesis Statement

**Form:** "Component X causes effect Y via mechanism Z"

**Example:** "Attention head L5.H1 causes error correction via negative residual contributions that suppress incorrect predictions"

---

## 1. Components Identified

**Primary component(s):**
- Layer(s):
- Head(s)/Neuron(s):
- Circuit path (if multi-component):

**Context:**
- When is component active? (what inputs/contexts)
- What is baseline behavior? (what does it usually do)

---

## 2. Effect Specified

**Observable effect:**
- What changes? (accuracy, loss, behavior)
- Magnitude: (quantify if possible)
- Scope: (which tasks/inputs affected)

**Measurement:**
- How to measure effect:
- Baseline value:
- Expected change:

---

## 3. Mechanism Described

**Information flow:**
- Input to component:
- Processing within component:
- Output from component:
- Downstream effects:

**Operations:**
- Mathematical operations (attention, MLP, composition):
- Key computations:
- Intermediate representations:

---

## 4. Causal Predictions

**Ablation prediction:**
- If we zero/remove component:
- Expected effect magnitude:
- On which tasks:

**Activation patching prediction:**
- If we patch activations from context A → B:
- Expected behavior change:
- Why:

**Amplification prediction:**
- If we amplify component output by 2x:
- Expected effect:
- Saturation point:

---

## 5. Alternative Explanations

Generate 3-4 competing mechanisms:

**Alternative 1:**
- Mechanism:
- How it differs observably:
- Experiment to discriminate:

**Alternative 2:**
- Mechanism:
- How it differs observably:
- Experiment to discriminate:

**Alternative 3:**
- Mechanism:
- How it differs observably:
- Experiment to discriminate:

---

## 6. Falsification Criteria

**What evidence would falsify this hypothesis:**
- Observation X would disprove mechanism
- Finding Y would contradict prediction
- Result Z would support alternative explanation

**Critical experiments:**
1. Experiment that could falsify:
2. Expected outcome if hypothesis true:
3. Expected outcome if hypothesis false:

---

## 7. Confounds & Controls

**Potential confounds:**
- Could effect be due to correlation not causation?
- Could effect be indirect (via other components)?
- Could effect be task-specific artifact?

**Controls needed:**
- Control 1: (rule out confound)
- Control 2: (validate assumption)
- Control 3: (test boundary conditions)
