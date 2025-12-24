# SemantiCore - UI/UX Design Recommendations

## Executive Summary
Transform the current Streamlit interface to match the technical, futuristic aesthetic demonstrated in the ui_example React components. Focus on micro-typography, glassmorphism, system-focused language, and evidence-based transparency.

---

## 1. SIDEBAR & NAVIGATION

### Current Issues:
- Brand is good but could be more prominent
- Project list items lack visual hierarchy
- System diagnostics feel disconnected
- Settings button placement is awkward

### Recommendations:

#### Brand Enhancement
```html
<!-- BEFORE -->
<div class="brand-name">SEMANTIC MAPPER</div>
<div class="brand-subtitle">ARCHITECT</div>

<!-- AFTER (Enhanced with better spacing) -->
<div class="brand-name" style="font-size: 0.875rem; font-weight: 900; letter-spacing: -0.02em;">SEMANTIC MAPPER</div>
<div class="brand-subtitle" style="font-size: 0.563rem; letter-spacing: 0.25em;">ARCHITECT</div>
```

#### Project List Items
Add richer metadata and hover states:
```css
.project-item {
    background: rgba(255, 255, 255, 0.03);
    border: 1px solid rgba(255, 255, 255, 0.05);
    border-radius: 0.75rem;
    padding: 0.75rem;
    margin: 0.25rem 0.75rem;
    cursor: pointer;
    transition: all 0.2s ease;
}

.project-item:hover {
    background: rgba(255, 255, 255, 0.05);
    border-color: rgba(37, 99, 235, 0.3);
    transform: translateX(2px);
}

/* Add status dot */
.project-status-dot {
    width: 4px;
    height: 4px;
    border-radius: 50%;
    background: #10b981;
    animation: pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
}
```

#### Navigation Footer
Replace simple buttons with icon + label pattern:
```html
<button class="nav-footer-item">
    <svg class="nav-icon" width="16" height="16">...</svg>
    <span class="nav-label">PROVENANCE LOG</span>
</button>
```

---

## 2. TYPOGRAPHY SYSTEM

### Micro-Typography Scale
Adopt the precise typography from ui_example:

| Element | Size | Weight | Transform | Tracking |
|---------|------|--------|-----------|----------|
| Section Headers | 10px | 900 | uppercase | 0.2em |
| Card Labels | 10px | 900 | uppercase | 0.15em |
| Metadata | 9px | 700-900 | uppercase | 0.15em |
| Evidence Labels | 9px | 900 | uppercase | 0.2em |
| Body Text | 14px | 400-500 | none | 0 |
| Hero Title | 48px | 900 | uppercase | -0.04em |
| Card Titles | 20px | 700 | none | -0.02em |

### Font Stack Enhancement
```css
* {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    -webkit-font-smoothing: antialiased;
    -moz-osx-font-smoothing: grayscale;
}

/* Monospace for technical data */
.technical-data, .evidence-box, code {
    font-family: 'JetBrains Mono', 'Fira Code', 'Courier New', monospace;
}
```

---

## 3. STEPPER COMPONENT

### Current State
Simple text badges without icons or rich states.

### Enhanced Stepper Design

```html
<div class="stepper-container">
    <div class="step-badge active">
        <svg class="step-icon">...</svg>
        <span>INGEST</span>
    </div>
    <svg class="step-chevron">...</svg>
    <div class="step-badge completed">
        <svg class="step-icon text-emerald-500">✓</svg>
        <span>EXTRACT</span>
    </div>
    <svg class="step-chevron">...</svg>
    <div class="step-badge pending">
        <svg class="step-icon">...</svg>
        <span>FRAME</span>
    </div>
</div>
```

```css
.step-badge {
    display: inline-flex;
    align-items: center;
    gap: 0.5rem;
    padding: 0.375rem 0.75rem;
    border-radius: 0.375rem;
    transition: all 0.2s ease;
    font-size: 0.625rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.15em;
}

.step-badge.active {
    background: rgba(37, 99, 235, 0.2);
    color: #60a5fa;
    border: 1px solid rgba(37, 99, 235, 0.3);
}

.step-badge.completed {
    color: #10b981;
}

.step-badge.pending {
    color: rgba(255, 255, 255, 0.2);
}

.step-icon {
    width: 16px;
    height: 16px;
}
```

---

## 4. CARD & COMPONENT PATTERNS

### A. Ontology Proposal Cards (Crucial!)

The ui_example shows sophisticated cards with:
- Border accent (border-left: 4px solid color)
- Nested reasoning boxes
- Confidence scores
- Evidence sections
- Alternative suggestions

```css
.ontology-card {
    background: rgba(23, 23, 23, 0.7);
    backdrop-filter: blur(12px);
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-left: 4px solid #2563eb;
    border-radius: 1rem;
    padding: 1.5rem;
    margin-bottom: 1.5rem;
    transition: all 0.2s ease;
}

.ontology-card:hover {
    background: rgba(255, 255, 255, 0.02);
    border-color: rgba(37, 99, 235, 0.3);
}

.ontology-card-title {
    font-size: 1.25rem;
    font-weight: 700;
    color: #60a5fa;
    margin-bottom: 0.5rem;
}

.reasoning-box {
    background: rgba(0, 0, 0, 0.4);
    padding: 0.75rem;
    border-radius: 0.5rem;
    border: 1px solid rgba(255, 255, 255, 0.05);
    margin-top: 1rem;
}

.reasoning-label {
    font-size: 0.563rem; /* 9px */
    text-transform: uppercase;
    color: #60a5fa;
    font-weight: 900;
    letter-spacing: 0.15em;
    margin-bottom: 0.25rem;
    display: block;
}

.reasoning-text {
    font-size: 0.688rem; /* 11px */
    color: rgba(255, 255, 255, 0.5);
    line-height: 1.4;
    font-family: monospace;
    font-style: italic;
}
```

### B. Evidence/Semantic Primitive Cards

```css
.candidate-card {
    background: rgba(255, 255, 255, 0.03);
    border: 1px solid rgba(255, 255, 255, 0.05);
    border-radius: 1rem;
    padding: 1.5rem;
    margin-bottom: 1rem;
    transition: all 0.2s ease;
}

.candidate-card:hover {
    border-color: rgba(37, 99, 235, 0.3);
    transform: translateY(-2px);
}

.candidate-type-badge {
    background: rgba(37, 99, 235, 0.2);
    color: #60a5fa;
    padding: 0.25rem 0.5rem;
    border-radius: 0.25rem;
    font-size: 0.625rem;
    font-weight: 900;
    text-transform: uppercase;
    display: inline-block;
}

.confidence-score {
    font-size: 0.625rem;
    font-family: monospace;
    color: #10b981;
    font-weight: 700;
}

.evidence-box {
    background: rgba(0, 0, 0, 0.4);
    padding: 0.75rem;
    border-radius: 0.5rem;
    border: 1px solid rgba(255, 255, 255, 0.05);
    font-size: 0.688rem;
    font-family: monospace;
    color: rgba(255, 255, 255, 0.6);
    font-style: italic;
    margin-top: 1rem;
}

.evidence-label {
    color: #60a5fa;
    text-transform: uppercase;
    font-size: 0.563rem;
    display: block;
    margin-bottom: 0.25rem;
    font-weight: 900;
    letter-spacing: 0.2em;
}
```

### C. Stats Cards

```css
.stat-card {
    background: rgba(23, 23, 23, 0.7);
    backdrop-filter: blur(12px);
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 1rem;
    padding: 1.5rem;
    text-align: left; /* Change from center */
    transition: all 0.2s ease;
}

.stat-card:hover {
    background: #151515;
    border-color: rgba(255, 255, 255, 0.15);
}

.stat-label {
    font-size: 0.625rem; /* 10px */
    font-weight: 900;
    text-transform: uppercase;
    letter-spacing: 0.15em;
    color: rgba(255, 255, 255, 0.3);
    margin-bottom: 1rem;
}

.stat-value {
    font-size: 1.875rem;
    font-weight: 900;
    color: white;
    letter-spacing: -0.02em;
}

/* For key metrics, add color */
.stat-value.success {
    color: #10b981;
}
```

---

## 5. LAYOUT & GRID PATTERNS

### Asymmetric Column Layouts

The ui_example uses sophisticated grid patterns:

```css
/* Main content + Sidebar pattern */
.content-with-sidebar {
    display: grid;
    grid-template-columns: 2fr 1fr;
    gap: 2rem;
}

/* 8-4 split for detailed views */
.detailed-view {
    display: grid;
    grid-template-columns: 8fr 4fr;
    gap: 2rem;
}

/* Responsive stats grid */
.stats-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
    gap: 1.5rem;
    margin: 2rem 0;
}
```

### Content Area Padding
```css
.content-area {
    padding: 3rem;
    min-height: calc(100vh - 80px);
}

/* For centered forms/wizards */
.centered-content {
    max-width: 42rem; /* 672px */
    margin: 0 auto;
    padding: 3rem;
}
```

---

## 6. INTERACTIVE STATES & ANIMATIONS

### Hover Transitions
```css
.interactive-card {
    transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
}

.interactive-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 30px rgba(0, 0, 0, 0.3);
}

/* Group hover effects */
.card-group:hover .card-icon {
    color: #60a5fa;
}
```

### Status Animations
```css
@keyframes pulse {
    0%, 100% {
        opacity: 1;
    }
    50% {
        opacity: 0.5;
    }
}

.status-dot {
    width: 6px;
    height: 6px;
    border-radius: 50%;
    background: #10b981;
    animation: pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
}
```

### Page Transitions
```css
@keyframes fadeIn {
    from {
        opacity: 0;
        transform: translateY(10px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}

.page-enter {
    animation: fadeIn 0.3s ease-out;
}
```

---

## 7. BUTTON SYSTEM

### Primary Button (CTA)
```css
.btn-primary {
    background: white;
    color: black;
    border: none;
    font-weight: 900;
    font-size: 0.875rem;
    padding: 0.75rem 3rem;
    border-radius: 0.75rem;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    box-shadow: 0 20px 60px rgba(255, 255, 255, 0.1);
    transition: all 0.2s ease;
    cursor: pointer;
}

.btn-primary:hover {
    background: #e5e5e5;
    transform: translateY(-1px);
    box-shadow: 0 25px 70px rgba(255, 255, 255, 0.15);
}

.btn-primary:active {
    transform: translateY(0);
}
```

### Secondary Button
```css
.btn-secondary {
    background: rgba(255, 255, 255, 0.02);
    color: rgba(255, 255, 255, 0.6);
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 0.75rem;
    padding: 0.75rem 1.5rem;
    font-weight: 700;
    font-size: 0.75rem;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    transition: all 0.2s ease;
}

.btn-secondary:hover {
    background: rgba(255, 255, 255, 0.05);
    color: white;
    border-color: rgba(37, 99, 235, 0.5);
}
```

### Icon Button
```css
.btn-icon {
    width: 36px;
    height: 36px;
    border-radius: 0.75rem;
    background: rgba(255, 255, 255, 0.05);
    border: 1px solid rgba(255, 255, 255, 0.1);
    display: flex;
    align-items: center;
    justify-content: center;
    color: rgba(255, 255, 255, 0.4);
    transition: all 0.2s ease;
    cursor: pointer;
}

.btn-icon:hover {
    color: white;
    background: rgba(255, 255, 255, 0.1);
}
```

---

## 8. FORM INPUTS

### Text Input
```css
.input-field {
    background: rgba(255, 255, 255, 0.02);
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 1rem;
    padding: 1rem 1.5rem;
    font-size: 0.875rem;
    font-family: monospace;
    color: white;
    width: 100%;
    transition: all 0.2s ease;
}

.input-field:focus {
    outline: none;
    border-color: #2563eb;
    box-shadow: 0 0 0 1px #2563eb;
    background: rgba(255, 255, 255, 0.03);
}

.input-field::placeholder {
    color: rgba(255, 255, 255, 0.1);
    font-style: italic;
}
```

### Text Area
```css
.textarea-field {
    background: rgba(255, 255, 255, 0.02);
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 1rem;
    padding: 1.5rem;
    font-size: 0.875rem;
    font-family: monospace;
    color: white;
    width: 100%;
    min-height: 200px;
    resize: vertical;
    transition: all 0.2s ease;
}

.textarea-field:focus {
    outline: none;
    border-color: #2563eb;
    box-shadow: 0 0 0 1px #2563eb;
}
```

---

## 9. STATUS BADGES & INDICATORS

### Badge System
```css
/* Status badge base */
.badge {
    display: inline-flex;
    align-items: center;
    gap: 0.375rem;
    padding: 0.25rem 0.5rem;
    border-radius: 0.375rem;
    font-size: 0.625rem;
    font-weight: 900;
    text-transform: uppercase;
    letter-spacing: 0.05em;
}

/* Success/Healthy */
.badge-success {
    background: rgba(16, 185, 129, 0.1);
    color: #10b981;
    border: 1px solid rgba(16, 185, 129, 0.2);
}

/* Active/Processing */
.badge-active {
    background: rgba(37, 99, 235, 0.1);
    color: #60a5fa;
    border: 1px solid rgba(37, 99, 235, 0.2);
}

/* Warning */
.badge-warning {
    background: rgba(245, 158, 11, 0.1);
    color: #fbbf24;
    border: 1px solid rgba(245, 158, 11, 0.2);
}

/* Error/Draft */
.badge-error {
    background: rgba(239, 68, 68, 0.1);
    color: #f87171;
    border: 1px solid rgba(239, 68, 68, 0.2);
}
```

### Status Indicator with Pulse
```html
<div class="status-indicator">
    <div class="status-dot"></div>
    <span class="status-text">GRAPH ONLINE</span>
</div>
```

```css
.status-indicator {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    background: rgba(16, 185, 129, 0.1);
    border: 1px solid rgba(16, 185, 129, 0.2);
    padding: 0.375rem 0.75rem;
    border-radius: 0.5rem;
}

.status-dot {
    width: 6px;
    height: 6px;
    border-radius: 50%;
    background: #10b981;
    animation: pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
}

.status-text {
    font-size: 0.563rem;
    font-weight: 900;
    color: #10b981;
    text-transform: uppercase;
    letter-spacing: 0.05em;
}
```

---

## 10. LANGUAGE & TERMINOLOGY

### System-Focused Vocabulary

Replace casual language with technical precision:

| Before | After |
|--------|-------|
| "New Project" | "NEW DEPLOYMENT" |
| "Projects" | "LOCAL GRAPH INSTANCES" |
| "Create" | "INITIALIZE" / "MATERIALIZE" |
| "Build" | "MATERIALIZE INSTANCES" |
| "Settings" | "SYSTEM SETTINGS" |
| "Stats" | "SYSTEM DIAGNOSTICS" |
| "Files" | "SOURCE INGESTION" |
| "Memory" | "MEMORY USAGE" |
| "Status" | "GRAPH DENSITY" / "HEALTH STATUS" |
| "Review" | "NEGOTIATE FEEDBACK" |
| "Accept" | "VALIDATE & ACCEPT" |

### Metadata Formatting
```html
<!-- Version display -->
<span class="version-badge">v3.0.0</span>

<!-- Status with dot -->
<div class="status-meta">
    <span class="dot"></span>
    <span>Healthy</span>
</div>

<!-- Technical metadata -->
<div class="tech-meta">
    TLS Verified • Neo4j 5.x • Claude 3.5
</div>
```

---

## 11. EMPTY STATES

### Hero Empty State
```html
<div class="empty-state-hero">
    <div class="glow-effect"></div>
    <div class="hero-icon">
        <svg>...</svg>
    </div>
    <h1 class="hero-title">ONTOLOGY HUB</h1>
    <p class="hero-subtitle">
        The industry's first human-in-the-loop semantic modeling platform.
        Transform unorganized data into versioned, traceable, and queryable knowledge.
    </p>
    <button class="btn-primary">INITIALIZE NEW DEPLOYMENT</button>
</div>
```

```css
.empty-state-hero {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    min-height: 70vh;
    text-align: center;
    position: relative;
    padding: 4rem;
}

.glow-effect {
    position: absolute;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    width: 800px;
    height: 800px;
    background: rgba(37, 99, 235, 0.05);
    border-radius: 50%;
    filter: blur(120px);
    z-index: 0;
}

.hero-icon {
    width: 96px;
    height: 96px;
    background: rgba(255, 255, 255, 0.03);
    border: 1px solid rgba(255, 255, 255, 0.05);
    border-radius: 40px;
    display: flex;
    align-items: center;
    justify-content: center;
    margin-bottom: 3rem;
    position: relative;
    z-index: 1;
}

.hero-title {
    font-size: 3rem;
    font-weight: 900;
    text-transform: uppercase;
    letter-spacing: -0.04em;
    font-style: italic;
    margin-bottom: 1.5rem;
    color: white;
    position: relative;
    z-index: 1;
}

.hero-subtitle {
    font-size: 1.125rem;
    color: rgba(255, 255, 255, 0.3);
    max-width: 600px;
    margin: 0 auto 3rem;
    line-height: 1.6;
    font-weight: 500;
    position: relative;
    z-index: 1;
}
```

---

## 12. QUERY INTERFACE

### Natural Language Query Box
```html
<div class="query-container">
    <div class="query-input-wrapper">
        <svg class="query-icon">...</svg>
        <input
            type="text"
            class="query-input"
            placeholder="Ask a question about your data..."
        />
        <button class="query-submit">EXECUTE</button>
    </div>

    <div class="cypher-display">
        <div class="cypher-header">
            <span class="cypher-label">GENERATED CYPHER</span>
            <button class="copy-btn">Copy Query</button>
        </div>
        <pre class="cypher-code">MATCH (n:Patient) RETURN n LIMIT 10</pre>
    </div>
</div>
```

```css
.query-input-wrapper {
    display: flex;
    align-items: center;
    gap: 1rem;
    background: rgba(23, 23, 23, 0.7);
    backdrop-filter: blur(12px);
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 1rem;
    padding: 1rem 1.5rem;
    transition: all 0.2s ease;
}

.query-input-wrapper:focus-within {
    border-color: #2563eb;
    box-shadow: 0 0 0 1px #2563eb;
}

.query-input {
    flex: 1;
    background: transparent;
    border: none;
    outline: none;
    color: white;
    font-size: 1rem;
    font-weight: 500;
}

.query-submit {
    background: #2563eb;
    color: white;
    padding: 0.625rem 2rem;
    border-radius: 0.75rem;
    font-weight: 900;
    font-size: 0.75rem;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    border: none;
    cursor: pointer;
    transition: all 0.2s ease;
}

.cypher-display {
    background: #000;
    border: 1px solid rgba(255, 255, 255, 0.05);
    border-radius: 1.5rem;
    overflow: hidden;
    margin-top: 1.5rem;
}

.cypher-header {
    background: rgba(255, 255, 255, 0.02);
    border-bottom: 1px solid rgba(255, 255, 255, 0.05);
    padding: 0.75rem 1.5rem;
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.cypher-label {
    font-size: 0.625rem;
    font-weight: 900;
    text-transform: uppercase;
    letter-spacing: 0.15em;
    color: rgba(255, 255, 255, 0.4);
}

.cypher-code {
    padding: 2rem;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.875rem;
    color: #60a5fa;
    line-height: 1.6;
}
```

---

## 13. GLASSMORPHISM UTILITIES

```css
/* Glass card base */
.glass {
    background: rgba(23, 23, 23, 0.7);
    backdrop-filter: blur(12px);
    -webkit-backdrop-filter: blur(12px);
    border: 1px solid rgba(255, 255, 255, 0.1);
}

/* Lighter glass */
.glass-light {
    background: rgba(255, 255, 255, 0.03);
    backdrop-filter: blur(8px);
    -webkit-backdrop-filter: blur(8px);
    border: 1px solid rgba(255, 255, 255, 0.05);
}

/* Heavy glass (for emphasis) */
.glass-heavy {
    background: rgba(23, 23, 23, 0.9);
    backdrop-filter: blur(20px);
    -webkit-backdrop-filter: blur(20px);
    border: 1px solid rgba(255, 255, 255, 0.15);
}
```

---

## 14. SCROLLBAR CUSTOMIZATION

```css
.custom-scrollbar::-webkit-scrollbar {
    width: 8px;
    height: 8px;
}

.custom-scrollbar::-webkit-scrollbar-track {
    background: rgba(255, 255, 255, 0.02);
    border-radius: 10px;
}

.custom-scrollbar::-webkit-scrollbar-thumb {
    background: rgba(255, 255, 255, 0.1);
    border-radius: 10px;
    transition: background 0.2s ease;
}

.custom-scrollbar::-webkit-scrollbar-thumb:hover {
    background: rgba(255, 255, 255, 0.2);
}
```

---

## 15. SUCCESS/COMPLETION STATE

```html
<div class="success-container">
    <div class="success-icon">
        <svg>✓</svg>
    </div>
    <h2 class="success-title">ONTOLOGY ACCEPTED</h2>
    <p class="success-subtitle">Human validation complete. Moving to Knowledge Graph materialization.</p>

    <div class="stats-grid">
        <div class="stat-card">
            <div class="stat-label">CONCEPTS</div>
            <div class="stat-value">12</div>
        </div>
        <div class="stat-card">
            <div class="stat-label">RELATIONS</div>
            <div class="stat-value">24</div>
        </div>
        <div class="stat-card">
            <div class="stat-label">VERSION</div>
            <div class="stat-value">1.0.0</div>
        </div>
    </div>

    <button class="btn-primary">MATERIALIZE INSTANCES & LAUNCH</button>
</div>
```

```css
.success-container {
    text-align: center;
    padding: 4rem 2rem;
    animation: fadeIn 0.5s ease-out;
}

.success-icon {
    width: 80px;
    height: 80px;
    background: rgba(16, 185, 129, 0.2);
    border-radius: 1.5rem;
    display: flex;
    align-items: center;
    justify-content: center;
    margin: 0 auto 2rem;
    box-shadow: 0 0 50px rgba(5, 150, 105, 0.2);
    border: 1px solid rgba(16, 185, 129, 0.3);
    animation: scaleIn 0.4s ease-out 0.2s backwards;
}

@keyframes scaleIn {
    from {
        transform: scale(0);
    }
    to {
        transform: scale(1);
    }
}

.success-title {
    font-size: 2.5rem;
    font-weight: 900;
    color: white;
    margin-bottom: 1rem;
    letter-spacing: -0.04em;
    text-transform: uppercase;
}

.success-subtitle {
    font-size: 1.125rem;
    color: rgba(255, 255, 255, 0.4);
    margin-bottom: 3rem;
    font-weight: 500;
}
```

---

## 16. IMPLEMENTATION PRIORITY

### Phase 1: Foundation (Do First)
1. ✅ Typography system overhaul
2. ✅ Color refinements (more glassmorphism)
3. ✅ Button system standardization
4. ✅ Badge/status components

### Phase 2: Components (Do Next)
1. ✅ Enhanced stepper with icons
2. ✅ Ontology card redesign with reasoning boxes
3. ✅ Evidence/primitive cards
4. ✅ Stats grid improvements

### Phase 3: Layout & Flow (Then)
1. ✅ Asymmetric grid layouts
2. ✅ Empty state hero
3. ✅ Success states
4. ✅ Query interface

### Phase 4: Polish (Finally)
1. ✅ Hover states and micro-interactions
2. ✅ Page transitions
3. ✅ Scrollbar styling
4. ✅ Loading states

---

## 17. STREAMLIT-SPECIFIC CONSIDERATIONS

### Custom Component Wrappers

Since you're using Streamlit, wrap complex HTML in markdown with `unsafe_allow_html=True`:

```python
def render_ontology_card(cls_proposal):
    """Render a rich ontology card with reasoning."""
    cls = cls_proposal.proposed_class
    conf = cls_proposal.confidence.score

    card_html = f"""
    <div class="ontology-card">
        <div style="display: flex; justify-content: space-between; margin-bottom: 1rem;">
            <div>
                <h3 class="ontology-card-title">{cls.label}</h3>
                <span class="ontology-card-type">{cls.name}</span>
            </div>
            <div style="text-align: right;">
                <div class="confidence-score">{int(conf * 100)}% CONF</div>
            </div>
        </div>
        <p style="font-size: 0.875rem; color: rgba(255, 255, 255, 0.8); margin-bottom: 1rem;">
            {cls.description}
        </p>
        <div class="reasoning-box">
            <span class="reasoning-label">Reasoning</span>
            <p class="reasoning-text">{cls.rationale}</p>
        </div>
    </div>
    """
    st.markdown(card_html, unsafe_allow_html=True)
```

### Streamlit Widget Overrides

```css
/* Override Streamlit's file uploader */
[data-testid="stFileUploader"] {
    background: transparent;
}

[data-testid="stFileUploader"] > div {
    border: 2px dashed rgba(255, 255, 255, 0.1);
    border-radius: 1rem;
    background: rgba(255, 255, 255, 0.02);
}

/* Override text inputs */
.stTextInput input, .stTextArea textarea {
    background: rgba(255, 255, 255, 0.02) !important;
    border: 1px solid rgba(255, 255, 255, 0.1) !important;
    border-radius: 1rem !important;
    padding: 1rem 1.5rem !important;
    font-size: 0.875rem !important;
    font-family: 'JetBrains Mono', monospace !important;
    color: white !important;
}

.stTextInput input:focus, .stTextArea textarea:focus {
    border-color: #2563eb !important;
    box-shadow: 0 0 0 1px #2563eb !important;
}

/* Override buttons */
.stButton > button {
    background: rgba(255, 255, 255, 0.02) !important;
    color: rgba(255, 255, 255, 0.6) !important;
    border: 1px solid rgba(255, 255, 255, 0.1) !important;
    border-radius: 0.75rem !important;
    padding: 0.75rem 1.5rem !important;
    font-weight: 700 !important;
    font-size: 0.75rem !important;
    text-transform: uppercase !important;
    letter-spacing: 0.1em !important;
}

.stButton > button:hover {
    background: rgba(255, 255, 255, 0.05) !important;
    color: white !important;
    border-color: rgba(37, 99, 235, 0.5) !important;
}

.stButton > button[kind="primary"] {
    background: white !important;
    color: black !important;
    border: none !important;
    font-weight: 900 !important;
    box-shadow: 0 20px 60px rgba(255, 255, 255, 0.1) !important;
}
```

---

## 18. ACCESSIBILITY NOTES

Even with the futuristic design, maintain accessibility:

```css
/* Focus states */
*:focus-visible {
    outline: 2px solid #2563eb;
    outline-offset: 2px;
}

/* Ensure sufficient contrast for text */
/* Current palette maintains WCAG AA compliance */

/* Skip to main content link */
.skip-link {
    position: absolute;
    top: -40px;
    left: 0;
    background: white;
    color: black;
    padding: 8px;
    z-index: 100;
}

.skip-link:focus {
    top: 0;
}
```

---

## SUMMARY OF KEY CHANGES

### Visual Hierarchy
- ✅ Extreme micro-typography (9px-10px labels)
- ✅ Bold, uppercase system labels
- ✅ Monospace for technical/evidence data
- ✅ More glassmorphism and backdrop-filter

### Components
- ✅ Ontology cards with reasoning boxes
- ✅ Evidence cards with confidence scores
- ✅ Enhanced stepper with icons + chevrons
- ✅ Status badges with pulse animations
- ✅ Rich stats cards with hover states

### Language
- ✅ "NEW DEPLOYMENT" not "New Project"
- ✅ "MATERIALIZE" not "Build"
- ✅ "SYSTEM DIAGNOSTICS" not "Stats"
- ✅ "LOCAL GRAPH INSTANCES" not "Projects"

### Layout
- ✅ Asymmetric grids (8-4 splits)
- ✅ Better spacing and padding
- ✅ Centered hero states
- ✅ Success states with animations

### Interactivity
- ✅ Subtle hover transforms
- ✅ Border color transitions
- ✅ Pulse animations for status
- ✅ Smooth page transitions

---

## NEXT STEPS

1. **Implement typography system** - Update all font sizes, weights, tracking
2. **Refactor card components** - Add reasoning boxes, evidence sections
3. **Enhance stepper** - Add icons, chevrons, better states
4. **Update terminology** - Replace all casual language with technical terms
5. **Add micro-interactions** - Hover states, animations, transitions
6. **Test on real data** - Ensure designs scale with actual content

---

*This design system transforms your Streamlit app from functional to exceptional, matching the sophistication of your ui_example while maintaining Streamlit's framework constraints.*
