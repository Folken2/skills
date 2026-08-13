---
name: database-migration-safety
description: Use when writing, reviewing, applying, or rolling back a database schema migration — creating tables/columns/indexes/constraints, altering types, or backfilling data — to ensure every change is reversible, tested, and safe for production.
version: 1.0.0
author: Nuvel Skills (inspired by Brandon Bayer / rag.saas-shipkit)
---

# Database Migration Safety

## Overview

A migration is production surgery on live data. The difference between a safe migration and an outage is not luck — it is a protocol: every forward change has a tested reverse, every risky operation is flagged before it runs, and nothing reaches production without being validated somewhere else first.

**Core principle:** No up migration ships without a corresponding down migration, and no migration reaches production without being run and rolled back on a disposable copy first.

This skill is database-agnostic. For engine/tool-specific mechanics (e.g. Drizzle's `down.sql` convention and journal handling), see [references/drizzle-migration-examples.md](references/drizzle-migration-examples.md).

## The Non-Negotiables

1. **Every up migration has a down migration.** If you cannot write the reverse, you do not yet understand the forward change well enough to ship it.
2. **Reverse in reverse order.** The down migration undoes operations last-created-first, so dependencies (indexes before their tables, constraints before their columns) unwind cleanly.
3. **Test the round-trip before production.** Apply up → verify → apply down → verify the schema returns to its prior state, on a throwaway database.
4. **Flag irreversible operations loudly.** A `DROP` that destroys data cannot be truly reversed. Say so, require a backup, and get explicit confirmation.
5. **Never edit an already-applied migration.** Once a migration has run anywhere shared, it is immutable. Fix forward with a new migration.

## Writing a Reversible Down Migration

For each forward operation, write its inverse. Reversibility falls into three buckets:

| Up operation | Down operation | Reversible? |
|---|---|---|
| Create table | Drop table (if exists) | ✅ fully |
| Add column | Drop column (if exists) | ✅ fully |
| Create index | Drop index (if exists) | ✅ fully |
| Add constraint | Drop constraint (if exists) | ✅ fully |
| Rename column/table | Rename back | ✅ fully |
| Change column type | Change back | ⚠️ only if the conversion is lossless |
| Insert seed data | Delete those specific rows | ⚠️ scope the delete precisely |
| **Drop table/column** | **Cannot restore data** | ❌ requires backup / manual restore |

**Safety rules for down migrations:**

- Use idempotent guards (`IF EXISTS` / `IF NOT EXISTS` or the engine's equivalent) so a partial rollback can re-run without erroring.
- Group operations by type and header them clearly, so a reviewer can scan the reversal.
- Put a header comment on every down migration listing the data-loss risks and any manual steps needed.
- For a type change or data transformation, state explicitly whether the reverse is lossless; if not, treat it as irreversible.

## Zero-Downtime Principles

When the schema is under live traffic, a change and its dependent code deploy cannot both flip at the same instant. Sequence them:

- **Additive first.** Add new columns/tables as nullable or with defaults before any code reads them. Old code must keep working against the new schema.
- **Expand, then contract.** To rename or restructure: add the new shape, backfill, switch reads/writes to it, and only remove the old shape in a *later* migration after the new code is fully deployed.
- **Backfill in batches.** A single `UPDATE` over millions of rows locks the table. Chunk it, and make it resumable.
- **Avoid long locks.** Adding a non-nullable column with a default, or an index without a concurrent/online option, can lock writes — check your engine's locking behavior for each operation.
- **Decouple destructive drops.** Never drop a column in the same release that stops using it. Drop it a release later, once you're confident nothing depends on it.

## Migration Order & Dependency Check

Before applying, confirm ordering is sound:

- Migrations apply in a deterministic, recorded order (timestamp/sequence + a journal or migrations table). Never reorder or renumber an applied migration.
- A migration must not depend on an object created by a *later* migration.
- When rolling back, ensure no *later* applied migration depends on what you are about to reverse — roll those back first, in reverse order.
- Foreign keys, indexes, and constraints must be created after, and dropped before, the objects they reference.

## Schema Diff Review

Before applying any generated migration, read the diff — do not trust auto-generation blindly:

- [ ] Does the diff match your *intended* change, and only that change?
- [ ] Any unexpected drops? (A tool misreading the schema can generate a destructive `DROP` you never asked for.)
- [ ] Any operation that will lock a large table or rewrite it in place?
- [ ] Do generated names (indexes, constraints) collide with existing ones?
- [ ] Is a NOT NULL column being added without a default to an existing populated table?

## Rollback Workflow

A complete rollback is two phases — reverse the database, then clean up local artifacts:

1. **Identify** the exact migration to roll back and confirm it is the latest applied one.
2. **Check the down migration exists** before touching the database. No reverse script → stop and write one first.
3. **Back up** production data before any destructive rollback.
4. **Execute the reverse** (run the down migration; remove its record from the migrations table).
5. **Clean up local files/metadata** so the next generate starts from a correct baseline (see the Drizzle reference for the file-level specifics).
6. **Verify** the schema and migration status match the intended prior state.

Require explicit human confirmation before any step that deletes data or files.

## Verification Checklist

Before declaring a migration safe:

- [ ] A down migration exists and reverses every forward operation, in reverse order.
- [ ] Irreversible operations (data-destroying drops, lossy type changes) are documented with data-loss warnings.
- [ ] Round-trip tested on a disposable DB: up applies cleanly, down restores prior state.
- [ ] Down migration uses idempotent guards and can re-run after a partial failure.
- [ ] Schema diff reviewed line-by-line; no unexpected drops or in-place rewrites.
- [ ] Ordering/dependencies checked; no forward-references, no orphaned constraints.
- [ ] For live traffic: change is additive/expand-contract, backfills are batched, no long table locks.
- [ ] Production backup taken before applying anything destructive.
- [ ] Applied migration files treated as immutable (fix-forward, never edit).

## Red Flags — STOP

| Thought | Reality |
|---|---|
| "It's a small change, skip the down migration" | Small changes still need reversing. Write it. |
| "I'll edit the migration that already ran" | Applied migrations are immutable. New migration only. |
| "The generated SQL looks fine, just apply it" | Read the diff — auto-generators emit unexpected drops. |
| "I'll drop the old column in this same release" | Expand-contract. Drop it a release later. |
| "One UPDATE will backfill everything" | Unbatched updates lock the table. Chunk it. |
| "I tested up, that's enough" | Test the round-trip. A down that fails is no down. |
| "No backup needed, I'm careful" | Destructive ops require a backup. No exceptions. |

## Common Mistakes to Avoid

| Don't | Do |
|---|---|
| Write an up migration with no reverse | Pair every up with a tested down |
| Reverse operations in forward order | Reverse last-created-first |
| Trust auto-generated diffs blindly | Review the diff for unexpected drops/rewrites |
| Add a NOT NULL column with no default to a populated table | Add nullable/defaulted, backfill, then constrain |
| Drop and stop-using a column in one release | Split into expand then contract releases |
| Roll back without checking later dependencies | Roll back dependents first, in reverse order |
