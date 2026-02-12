# Tasks: UI/UX Enhancement

**Input**: Design documents from `/specs/004-ui-ux-enhancement/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/

**Tests**: Tests included per constitution (Test-First Approach, Principle IV)

**Organization**: Tasks grouped by user story for independent implementation and testing.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1-US6)
- All paths relative to `frontend/` directory

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Install dependencies and configure project foundations

- [x] T001 Install new dependencies: `npm install @openai/chatkit-react @headlessui/react @heroicons/react framer-motion` in frontend/
- [x] T002 Add ChatKit CDN script to frontend/src/app/layout.tsx
- [x] T003 [P] Create design tokens file at frontend/src/styles/design-tokens.ts per data-model.md
- [x] T004 [P] Update frontend/tailwind.config.ts with design tokens and dark mode class strategy
- [x] T005 [P] Add CSS variables for theming in frontend/src/app/globals.css
- [x] T006 [P] Create utility function `cn()` for class merging in frontend/src/lib/utils.ts

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure MUST be complete before user stories

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [x] T007 Create ThemeProvider component in frontend/src/providers/ThemeProvider.tsx per quickstart.md
- [x] T008 Create useTheme hook in frontend/src/hooks/useTheme.ts
- [x] T009 Create useMediaQuery hook for breakpoints in frontend/src/hooks/useMediaQuery.ts
- [x] T010 Create ToastProvider and useToast hook in frontend/src/providers/ToastProvider.tsx
- [x] T011 Update frontend/src/providers/Providers.tsx to include ThemeProvider and ToastProvider
- [x] T012 [P] Create Spinner component in frontend/src/components/ui/Spinner.tsx per contracts
- [x] T013 [P] Create base Toast component in frontend/src/components/ui/Toast.tsx per contracts

**Checkpoint**: Foundation ready - user story implementation can begin

---

## Phase 3: User Story 6 - ChatKit-Based Primary Interface (Priority: P1) 🎯 MVP

**Goal**: Replace custom ChatInterface with OpenAI ChatKit as primary interface

**Independent Test**: Load application, verify ChatKit renders with custom theming

### Tests for User Story 6

- [x] T014 [P] [US6] Create ChatContainer integration test in frontend/tests/components/ChatContainer.test.tsx
- [x] T015 [P] [US6] Create accessibility test for chat interface in frontend/tests/a11y/chat.test.tsx

### Implementation for User Story 6

- [x] T016 [P] [US6] Create ChatContainer component wrapping ChatKit in frontend/src/components/chat/ChatContainer.tsx
- [x] T017 [P] [US6] Create ToolCallDisplay component in frontend/src/components/chat/ToolCallDisplay.tsx
- [x] T018 [P] [US6] Create EmptyState component in frontend/src/components/chat/EmptyState.tsx
- [x] T019 [US6] Add ChatKit CSS theme overrides to frontend/src/app/globals.css
- [x] T020 [US6] Update frontend/src/app/page.tsx to use ChatContainer as main interface
- [x] T021 [US6] Remove or deprecate old ChatInterface component references

**Checkpoint**: ChatKit is primary interface, themed to design system

---

## Phase 4: User Story 1 - Responsive Task Management on Mobile (Priority: P1)

**Goal**: Mobile-optimized interface with touch-friendly controls (44x44px minimum)

**Independent Test**: Access on mobile viewport (<768px), perform all task operations

### Tests for User Story 1

- [x] T022 [P] [US1] Create responsive layout test in frontend/tests/components/Layout.test.tsx
- [x] T023 [P] [US1] Create mobile navigation test in frontend/tests/components/MobileNav.test.tsx

### Implementation for User Story 1

- [x] T024 [P] [US1] Create Header component in frontend/src/components/layout/Header.tsx per contracts
- [x] T025 [P] [US1] Create MobileNav hamburger menu in frontend/src/components/layout/MobileNav.tsx per contracts
- [x] T026 [P] [US1] Create Sidebar for desktop in frontend/src/components/layout/Sidebar.tsx per contracts
- [x] T027 [US1] Create responsive Layout wrapper in frontend/src/components/layout/Layout.tsx
- [x] T028 [US1] Update frontend/src/app/layout.tsx to use new Layout component
- [x] T029 [US1] Ensure all touch targets are minimum 44x44px (audit existing buttons/inputs)
- [x] T030 [US1] Add responsive breakpoint styles to globals.css for mobile-first approach

**Checkpoint**: Mobile users can perform all operations with touch-friendly UI

---

## Phase 5: User Story 2 - Keyboard-Accessible Task Operations (Priority: P1)

**Goal**: Full keyboard navigation with visible focus indicators (WCAG 2.1 AA)

**Independent Test**: Unplug mouse, perform all operations with keyboard only

### Tests for User Story 2

- [ ] T031 [P] [US2] Create keyboard navigation test in frontend/tests/a11y/keyboard.test.tsx
- [ ] T032 [P] [US2] Create focus management test in frontend/tests/a11y/focus.test.tsx

### Implementation for User Story 2

- [ ] T033 [US2] Refactor Button component with focus-visible states in frontend/src/components/ui/Button.tsx
- [ ] T034 [US2] Refactor Input component with focus-visible states in frontend/src/components/ui/Input.tsx
- [ ] T035 [US2] Refactor Modal with focus trap and Escape handling in frontend/src/components/ui/Modal.tsx
- [ ] T036 [US2] Create ConfirmationDialog component in frontend/src/components/ui/ConfirmationDialog.tsx per contracts
- [ ] T037 [US2] Add skip-to-content link in frontend/src/app/layout.tsx
- [ ] T038 [US2] Add ARIA live regions for dynamic content announcements
- [ ] T039 [US2] Audit and fix tab order across all pages

**Checkpoint**: All operations accessible via keyboard, focus always visible

---

## Phase 6: User Story 4 - Consistent Design System Across Pages (Priority: P2)

**Goal**: Uniform colors, buttons, spacing, typography on all pages

**Independent Test**: Navigate all pages, verify consistent component styling

### Tests for User Story 4

- [ ] T040 [P] [US4] Create visual regression test for Button variants in frontend/tests/components/Button.test.tsx
- [ ] T041 [P] [US4] Create visual regression test for Input variants in frontend/tests/components/Input.test.tsx

### Implementation for User Story 4

- [ ] T042 [P] [US4] Update Button with all variants (primary, secondary, ghost, danger) per contracts
- [ ] T043 [P] [US4] Update Input with all states (default, valid, invalid, disabled) per contracts
- [ ] T044 [US4] Refactor LoginForm to use design system components in frontend/src/components/LoginForm.tsx
- [ ] T045 [US4] Refactor RegisterForm to use design system components in frontend/src/components/RegisterForm.tsx
- [ ] T046 [US4] Update login page styling in frontend/src/app/login/page.tsx
- [ ] T047 [US4] Update register page styling in frontend/src/app/register/page.tsx
- [ ] T048 [US4] Audit all pages for typography scale consistency

**Checkpoint**: All pages use consistent design system

---

## Phase 7: User Story 3 - Visual Feedback for Task Actions (Priority: P2)

**Goal**: Loading states, success toasts, error messages for all actions

**Independent Test**: Perform each action type, observe feedback within 2 seconds

### Tests for User Story 3

- [ ] T049 [P] [US3] Create Toast notification test in frontend/tests/components/Toast.test.tsx
- [ ] T050 [P] [US3] Create loading state test in frontend/tests/components/Spinner.test.tsx

### Implementation for User Story 3

- [ ] T051 [US3] Add loading states to Button component (isLoading prop) in frontend/src/components/ui/Button.tsx
- [ ] T052 [US3] Implement toast notification system with auto-dismiss in frontend/src/providers/ToastProvider.tsx
- [ ] T053 [US3] Create ToastContainer for stacking toasts in frontend/src/components/ui/ToastContainer.tsx
- [ ] T054 [US3] Add success/error toasts to ChatContainer for tool call results
- [ ] T055 [US3] Add loading indicator to chat input during AI response
- [ ] T056 [US3] Implement prefers-reduced-motion check for animations in frontend/src/hooks/useReducedMotion.ts

**Checkpoint**: All actions provide immediate visual feedback

---

## Phase 8: User Story 5 - Dark Mode Support (Priority: P3)

**Goal**: Light/dark themes with system preference detection

**Independent Test**: Toggle system preference, toggle manual switch, verify persistence

### Tests for User Story 5

- [ ] T057 [P] [US5] Create theme toggle test in frontend/tests/components/ThemeToggle.test.tsx
- [ ] T058 [P] [US5] Create dark mode persistence test in frontend/tests/hooks/useTheme.test.ts

### Implementation for User Story 5

- [ ] T059 [US5] Create ThemeToggle UI component in frontend/src/components/ui/ThemeToggle.tsx per contracts
- [ ] T060 [US5] Add dark mode CSS variables to frontend/src/app/globals.css
- [ ] T061 [US5] Update all components with dark: variants in Tailwind
- [ ] T062 [US5] Add ThemeToggle to Header component
- [ ] T063 [US5] Verify ChatKit theming works in dark mode
- [ ] T064 [US5] Verify WCAG AA contrast in dark mode (4.5:1 minimum)

**Checkpoint**: Dark mode fully functional with persistence

---

## Phase 9: Polish & Cross-Cutting Concerns

**Purpose**: Final integration and quality assurance

- [ ] T065 [P] Run full accessibility audit with axe-core
- [ ] T066 [P] Test on Chrome, Firefox, Safari, Edge
- [ ] T067 [P] Test on mobile devices (iOS Safari, Android Chrome)
- [ ] T068 Performance audit: verify <3s page load on 3G throttle
- [ ] T069 Remove unused code and old component imports
- [ ] T070 Update component exports in frontend/src/components/index.ts
- [ ] T071 Run quickstart.md validation steps
- [ ] T072 Final code cleanup and formatting

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - start immediately
- **Foundational (Phase 2)**: Depends on Setup - BLOCKS all user stories
- **US6 ChatKit (Phase 3)**: Depends on Foundational - MVP core interface
- **US1 Mobile (Phase 4)**: Depends on Foundational - can parallel with US6
- **US2 Keyboard (Phase 5)**: Depends on Foundational - can parallel with US6, US1
- **US4 Design System (Phase 6)**: Depends on Foundational - can parallel with above
- **US3 Feedback (Phase 7)**: Depends on US4 (needs consistent components)
- **US5 Dark Mode (Phase 8)**: Depends on US4 (needs design system complete)
- **Polish (Phase 9)**: Depends on all user stories complete

### User Story Independence

| Story | Can Start After | Dependencies on Other Stories |
|-------|-----------------|------------------------------|
| US6 (ChatKit) | Foundational | None - MVP core |
| US1 (Mobile) | Foundational | None - independent |
| US2 (Keyboard) | Foundational | None - independent |
| US4 (Design System) | Foundational | None - independent |
| US3 (Feedback) | US4 | Uses design system components |
| US5 (Dark Mode) | US4 | Uses design system tokens |

### Parallel Opportunities

**Phase 1 (Setup)**: T003, T004, T005, T006 can all run in parallel

**Phase 2 (Foundational)**: T012, T013 can run in parallel

**Phase 3+ (User Stories)**: After Foundational:
- US6, US1, US2, US4 can ALL start in parallel
- Tests within each story can run in parallel
- Different developers can work different stories

---

## Parallel Example: After Foundational Phase

```bash
# Team of 4 developers after Phase 2:

Developer A: User Story 6 (ChatKit)
  → T014, T015 (tests in parallel)
  → T016, T017, T018 (components in parallel)
  → T019, T020, T021 (integration)

Developer B: User Story 1 (Mobile)
  → T022, T023 (tests in parallel)
  → T024, T025, T026 (layout components in parallel)
  → T027, T028, T029, T030 (integration)

Developer C: User Story 2 (Keyboard)
  → T031, T032 (tests in parallel)
  → T033, T034, T035 (refactors)
  → T036, T037, T038, T039 (a11y additions)

Developer D: User Story 4 (Design System)
  → T040, T041 (tests in parallel)
  → T042, T043 (component updates in parallel)
  → T044, T045, T046, T047, T048 (page updates)
```

---

## Implementation Strategy

### MVP First (User Story 6 Only)

1. Complete Phase 1: Setup (T001-T006)
2. Complete Phase 2: Foundational (T007-T013)
3. Complete Phase 3: User Story 6 - ChatKit (T014-T021)
4. **STOP and VALIDATE**: Test ChatKit interface independently
5. Deploy/demo MVP with ChatKit as primary interface

### Incremental Delivery

1. Setup + Foundational → Foundation ready
2. Add US6 (ChatKit) → Deploy/Demo (MVP!)
3. Add US1 (Mobile) + US2 (Keyboard) → Deploy/Demo (Accessibility MVP)
4. Add US4 (Design System) → Deploy/Demo (Polish)
5. Add US3 (Feedback) + US5 (Dark Mode) → Deploy/Demo (Complete)
6. Polish phase → Final release

---

## Summary

| Phase | Story | Task Count | Parallelizable |
|-------|-------|------------|----------------|
| 1 | Setup | 6 | 4 |
| 2 | Foundational | 7 | 2 |
| 3 | US6 ChatKit | 8 | 5 |
| 4 | US1 Mobile | 9 | 5 |
| 5 | US2 Keyboard | 9 | 2 |
| 6 | US4 Design System | 9 | 4 |
| 7 | US3 Feedback | 8 | 2 |
| 8 | US5 Dark Mode | 8 | 2 |
| 9 | Polish | 8 | 4 |
| **Total** | | **72** | **30** |

---

## Notes

- [P] tasks = different files, no dependencies on incomplete tasks
- [Story] label maps task to specific user story for traceability
- Each user story independently completable and testable
- Tests written FIRST, verified to FAIL before implementation
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
