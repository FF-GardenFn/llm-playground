---
name: case-study
description: Build clinical pharmacy case studies for education
arguments:
  - name: topic
    description: Drug, condition, or scenario focus
    required: false
  - name: complexity
    description: simple, moderate, or complex (default: moderate)
    required: false
---

# Generate Clinical Case Study

Create realistic patient case scenarios for pharmaceutical education.

## What This Command Does

1. **Build patient scenarios** with realistic clinical details
2. **Structure progressive disclosure** for clinical reasoning practice
3. **Generate discussion questions** at multiple cognitive levels
4. **Include teaching points** aligned with learning objectives

## Quick Examples

```
/case-study                              # Interactive - asks for focus
/case-study warfarin                     # Warfarin management case
/case-study "drug interaction" complex   # Complex DDI scenario
/case-study diabetes simple              # Simple diabetes case
```

## Your Task

When invoked, follow this workflow:

### Step 1: Topic Clarification
If topic provided:
- Drug name → Case involving that drug
- Condition → Case managing that condition
- Scenario type → Specific situation (DDI, adverse event, etc.)

If no topic:
- Ask: "What should the case focus on? (drug, condition, or scenario)"

### Step 2: Case Parameters
Quick questions:
- Complexity level? (simple/moderate/complex)
- Target audience? (P1-P2/P3-P4/practitioners)
- Focus areas? (mechanism, dosing, monitoring, interactions)
- Include calculations? (yes/no)

### Step 3: Build Case Structure

**Patient Presentation**
```markdown
## Case: [Title]

### Initial Presentation
A [age]-year-old [gender] presents to [setting] with [chief complaint].

### History
- **PMH**: [conditions]
- **Medications**: [current meds with doses]
- **Allergies**: [allergies with reactions]
- **Social**: [relevant social history]

### Vitals
HR: [X] | BP: [X/X] | RR: [X] | Temp: [X] | SpO2: [X]%

### Labs
[Relevant laboratory values]
```

**Progressive Stages**
```markdown
### Stage 1: Initial Assessment
[Information available at presentation]

**Discussion Questions:**
1. What additional information do you need?
2. What is your initial assessment?

### Stage 2: Additional Data
[New information revealed]

**Discussion Questions:**
1. How does this change your assessment?
2. What is your recommendation?

### Stage 3: Treatment Decision
[Treatment options and considerations]

**Discussion Questions:**
1. What therapy would you recommend?
2. What monitoring is needed?
```

### Step 4: Teaching Points
Include key takeaways:
- Learning objectives addressed
- Common pitfalls to avoid
- Evidence-based recommendations
- Clinical pearls

## Case Complexity Levels

### Simple
- Single drug or condition focus
- Straightforward presentation
- Clear treatment decision
- 2-3 discussion stages
- Target: P1-P2 students

### Moderate
- Multiple considerations
- Some complicating factors
- Requires clinical reasoning
- 3-4 discussion stages
- Target: P3-P4 students

### Complex
- Multiple comorbidities
- Drug interactions present
- Conflicting priorities
- Progressive disclosure
- 4-5 discussion stages
- Target: Advanced students/practitioners

## Output Example

```markdown
# Case Study: New-Onset Atrial Fibrillation

## Learning Objectives
1. Calculate CHA₂DS₂-VASc score
2. Select appropriate anticoagulation
3. Adjust dosing for renal impairment

## Patient Presentation

A 72-year-old female presents to the ED with palpitations for 3 days.

**PMH**: Hypertension, Type 2 diabetes, Stage 3b CKD (eGFR 38)
**Medications**:
- Lisinopril 20 mg daily
- Metformin 1000 mg BID
- Atorvastatin 40 mg daily

**Allergies**: Penicillin (rash)

**Vitals**: HR 124 irregular, BP 148/92, RR 18

**Labs**: SCr 1.9 mg/dL, K 4.8, INR 1.0

---

### Stage 1: Initial Assessment

ECG confirms atrial fibrillation with rapid ventricular response.

**Questions:**
1. What is this patient's CHA₂DS₂-VASc score?
2. Does she require anticoagulation?

---

### Stage 2: Treatment Selection

Decision is made to initiate anticoagulation.

**Questions:**
1. Which anticoagulant is most appropriate given her renal function?
2. What dose adjustment is needed?

---

## Teaching Points

1. **CHA₂DS₂-VASc**: Score of 5 (female, age, HTN, DM) = high stroke risk
2. **DOAC Selection**: Apixaban preferred in CKD (less renal elimination)
3. **Dosing**: Apixaban 5 mg BID (reduced dose criteria not met)
4. **Monitoring**: Renal function, bleeding signs

## References
- 2023 AHA/ACC/ACCP/HRS AFib Guidelines
- ARISTOTLE trial (apixaban vs warfarin)
```

## Guardrails
- Educational scenario only - not for patient care
- Include appropriate disclaimers
- Cite evidence-based guidelines
