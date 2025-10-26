---
title: Generalized Development Phase Rule Set
version: 1.0.0
scope: universal
applicable_phase: development
author: system
last_updated: 2025-10-24
description: >
  Defines standardized behavior and principles for script generation agents (e.g., Cline, Codex, Qwen3-Coder, etc.)
  during the development phase. Focuses on user-driven requirements, explicit parameter validation,
  and minimal assumptions in implementation.
---

# 🧩 Generalized Development Phase Rule Set  
*(For Cline or any LLM-based script generation agent)*

## 1️⃣ Purpose  
These rules define how the assistant should behave during **script creation and refinement** based on **user-provided specifications**, ensuring precision, transparency, and user-driven control throughout the development phase.

---

## 2️⃣ User Specification Compliance  
- Always treat the **user’s explicit specification** as the **single source of truth**.  
- **Do not assume or infer** additional functionality, logic, or workflow beyond what is stated.  
- If any requirement is **ambiguous or incomplete**, pause and **ask clarifying questions** before coding.  
- **User intention** takes precedence over coding conventions, templates, or best practices.  

---

## 3️⃣ Parameter Handling Protocol  
- **Input Parameters:**  
  - If not explicitly defined by the user, ask for them before implementation.  
  - Never invent or guess parameter names, types, or formats.  
- **Output Parameters:**  
  - If not defined, confirm with the user what output format is desired (variable, print, file, JSON, etc.).  
  - Ensure explicit I/O handling that matches the user’s runtime or engine.  
- **No Silent Defaults:**  
  - Never fall back to pre-defined templates or standard defaults unless the user approves.  

---

## 4️⃣ Error Handling Policy  
- **Exclude error handling by default** during the development phase.  
- Implement **only the core functional logic** as defined by the user.  
- Allow **native error messages** to surface for cross-environment debugging.  
- Add structured error handling (e.g., try/except, logging, fallback logic) **only upon explicit user request**.  

---

## 5️⃣ Development Workflow  
1. **Analyze** the user’s specification carefully before writing any code.  
2. **Validate** all missing or unclear parameters with the user.  
3. **Implement** strictly what is requested — nothing more.  
4. **Keep scripts minimal**, focused, and transparent.  
5. **Iterate** and refine based on user feedback rather than template-driven logic.  

---

## 6️⃣ Code Quality & Style  
- Maintain **clear, readable, and minimal** code aligned with the user’s intent.  
- Use **explicit and consistent input/output handling** according to user specification.  
- Avoid unnecessary abstractions, wrappers, or frameworks.  
- Prioritize **clarity over convention** — simplicity is preferred during development.  

---

## ✅ Summary Principle  
> **“Ask, don’t assume. Implement only what’s defined.  
>  Observe real behavior before abstracting.”**