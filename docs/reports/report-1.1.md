# Report 1.1

## 1. Goal
Task 1.1 — Error handling

## 2. Status
DONE

## 3. Checks

| Done when | Result | Command |
|---|---|---|
| Bad body → 422 in shared shape | PASS | `test_bad_body_gives_422_in_shared_shape`, `test_non_json_body_gives_422_in_shared_shape` |
| Unknown path → 404 in shared shape | PASS | `test_unknown_path_gives_404_in_shared_shape` |
| Route that raises → 500 in shared shape, no traceback | PASS | `test_unhandled_exception_gives_500_without_traceback` |
| All tests pass | PASS | `.venv/bin/pytest` |

pytest:
```
16 passed, 1 warning in 6.31s
```

## 4. What changed
- `api/app/errors.py` (new): handlers for HTTPException (404/405/401/…), RequestValidationError (422) and any other exception (500, logged with traceback, body has none).
- `api/app/main.py`: installs the handlers. `/health` unchanged.
- `api/tests/test_errors.py` (new): tests use two throwaway routes (`/_test/echo` with a body, `/_test/boom` that raises), removed after the module.

## 5. Decisions I made
- 422 message format: `<field>: <pydantic message lowercased>`, several errors joined by `; ` — gives `password: field required` like the contract example.
- Our own code raises `HTTPException(status, detail={"code", "message"})`; plain-string details get a code from the status (404 `not_found`, 405 `method_not_allowed`, 401 `unauthorized`, else `http_error`).
- Also tested 405 in the shared shape (task asked for it, not in Done when).

## 6. Questions for the owner
None.

## 7. Not checked / risks
- The warning is Starlette deprecating `httpx` in its TestClient (wants `httpx2`); harmless for now.

## 8. Commit
See `git log` for `task 1.1: error handling`.
