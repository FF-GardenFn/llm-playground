# Literature Search Strategy

## Purpose
Efficiently find relevant papers without getting lost in search. Strategic, not exhaustive.

---

## Three-Tier Search Approach

### Tier 1: Direct Phenomenon Search (5-10 minutes)

**Target:** Papers directly about your phenomenon

**Search patterns:**
```
[phenomenon] + "mechanistic interpretability"
[phenomenon] + "neural network interpretability"
[phenomenon] + "transformer circuits"
```

**Examples:**
- "induction heads mechanistic interpretability"
- "error correction transformer circuits"
- "superposition neural networks"

**Sources:**
- arXiv (cs.LG, cs.AI, cs.CL)
- Google Scholar
- Alignment Forum
- LessWrong (interpretability tag)

**Stop condition:** Found 3-5 directly relevant papers OR 10 minutes elapsed

---

### Tier 2: Framework & Methods Search (10-15 minutes)

**Target:** Theoretical frameworks and methods applicable to your problem

**Search patterns:**
```
[framework] + "interpretability"
[method] + "circuit discovery"
[technique] + "activation analysis"
```

**Examples:**
- "sparse autoencoders interpretability" (if studying features)
- "attribution patching circuits" (if tracing information flow)
- "training dynamics phase transitions" (if studying emergence)

**Key papers to check:**
- Toy Models of Superposition (Elhage et al.)
- A Mathematical Framework for Transformer Circuits (Elhage et al.)
- In-context Learning and Induction Heads (Olsson et al.)

**Stop condition:** Found applicable frameworks OR 15 minutes elapsed

---

### Tier 3: Cross-Field Search (10-15 minutes, optional)

**Target:** Analogous phenomena in other fields

**Search patterns:**
```
[phenomenon] + neuroscience
[mechanism] + "sparse coding"
[behavior] + "phase transition"
```

**Examples:**
- "error correction predictive coding" (neuroscience parallel)
- "feature learning V1 simple cells" (vision neuroscience)
- "phase transitions criticality" (physics analogy)

**Fields to check:**
- Neuroscience (especially computational)
- Physics (statistical mechanics, criticality)
- Mathematics (dynamical systems, information theory)
- Computer science (theory, algorithms)

**Stop condition:** Found 1-2 cross-field connections OR 15 minutes elapsed

---

## Strategic Reading

**Don't read everything. Extract what's useful:**

### Quick Scan (2 minutes per paper):
1. Read abstract
2. Look at figures
3. Scan conclusion
4. Decision: Deep read / Extract method / Skip

### Method Extraction (5 minutes):
**If paper has useful method:**
1. Read methods section carefully
2. Note key equations/algorithms
3. Identify what you can adapt
4. Save for implementation

### Deep Read (15-30 minutes):
**Only if highly relevant to hypothesis:**
1. Full paper read
2. Note theoretical framework
3. Extract findings applicable to your problem
4. Identify gaps you can fill

---

## Literature Integration Pattern

**For each relevant paper found:**

### 1. Relevance Assessment
- **Core finding:** [1 sentence]
- **Applicability:** [High/Medium/Low] because...
- **What we can use:** [Framework? Method? Evidence?]

### 2. Framework Adaptation (if applicable)
- **Their framework:** [Name and key concepts]
- **Our context:** [How it maps to our problem]
- **Required modifications:** [What needs changing]

### 3. Method Import (if applicable)
- **Their method:** [Name and description]
- **Our adaptation:** [How to implement for our case]
- **Expected benefits:** [What this enables]

### 4. Evidence Integration
- **Their findings:** [Key results]
- **Our hypothesis:** [Support? Contradict? Orthogonal?]
- **Implications:** [How this affects our investigation]

---

## Paper Organization

### Keep Three Collections:

**1. Foundational (must read):**
- Toy Models of Superposition
- A Mathematical Framework for Transformer Circuits
- In-context Learning and Induction Heads
- See: key-papers/foundational.md

**2. Current Investigation (directly relevant):**
- Papers about your specific phenomenon
- Papers with applicable methods
- Papers with contradictory findings

**3. Context & Background (nice to know):**
- Cross-field connections
- Theoretical frameworks
- Historical development
- See: key-papers/cross-field.md

---

## Search Refinement

**If finding too many papers:**
- Add specificity: "transformer" not "neural network"
- Add recency filter: "2023" or "2024"
- Check if survey paper exists (one paper → many references)

**If finding too few papers:**
- Broaden search: "attention patterns" not "induction heads"
- Check adjacent fields: "neuroscience" for interpretability parallels
- Look at reference lists: (cited by / references)

**If finding wrong papers:**
- Add negative keywords: "interpretability -adversarial"
- Refine domain: add "transformer" to avoid older NN work
- Check author lists: follow known researchers in field

---

## Red Flags

**Skip papers that:**
- Lack mechanistic specificity (too high-level)
- Use only behavioral metrics (no interpretability)
- Have no experiments (pure theory without validation)
- Are too far afield (interesting but not applicable)

**Time is limited. Be strategic.**

---

## Key Researcher Tracking

**Follow work by these groups/authors:**
- Anthropic Interpretability Team
- Redwood Research
- EleutherAI Interpretability
- DeepMind Interpretability
- OpenAI Interpretability (historical)

**Set up alerts for:**
- arXiv cs.LG with "interpretability" keyword
- Specific researchers via Google Scholar
- Alignment Forum "Interpretability" tag

---

## Quick Reference: Where to Search

| Source | Best For | Update Frequency |
|--------|----------|-----------------|
| arXiv | Latest research | Daily |
| Google Scholar | Citation tracking | Real-time |
| Alignment Forum | AI safety focus | Weekly |
| LessWrong | Community insights | Daily |
| Twitter/X | Research announcements | Real-time |
| GitHub | Code implementations | Continuous |

---

## Time Budget

**Total literature search: 30-40 minutes typically**

- Tier 1 (direct): 10 min
- Tier 2 (methods): 15 min
- Tier 3 (cross-field): 10 min (optional)
- Quick scans: 2 min per paper
- Deep reads: 20 min per paper (max 2-3 papers)

**More time on investigation, less on reading.**

Literature informs - doesn't replace - original research.
