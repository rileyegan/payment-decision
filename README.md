# payment-decision

Personal example of a payment decision and a false-positive check. One made-up payment event goes in. An allow, review, or decline decision and a reason come out.

I work in payments risk. This is not code from that job. It has no employer data, no employer thresholds, and no merchant list. The cutoffs in `payment_decision/rules.py` are numbers I picked so the tests stay obvious.

Review counts as not allowed. A false positive is a good event the rule does not allow. The example gate ships a rule only when that share is 30 percent or lower on the made-up cohort in `tests/test_false_positive.py`. The balanced rules pass. A rule that declines every account under 30 days fails the same gate.

## Run one event

From this folder:

```bash
# =============================================================================
# COMMAND GLOSSARY — tools used in this script
# -----
# python3  Python interpreter. Here: runs this repo's decision command.
# =============================================================================

# Print one JSON decision for a made-up event.
# Read-only: no file, no network, nothing saved.
python3 -m payment_decision \
  --amount-cents 25000 \
  --account-age-days 3 \
  --declines-in-last-hour 0 \
  --country-mismatch
```

That event is a new account and an elevated amount, so the decision is review. The reason code is `new_account_elevated_amount`.

`--merchant-category` is optional. The choices are `grocery`, `digital_goods`, and `money_movement`. The example rules do not use it.

## Run the tests

Python 3.11 or newer.

```bash
# =============================================================================
# COMMAND GLOSSARY — tools used in this script
# -----
# python3  Python interpreter. Here: creates a virtualenv and installs pytest.
# source   Runs a file in the current shell. Here: activates that virtualenv.
# pytest   Test runner. Here: runs the local decision and false-positive tests.
# =============================================================================

# Create a local virtualenv in this folder.
# Safety: writes .venv here. Does not change other projects.
python3 -m venv .venv

# Turn on that virtualenv in this shell.
# Safety: changes this shell's python and pip only.
source .venv/bin/activate

# Install pytest into the virtualenv.
# Safety: network install of pytest. Does not install a web service.
pip install -r requirements.txt

# Run the tests.
# Safety: local only. No network and no files written except pytest's cache.
pytest
```
