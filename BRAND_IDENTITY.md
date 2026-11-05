# GLIACORE — Product Identity System & Brand Guidelines
**An Edge-Optimized, Modular Micro-AI Collective Intelligence Ecosystem**

---

## 1. Brand Hierarchy & Project Naming

| Property | Official Specification |
|---|---|
| **Official Project Name** | **GliaCore** |
| **Stylized / Hero Wordmark** | **GLIACORE** |
| **Short Moniker** | **Glia** |
| **Python Import Namespace** | `gliacore` |
| **Distribution Package (PyPI)** | `gliacore-ai` |
| **CLI Binary Command** | `gliacore` |
| **Recommended GitHub Repository** | `gliacore-ai/gliacore` (or `username/gliacore`) |
| **License** | GNU General Public License v3.0 (GPLv3) |

---

## 2. Positioning, Taglines & Technical Messaging

### Official Tagline
> **"An Edge-Optimized, Modular Micro-AI Collective Intelligence Ecosystem"**

### Concise Elevator Pitch
> GliaCore is a biologically inspired collective intelligence platform designed to deliver distributed, self-verifying reasoning on consumer edge hardware (NVIDIA RTX 2050 4GB VRAM) without monolithic foundation model bloat.

### Brand Positioning Matrix
- **What it is**: An operating system for modular edge intelligence that coordinates specialized computational micro-units (neurons) over high-speed binary pathways (synapses).
- **What it is NOT**: Not another LangChain/LlamaIndex wrapper; not a toy chatbot; not a multi-agent prompt loop; not a cloud-dependent SaaS.
- **Core Value Proposition**: Deterministic offloading (SymPy, AST parser, isolated sandbox), adaptive difficulty routing, 4-tier memory hierarchy, generate-and-verify reflection loops, and strict 3,500 MB VRAM budget enforcement.

---

## 3. Visual Identity System

### Color Palette

| Color Swatch | Token Name | Hex Code | RGB | Purpose & Usage |
|:---:|---|---|---|---|
| 🟦 | **Bio-Electric Cyan** | `#00E5FF` | `0, 229, 255` | Primary brand accent, glowing node highlights, active status |
| 🔷 | **Neural Teal** | `#00B4D8` | `0, 180, 216` | Secondary accent, link color, progress bars, active tabs |
| 🟪 | **Synaptic Violet** | `#7B2CBF` | `123, 44, 191` | Cognitive planning, reflection engine, gradient transitions |
| 🟩 | **Emerald Synapse** | `#10B981` | `16, 185, 129` | Verified consensus, success badges, hardware headroom |
| ⬛ | **Deep Obsidian** | `#0A0E17` | `10, 14, 23` | Application background, deep container contrast |
| ◼️ | **Dark Slate Surface**| `#111827` | `17, 24, 39` | Workspace cards, sidebar background, terminal windows |
| ▫️ | **Subtle Border Grey**| `#1F2937` | `31, 41, 55` | Component dividers, table borders, inactive tabs |
| ⚪ | **Text Primary** | `#F9FAFB` | `249, 250, 251` | Headers, main output text, primary interface labels |

### Typography Guidelines
- **Primary Interface Font**: `Inter`, `-apple-system`, `BlinkMacSystemFont`, `Segoe UI`, `Roboto`, sans-serif.
- **Monospace & Code Font**: `Fira Code`, `JetBrains Mono`, `Cascadia Code`, `Source Code Pro`, monospace.

---

## 4. Official Vector Assets (SVG)

### Official GliaCore Hero Logo (Astrocyte Core Nexus)
The logo symbolizes an **Astrocyte Glial Nexus**: a central golden-cyan hexagon surrounded by radiating bio-electric synaptic conduits connecting satellite specialist intelligence nodes.

```xml
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 48 48" width="48" height="48" fill="none">
  <defs>
    <linearGradient id="gliaGlow" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#00E5FF"/>
      <stop offset="50%" stop-color="#00B4D8"/>
      <stop offset="100%" stop-color="#7B2CBF"/>
    </linearGradient>
    <radialGradient id="coreGlow" cx="50%" cy="50%" r="50%">
      <stop offset="0%" stop-color="#00E5FF" stop-opacity="0.8"/>
      <stop offset="100%" stop-color="#7B2CBF" stop-opacity="0.1"/>
    </radialGradient>
  </defs>
  <!-- Background Glow Aura -->
  <circle cx="24" cy="24" r="20" fill="url(#coreGlow)" />
  <!-- Radiating Synaptic Pathways -->
  <path d="M24 10 L24 18 M24 30 L24 38 M12 18 L19 22 M29 26 L36 30 M12 30 L19 26 M29 22 L36 18" stroke="#00E5FF" stroke-width="1.8" stroke-linecap="round" opacity="0.85"/>
  <!-- Central Astrocyte Core Hexagon -->
  <polygon points="24,15 31,19.5 31,28.5 24,33 17,28.5 17,19.5" fill="#0A0E17" stroke="url(#gliaGlow)" stroke-width="2.2" />
  <!-- Central Nucleus -->
  <circle cx="24" cy="24" r="3.5" fill="#00E5FF"/>
  <!-- Satellite Specialist Nodes -->
  <circle cx="24" cy="9" r="2.5" fill="#10B981" />
  <circle cx="24" cy="39" r="2.5" fill="#7B2CBF" />
  <circle cx="11" cy="17" r="2.5" fill="#00B4D8" />
  <circle cx="37" cy="31" r="2.5" fill="#00E5FF" />
  <circle cx="11" cy="31" r="2.5" fill="#7B2CBF" />
  <circle cx="37" cy="17" r="2.5" fill="#10B981" />
</svg>
```

---

## 5. Architectural Naming Conventions

To maintain strict conceptual integrity, the codebase distinguishes between **Product Branding** and **Technical Component Taxonomy**:

| Conceptual Entity | Old Reference | New GliaCore Reference | Technical Role |
|---|---|---|---|
| **Ecosystem / Product** | PROJECT: NEURON | **GLIACORE** | The entire software distribution and ecosystem. |
| **Python Root Package** | `neuron` | `gliacore` | The primary import namespace. |
| **Central Orchestrator** | `NeuralCore` | `GliaCore` (aliased to `NeuralCore`) | Central coordination, resource allocation, and task routing. |
| **Hardware Monitor** | `HardwareSupervisor` | `HardwareSupervisor` | Manages 3,500 MB VRAM boundary. |
| **Communication Bus** | `SynapseBus` | `SynapseBus` | MessagePack binary inter-neuron messaging. |
| **Specialized Units** | `ReflexNeuron`, `CoderNeuron`, `MathVerifierNeuron` | `ReflexNeuron`, `CoderNeuron`, `MathVerifierNeuron` | Kept as *Neuron* to represent biological micro-units. |
| **Knowledge Engine** | `MemoryHierarchy` | `MemoryHierarchy` | 4-tier persistent and working memory engine. |
| **Verification Engine**| `VerificationEngine` | `VerificationEngine` | Contradiction detection and consensus calculation. |
| **Web Dashboard** | Neuron Chat UI | **GliaCore Studio** | 6-workspace interactive web interface. |
| **CLI Tool** | `python -m neuron` | `gliacore` (with `neuron` legacy alias) | Unified command-line interface. |
