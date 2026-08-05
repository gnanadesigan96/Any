# SaaS Consumption Pipeline

Turns the customer's multi-sheet consumption workbook into per-provider,
per-month cost files in S3 - and skips straight to whatever's new every time
it's re-run.

## What it does

1. Reads the workbook (e.g. `2026 Consumption Costs.xlsx`) and keeps only the
   five provider sheets: **Snowflake, Databricks, Elastic, Datadog, Splunk**
   (the `... VLookup` sheets are ignored).
2. For each provider, groups rows by month (based on `usage_start_date`) and
   figures out which months are **already uploaded to S3** vs. new.
3. For each new month only, writes a raw CSV with:
   - `usage_start_date` / `usage_end_date` formatted as `DD/MM/YY` (e.g. `01/06/26`)
   - `cost` as a plain number (e.g. `12499.00`, no `$` or thousands separator)
4. Runs the existing `process_saas_data_local.py` on that CSV to produce the
   `*_output.csv` file (unchanged - this repo doesn't modify that script).
5. Uploads the output file to
   `s3://<bucket>/<Provider>/<Year>/<Month>/<Provider><Mon>_output.csv`
   (e.g. `s3://<bucket>/Databricks/2026/04/DatabricksApr_output.csv`), matching
   the existing `Provider -> Year -> Month` folder structure in the bucket.

Note: the `2026-6` / `$12,499` look in the workbook is just Excel's *display*
formatting - the cells actually hold a real date and a real number. The split
step reads the real values directly, and also tolerates a messier text export
(literal `"2026-6"` or `"$12,499"` strings) as a fallback, so it's robust
either way.

Re-running the pipeline on the same or an updated workbook is always safe: it
never re-derives state from a local file, only from what's actually sitting in
S3, so it can't re-process or double-upload a month that's already there.

## Setup

```bash
pip install -r requirements.txt
```

## Running it manually

```bash
# Full run: split new months, process them, upload to S3
python run_pipeline.py --workbook "2026 Consumption Costs.xlsx" --bucket my-saas-billing-bucket

# Local-only dry run (no AWS needed): split + process every month, skip S3 entirely
python run_pipeline.py --workbook "2026 Consumption Costs.xlsx" --no-upload

# Re-process every month regardless of what's already in S3 (e.g. to backfill or fix a bad upload)
python run_pipeline.py --workbook "2026 Consumption Costs.xlsx" --bucket my-saas-billing-bucket --force-all-months

# Only specific providers
python run_pipeline.py --workbook "2026 Consumption Costs.xlsx" --bucket my-saas-billing-bucket --providers Databricks Snowflake
```

## AWS setup (not yet configured)

The script uses boto3's standard credential chain - it doesn't hardcode
anything, so any of these work once set up:

- **Access keys**: set `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, and
  `AWS_DEFAULT_REGION` as environment variables (or an `AWS_PROFILE` pointing
  at a profile in `~/.aws/credentials`).
- **IAM role**: if this ends up running on an EC2 instance, ECS task, or
  Lambda, attach a role instead - no static keys needed.

Whichever identity runs this needs, at minimum, on the target bucket:
`s3:ListBucket` (to find the latest uploaded month) and `s3:PutObject` (to
upload output files). Scope it to that one bucket/prefix rather than
account-wide access.

Until credentials exist, use `--no-upload` to test the split + process steps
locally - the S3 step is the only part that needs AWS access.

## SharePoint -> Power Automate -> this pipeline

Since detection is happening via Power Automate rather than this script
polling SharePoint directly, the integration contract is:

1. A Power Automate flow triggers **"When a file is created or modified"** on
   the SharePoint folder the customer emails their workbook into.
2. That flow gets the file onto a location this script can read - e.g. a
   network/shared path, or an HTTP/Run-script action that hands the file to
   wherever this runs.
3. Power Automate then invokes:
   ```bash
   python run_pipeline.py --workbook "<downloaded file path>" --bucket my-saas-billing-bucket
   ```
4. That's it - Power Automate doesn't need to track "what month are we on."
   Every invocation re-checks S3 itself and only processes what's actually
   new, so it's safe to call this on every file drop, even if the customer
   re-uploads the same workbook with just one new month appended, or the flow
   fires more than once for the same file.

The only two things needed to wire this up for real: (1) the AWS credentials
above, and (2) whatever mechanism gets the SharePoint file from Power Automate
onto disk where `run_pipeline.py` runs.

## Layout

```
process_saas_data_local.py   # existing per-file transform script, unchanged
run_pipeline.py              # orchestrator: split -> process -> upload
saas_pipeline/
  config.py                  # provider list, month names, column names
  split_monthly.py           # workbook -> per-month raw CSVs
  s3_sync.py                 # latest-month detection + upload
tests/                       # uses a synthetic workbook + moto-mocked S3, no customer data
```

## Tests

```bash
pip install pytest moto
python -m pytest tests/ -q
```
