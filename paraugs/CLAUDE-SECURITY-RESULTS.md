# Claude Security results

This low-effort codebase scan covered the whole repository at `/workspaces/m3-run1` on branch `main`, revision `d6f36c2db6f695181031b5c7c0a30c7ed5d27d86`, starting at 2026-10-27 22:34 UTC. It found six verified issues: 1 HIGH and 5 MEDIUM. The HIGH finding is that the citizen-submissions API has no authentication. The five MEDIUM findings are hard-coded production and test credentials committed to the repository, one of which is still in Git history after the file was deleted.

## Coverage

All 35 tracked files were read as one component (`.`) by a single researcher covering every vulnerability category. Low effort has no inventory, threat model or breadth sweep, so the top-level completeness check does not apply. The tree is small enough that one reader covers all of it: `.claude`, `.devcontainer`, `.github`, `app`, `dati`, `deploy`, `paraugs`, `riki`, `tests` and the root files. Nothing was skipped on purpose. One researcher was dispatched and it returned. The panel finished in one verification run, and no candidate was lost on the way. Because this was a low-effort pass, a medium or high scan could still turn up issues that one reader missed.

## Findings

### F1 — Unauthenticated GET /submissions/{id} returns citizens' personal codes, names, emails and submission text for sequential, guessable IDs (HIGH, confidence medium)

**Impact.** Any client that can reach the API can read every stored citizen submission. That includes national personal identity codes, full names, emails, and the submission text itself, such as social-assistance requests.

**Where.** `app/main.py:136` in `get_submission` — CWE-306

**What.** The API has no authentication and no ownership check. `get_submission` takes the ID from the path, loads the record with `storage.get()`, and returns the full `Submission` model (`personalCode`, `fullName`, `email`, `subject`, `body`, `department`). IDs are sequential (`IES-2026-%06d` from `MAX(seq)+1`), and the unauthenticated `GET /submissions` list hands out every valid ID anyway.

**Exploit scenario.** An anonymous caller requests `GET /submissions` to collect all IDs, or simply counts upward from `IES-2026-000001`. They then request `GET /submissions/IES-2026-00000N` for each ID and harvest every record.

**Preconditions.**
- Network access to the API. uvicorn binds `0.0.0.0:8000`, and the project's catalogue lists the API as internet-facing.

**Fix.** Require authentication on all `/submissions` endpoints. Allow reads only by the submitting citizen (matched by authenticated identity) or by authorized staff roles. Restrict the list endpoint to staff, and switch to non-sequential, unguessable IDs.

**Verification.** 3/3 lens verifiers confirmed.

### F2 — Live ezer-llm API key hardcoded in committed config.ini and baked into the Docker image (MEDIUM, confidence high)

**Impact.** Anyone holding the key can use the production LLM tenant as the municipality. That means cost and quota abuse, and possibly access to the tenant's data and logs. The key stays valid until it is rotated.

**Where.** `config.ini:7` in the `[llm]` section (read by `app.config.llm_settings`) — CWE-798

**What.** `config.ini` is tracked in Git and holds a live production LLM API key. `app/config.py` `llm_settings()` reads it, and `app/triage.py` `route()` sends it with every request. The `Dockerfile` also copies `config.ini` into the image, so the key ships with every built container.

**Exploit scenario.** Someone with access to the repository, a clone, a fork or the built image copies the key. They then call the LLM endpoint as the municipality's tenant.

**Preconditions.**
- Read access to the repository, a copy of it, or the built Docker image.

**Fix.** Revoke and rotate the key. Load it at runtime from an environment variable or a secret manager, and stop copying secrets into the image. Purge the value from Git history.

**Verification.** 3/3 lens verifiers confirmed. The panel lowered the severity from HIGH to MEDIUM (confirming votes: HIGH, MEDIUM, MEDIUM).

### F3 — Production LLM API key committed in deploy/prod.env and still recoverable from Git history after 'removal' (MEDIUM, confidence high)

**Impact.** Anyone holding the key can use the production LLM service account, causing financial cost, quota exhaustion and possible access to tenant data.

**Where.** `deploy/prod.env:4` as committed in `7943761`. The file is gone from the current tree but remains in history. — CWE-798

**What.** Commit `7943761` added `deploy/prod.env` containing the production `EZLLM_API_KEY`. The next commit, `d6f36c2` ("noņemu atslēgu"), only deleted the file, so the key can still be read from any clone or fork with `git show 7943761:deploy/prod.env`.

**Exploit scenario.** An attacker clones the repository or any mirror of it, then runs `git log -p` or a secret scanner over the history. They recover the key and call the production LLM endpoint as Ezerdati.

**Preconditions.**
- Read access to the repository, or to any clone or fork that includes its history.

**Fix.** Treat the key as compromised and rotate it at the provider, because deleting the file did not revoke it. Rewrite history if needed (git filter-repo or BFG), and keep production `.env` files out of version control.

**Verification.** 3/3 lens verifiers confirmed. The panel lowered the severity from HIGH to MEDIUM (confirming votes: MEDIUM, MEDIUM, MEDIUM).

### F4 — Production OMD registry API token hardcoded in the deploy script, hidden only by base64 (MEDIUM, confidence high)

**Impact.** Anyone holding the token can use the production mailbox (OMD) registry API as the municipality, including lookups of e-address and mailbox status by national personal identity code.

**Where.** `deploy/izvietot.sh:10` (script top level) — CWE-798

**What.** The deploy script stores the production OMD token as a base64 string. Base64 is an encoding, not encryption: line 11 decodes it, and anyone else can do the same. Line 15 then puts the token on the ssh remote command line, where the remote host's process listing and shell history can show it.

**Exploit scenario.** A reader of the repository base64-decodes the string to get the plaintext production token. They send it as `X-Api-Key` to the OMD registry and run lookups by personal code.

**Preconditions.**
- Read access to the repository or a copy of it.

**Fix.** Rotate the token. Keep it in a secret store or in a server-side env file outside the repository, set it up on the server, and stop passing secrets on the ssh command line.

**Verification.** 3/3 lens verifiers confirmed. The panel lowered the severity from HIGH to MEDIUM (confirming votes: MEDIUM, MEDIUM, MEDIUM).

### F5 — Hardcoded Postgres password in docker-compose.yml with the database port published on all host interfaces (MEDIUM, confidence high)

**Impact.** An attacker gets full read and write control of the test environment's submissions database, which is meant to hold citizens' personal data.

**Where.** `docker-compose.yml:18` in `services.db.environment` — CWE-798

**What.** The Postgres owner password is committed in plaintext here, and again in `DATABASE_URL` on line 9. The `db` service publishes `5432:5432`, which binds on all host interfaces, so the database accepts connections from anywhere that can reach the host.

**Exploit scenario.** An attacker who has seen the repository connects with `psql` to port 5432 on the test server as user `ezermala` using the committed password. As the database owner, they can read, change or drop the `iesniegumi` database.

**Preconditions.**
- Read access to the repository.
- Network reach to the host running this compose file.

**Fix.** Rotate the password and load it from Docker secrets or an untracked `.env` file. Remove the published 5432 port, or bind it to `127.0.0.1`. Purge the value from history.

**Verification.** 3/3 lens verifiers confirmed. The panel lowered the severity from HIGH to MEDIUM (confirming votes: MEDIUM, MEDIUM, MEDIUM).

### F6 — Test database credentials for the Ezerdati Postgres host left in a source comment (MEDIUM, confidence high)

**Impact.** An attacker gets access to the vendor's test database, limited by the test account's rights and by the need to reach the Ezerdati network.

**Where.** `tests/test_integracija.py:9` (module comment) — CWE-798

**What.** A committed comment gives the host (`db-tests.ezerdati.example:5432`), the user (`ezermala_tests`) and the password for the vendor's test database. The comment says not to change it, which suggests the credential is long-lived and still current.

**Exploit scenario.** A repository reader inside the Ezerdati network, such as an insider, a contractor or an attacker already there, logs in as `ezermala_tests` and reads or changes the test data.

**Preconditions.**
- Read access to the repository.
- Network access to `db-tests.ezerdati.example`, which is stated to be reachable only from the Ezerdati network.

**Fix.** Rotate the test account password and remove it from the comment and from Git history. Supply integration-test credentials through CI secrets or environment variables.

**Verification.** 3/3 lens verifiers confirmed.

## What was verified

These findings come from reading the code only. Nothing in the repository was executed, and no exploit was run. One researcher read the whole tree for every vulnerability category. A three-member panel then examined each candidate through three lenses: reachability, impact and existing defenses. All six findings were confirmed 3/3. The panel lowered F2–F5 from HIGH to MEDIUM. The renderer stamped this run `unverified` because it refused F3 at render time: F3 points at `deploy/prod.env`, which exists only in Git history and not in the scanned tree. F3 is therefore absent from the JSONL and SARIF files, which hold the other five findings. The panel still confirmed F3 3/3 and it is described above. Rotating that key is still required.
