# Implementation Plan: User Profile (Minimal)

**Branch**: `005-task-enhancements` | **Date**: 2026-02-06
**Scope**: User info display + account actions (logout, delete)

## Summary

Add a user profile page that displays basic user information (email, account creation date) and provides account actions (logout button, delete account with confirmation).

## Changes Required

### Backend (2 changes)

**1. User Repository - Add delete method**
- File: `backend/src/repositories/user_repository.py`
- Add: `async def delete(self, user: User) -> None`
- Cascade delete handled by SQLModel relationship config (already set up)

**2. Auth API - Add delete account endpoint**
- File: `backend/src/api/auth.py`
- Add: `DELETE /api/v1/auth/me` - deletes authenticated user
- Returns: 204 No Content on success
- Requires: Valid JWT token

### Frontend (4 changes)

**1. Auth Library - Add deleteAccount function**
- File: `frontend/src/lib/auth.ts`
- Add: `export async function deleteAccount(): Promise<void>`
- Calls DELETE to `/api/v1/auth/me`, then removes token

**2. AuthProvider - Add deleteAccount to context**
- File: `frontend/src/providers/AuthProvider.tsx`
- Add `deleteAccount` method that calls auth lib, clears user, redirects to login

**3. Profile Page - New page component**
- File: `frontend/src/app/profile/page.tsx`
- Displays: User email, member since date (formatted)
- Actions: Logout button, Delete Account button (with confirmation modal)
- Uses existing Layout, Button, useAuth

**4. Navigation - Add profile link**
- File: `frontend/src/components/layout/Layout.tsx`
- Add: Profile nav item with UserCircleIcon

## File Changes Summary

| File | Action | Description |
|------|--------|-------------|
| `backend/src/repositories/user_repository.py` | Edit | Add `delete()` method |
| `backend/src/api/auth.py` | Edit | Add `DELETE /auth/me` endpoint |
| `frontend/src/lib/auth.ts` | Edit | Add `deleteAccount()` function |
| `frontend/src/providers/AuthProvider.tsx` | Edit | Add `deleteAccount` to context |
| `frontend/src/app/profile/page.tsx` | Create | Profile page with user info and actions |
| `frontend/src/components/layout/Layout.tsx` | Edit | Add Profile nav item |

## Acceptance Criteria

- [ ] Profile page shows user email
- [ ] Profile page shows "Member since" date
- [ ] Logout button works (clears session, redirects to login)
- [ ] Delete account shows confirmation modal
- [ ] Delete account removes user and all their data
- [ ] Delete account redirects to login after deletion
- [ ] Profile link visible in navigation
