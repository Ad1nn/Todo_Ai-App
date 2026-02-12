# Research: UI/UX Enhancement with ChatKit

**Feature**: 004-ui-ux-enhancement
**Date**: 2026-01-30
**Status**: Complete

## Research Questions

1. How to integrate OpenAI ChatKit with existing Next.js app?
2. What theming/customization options does ChatKit provide?
3. What backend changes are needed for ChatKit integration?
4. How to implement dark mode with ChatKit?

---

## 1. OpenAI ChatKit Integration

### Decision: Use @openai/chatkit-react package

**Package**: `@openai/chatkit-react`

**Installation**:
```bash
npm install @openai/chatkit-react
```

**CDN Requirement** (add to layout.tsx):
```html
<script
  src="https://cdn.platform.openai.com/deployments/chatkit/chatkit.js"
  async
/>
```

### Basic Integration Pattern

```tsx
import { ChatKit, useChatKit } from '@openai/chatkit-react';

export function TaskChat() {
  const { control } = useChatKit({
    api: {
      async getClientSecret(existing) {
        // Refresh session if existing
        if (existing) {
          const res = await fetch('/api/chatkit/refresh', { method: 'POST' });
          return (await res.json()).client_secret;
        }
        // New session
        const res = await fetch('/api/chatkit/session', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
        });
        return (await res.json()).client_secret;
      },
    },
  });

  return <ChatKit control={control} className="h-full w-full" />;
}
```

### Rationale
- Official OpenAI package with React bindings
- Handles message rendering, typing indicators, tool calls out of the box
- Reduces custom code maintenance burden
- Consistent with constitution Phase 3 technology stack

### Alternatives Considered

| Option | Pros | Cons | Decision |
|--------|------|------|----------|
| Keep custom ChatInterface | Full control, no new deps | Manual accessibility, more code | ❌ Rejected |
| Vercel AI SDK (current) | Already installed | Not ChatKit, limited styling | ❌ Rejected |
| @openai/chatkit-react | Official, feature-rich | New dependency, CDN script | ✅ Selected |

---

## 2. ChatKit Theming & Customization

### Decision: CSS Variables + className styling

ChatKit provides deep UI customization through:
1. **className prop** - Control dimensions and layout
2. **CSS Variables** - Override colors, typography, spacing
3. **Shadow DOM styling** - Target internal elements

### Theming Approach

```css
/* globals.css - ChatKit theme overrides */
openai-chatkit {
  --chatkit-primary-color: var(--color-primary-600);
  --chatkit-background: var(--color-background);
  --chatkit-text-color: var(--color-text-primary);
  --chatkit-border-radius: 0.5rem;
  --chatkit-font-family: var(--font-sans);
}

/* Dark mode variant */
.dark openai-chatkit {
  --chatkit-background: var(--color-background-dark);
  --chatkit-text-color: var(--color-text-primary-dark);
}
```

### Rationale
- CSS variables align with Tailwind design token approach
- Easy dark mode support via class toggle
- No runtime JavaScript needed for theme changes

---

## 3. Backend Integration

### Decision: Add ChatKit session endpoint to existing backend

ChatKit requires a session management endpoint that returns a `client_secret`.

**New Backend Endpoint**:
```
POST /api/chatkit/session
Response: { "client_secret": "..." }
```

This endpoint should:
1. Authenticate the user (verify JWT)
2. Create a ChatKit session with OpenAI
3. Return the client secret to frontend

### Integration with Existing Chat Flow

```
Current: Frontend → POST /api/{user_id}/chat → AI Agent → Response
ChatKit: Frontend → ChatKit → OpenAI (managed) → MCP Tools → Response
```

**Note**: ChatKit may require backend to use ChatKit Python SDK instead of direct OpenAI Agents SDK integration. This is a **BLOCKING DEPENDENCY** that needs clarification.

### Research Finding: Two ChatKit Backend Options

1. **OpenAI-hosted backend** (Agent Builder workflows)
2. **Custom backend** (ChatKit Python SDK)

For our project with existing FastAPI + MCP tools, we need **Option 2** (custom backend).

---

## 4. Dark Mode Implementation

### Decision: System preference + manual toggle using CSS class

**Approach**:
1. Detect system preference with `prefers-color-scheme`
2. Store user preference in localStorage
3. Apply `dark` class to `<html>` element
4. Use Tailwind `dark:` variants for all components

**Implementation**:
```tsx
// ThemeProvider.tsx
const ThemeProvider = ({ children }) => {
  const [theme, setTheme] = useState<'light' | 'dark' | 'system'>('system');

  useEffect(() => {
    const stored = localStorage.getItem('theme');
    if (stored) setTheme(stored as 'light' | 'dark' | 'system');
  }, []);

  useEffect(() => {
    const root = document.documentElement;
    if (theme === 'system') {
      const isDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
      root.classList.toggle('dark', isDark);
    } else {
      root.classList.toggle('dark', theme === 'dark');
    }
    localStorage.setItem('theme', theme);
  }, [theme]);

  return <ThemeContext.Provider value={{ theme, setTheme }}>{children}</ThemeContext.Provider>;
};
```

### Rationale
- SSR-safe (no flash of wrong theme)
- Respects user system preference
- Persists manual override
- Compatible with Tailwind dark mode

---

## 5. Accessibility Requirements

### Decision: Leverage ChatKit built-in a11y + supplement with custom components

ChatKit provides:
- Keyboard navigation within chat
- Screen reader announcements for new messages
- Focus management

Our supplementary components must add:
- ARIA labels for navigation
- Focus trap in modals
- Skip links for main content
- Visible focus indicators (2px outline minimum)

### Testing Strategy
- axe-core for automated a11y audits
- Manual keyboard navigation testing
- Screen reader testing (VoiceOver, NVDA)

---

## 6. Responsive Design

### Decision: Mobile-first with Tailwind breakpoints

**Breakpoints** (per Constitution Principle X):
- sm: 640px
- md: 768px
- lg: 1024px
- xl: 1280px

**Layout Strategy**:
- Mobile: Full-screen ChatKit, hamburger menu for navigation
- Tablet: Side navigation drawer, ChatKit main content
- Desktop: Persistent sidebar, ChatKit takes remaining space

---

## Blocking Dependencies Identified

1. **ChatKit Python SDK integration** - Backend needs to support ChatKit session management
2. **Domain allowlist** - ChatKit requires domain verification in OpenAI org settings
3. **OPENAI_API_KEY** - Already available from Phase 3

---

## Next Steps

1. Create design tokens in `design-tokens.ts`
2. Define component API contracts
3. Document ChatKit integration quickstart
4. Generate implementation tasks

---

## Sources

- [OpenAI ChatKit GitHub](https://github.com/openai/chatkit-js)
- [ChatKit Quick Start](https://openai.github.io/chatkit-js/quickstart/)
- [ChatKit Documentation](https://platform.openai.com/docs/guides/chatkit)
- [ChatKit Advanced Samples](https://github.com/openai/openai-chatkit-advanced-samples)
