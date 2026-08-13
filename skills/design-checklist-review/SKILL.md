---
name: design-checklist-review
description: "Reference UX/UI quality checklists for web app screens. Run before shipping."
version: 1.0.0
author: markfolken
---

# Design Checklist Review

Reference the 100+ design checklists at https://www.checklist.design to review web app screens before shipping.

## How to use

1. Identify the screen type (onboarding, settings, empty-state, chat, billing, etc.)
2. Fetch the relevant checklist from https://www.checklist.design/<category>/<slug>
3. Walk each item against the actual screen
4. Flag any gaps as pre-ship blockers

## Screen to checklist mapping (base URL: https://www.checklist.design)

| Screen | Checklist |
|--------|-----------|
| Onboarding | /web-app/onboarding |
| Settings | /web-app/settings |
| Chat | /web-app/chat |
| Empty state | /web-app/empty-state |
| Billing | /web-app/billing |
| Login | /web-app/login |
| Sign up | /web-app/sign-up |
| Integrations | /web-app/integrations |
| Notifications | /web-app/notifications |
| API Keys | /web-app/api-keys |
| Pricing | /web-app/pricing |
| User Management | /web-app/user-management |
| 2FA | /web-app/2-factor-authentication |
| Search results | /web-app/search-results |
| Help center | /web-app/help-center |
| Analytics | /web-app/analytics |
| Feed | /web-app/feed |
| Version history | /web-app/version-history |
| Comments | /web-app/comments |

## Alternative: install the full bundled skill

Checklist Design publishes all 112 checklists as a bundled Agent Skills package:

- Repo: https://github.com/Checklist-Design/skills
- Install: `npx skills add checklist-design/skills`
- Contains audit mode (item-by-item) and critique mode (fast feedback), no network needed

## Source

Checklist data from https://www.checklist.design by George Hatzis. Created for Co-assistant design reviews.
