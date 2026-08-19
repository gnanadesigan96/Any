# SaaS Consumption Pipeline

Turns the customer's multi-sheet consumption workbook into per-provider,
per-month cost files in S3 - and skips straight to whatever's new every time
it's re-run.

## What it does

1. Reads the workbook (e.g. `2026 Consumption Costs.xlsx`) and keeps only the
   five provider sheets: **Snowflake, Databricks, Elastic, Datadog, Splunk**
   (the `... VLookup` sheets are ignored).
2. For each provider, groups rows by month (based on `usage_start_date`), looks
   at the most recent **12 months** present in the workbook, and checks each one
   individually against S3 - a month already uploaded is skipped, and a
   missing one is queued for processing. This is a per-month gap check, not a
   moving cutoff: if February was somehow skipped while January and March both
   uploaded fine, it gets backfilled too - it's not just "whatever's newer
   than the last upload." Months older than that trailing 12-month window are
   left alone even if they happen to be missing. It also never looks earlier
   than `PIPELINE_START_MONTH` (2026-01) in `saas_pipeline/config.py`, however
   wide the window is - the pipeline has no reason to touch anything before
   its own start date, even if the workbook someday grows to include it.
3. For each month being processed, writes a raw CSV with:
   - `usage_start_date` / `usage_end_date` formatted as `DD/MM/YY` (e.g. `01/06/26`)
   - `cost` as a plain number (e.g. `12499.00`, no `$` or thousands separator)
4. Runs the existing `process_saas_data_local.py` on that CSV to produce the
   `*_output.csv` file (unchanged - this repo doesn't modify that script).
5. Uploads the output file to
   `s3://<bucket>/<prefix>/<Provider>/<Year>/<Month>/<Provider><Mon>_output.csv`
   (e.g. `s3://flatiron-saas-upload/saas-upload/Databricks/2026/04/DatabricksApr_output.csv`),
   matching the existing `prefix -> Provider -> Year -> Month` folder structure
   in the bucket. The bucket name and that prefix both vary per
   engagement/environment - this test bucket is `flatiron-saas-upload` with
   prefix `saas-upload`, but neither is hardcoded anywhere; both are passed in
   (`--bucket`/`--s3-prefix` on the CLI, `S3_BUCKET`/`S3_PREFIX` for the
   Function). Leave the prefix unset if the provider folders sit directly at
   the bucket root.

Note: the `2026-6` / `$12,499` look in the workbook is just Excel's *display*
formatting - the cells actually hold a real date and a real number. The split
step reads the real values directly, and also tolerates a messier text export
(literal `"2026-6"` or `"$12,499"` strings) as a fallback, so it's robust
either way.

Re-running the pipeline on the same or an updated workbook is always safe: it
never re-derives state from a local file, only from what's actually sitting in
S3, so it can't re-process or double-upload a month that's already there. This
is checked *before* anything else happens for that month - if a month's S3
folder already has a file in it, that month is never re-generated, never
re-transformed, and never re-uploaded. Nothing in that folder is touched.

"Current month" is driven entirely by what's newest in the customer's
workbook, not by today's real calendar date - billing data lags (e.g. June's
costs might not be final until August), so a workbook that only goes up to
June is treated as being caught up through June, even if it's August when the
pipeline runs.

## Setup

```bash
pip install -r requirements.txt
```

## Running it manually

```bash
# Full run: split new months, process them, upload to S3
python run_pipeline.py --workbook "2026 Consumption Costs.xlsx" --bucket flatiron-saas-upload --s3-prefix saas-upload

# Local-only dry run (no AWS needed): split + process every month, skip S3 entirely
python run_pipeline.py --workbook "2026 Consumption Costs.xlsx" --no-upload

# Re-process every month regardless of what's already in S3 (e.g. to backfill or fix a bad upload)
python run_pipeline.py --workbook "2026 Consumption Costs.xlsx" --bucket flatiron-saas-upload --s3-prefix saas-upload --force-all-months

# Only specific providers
python run_pipeline.py --workbook "2026 Consumption Costs.xlsx" --bucket flatiron-saas-upload --s3-prefix saas-upload --providers Databricks Snowflake
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
`s3:ListBucket` (to check which months already have a file) and
`s3:PutObject` (to upload output files). Scope it to that one bucket/prefix
rather than account-wide access.

Until credentials exist, use `--no-upload` to test the split + process steps
locally - the S3 step is the only part that needs AWS access.

## SharePoint -> Azure Function -> S3

`function_app.py` is an HTTP-triggered Azure Function that runs this whole
pipeline in the cloud: it fetches the latest matching workbook from SharePoint
itself (via Microsoft Graph, app-only auth), then does the same split ->
process -> upload steps as `run_pipeline.py`, in memory, per invocation.

Power Automate's job is reduced to just the trigger:

1. A Power Automate flow triggers **"When a file is created or modified"** on
   the SharePoint folder the customer's workbook lands in.
2. It calls the Function's HTTP endpoint (an "HTTP" or "Azure Functions"
   action, using the function key for auth) - no file content needs to be
   attached to the call, since the Function pulls the file itself.
3. The Function finds the most recently modified file in that folder
   (optionally filtered by `SHAREPOINT_FILENAME_CONTAINS`), downloads it, and
   runs the pipeline.

Same safety property as `run_pipeline.py`: every invocation re-checks S3,
month by month across the trailing 12-month window, per provider - so it's safe
for Power Automate to call this on every file drop, or more than once for the
same file, without double-processing anything.

### Required Function App configuration

Set these as Application Settings (Key Vault references for the two secrets -
see the Key Vault setup steps from earlier in this conversation):

| Setting | Description |
|---|---|
| `SHAREPOINT_TENANT_ID` | Azure AD tenant ID |
| `SHAREPOINT_CLIENT_ID` | App registration (client) ID, granted Graph `Sites.Selected` or `Sites.Read.All` with admin consent |
| `SHAREPOINT_CLIENT_SECRET` | That app registration's client secret - **Key Vault reference** |
| `SHAREPOINT_SITE_URL` | Combined hostname + site path, e.g. `yourtenant.sharepoint.com/sites/YourSiteName` (scheme/trailing slash optional, both get stripped) |
| `SHAREPOINT_FOLDER_PATH` | Document library path the workbook lands in, e.g. `General/Flatiron-SaaS-Upload/Data` |
| `SHAREPOINT_FILENAME_CONTAINS` | Optional substring to match the workbook's filename, e.g. `Consumption Costs`. Leave unset/empty to just take the most recently modified file in the folder - fine when that folder is dedicated to this one workbook. |
| `S3_BUCKET` | Target S3 bucket, e.g. `flatiron-saas-upload` - varies per engagement |
| `S3_PREFIX` | Optional path between the bucket root and the provider folders, e.g. `saas-upload`. Leave unset if the provider folders sit directly at the bucket root - also varies per engagement |
| `AWS_ACCESS_KEY_ID` / `AWS_SECRET_ACCESS_KEY` | (or rely on a role/instance identity if you set one up) - **Key Vault references** |
| `AWS_DEFAULT_REGION` | Bucket's region |

`local.settings.json.example` has the same list for local `func start` testing
- copy it to `local.settings.json` (already gitignored) and fill in real
values there, never in `local.settings.json.example` itself.

### Calling it

```bash
curl -X POST "https://<function-app-name>.azurewebsites.net/api/process?code=<function-key>"

# optional query params:
#   providers=Databricks,Snowflake   (default: all five)
#   force_all_months=true            (ignore S3 state, reprocess everything)
```

It returns a JSON summary per provider: the trailing 12-month window that was
checked, which of those months were already in S3, and which ones got
processed (backfilled).

### Deploying

```bash
func azure functionapp publish saas-pipeline-func
```
(run from this repo's root, alongside `host.json`; `.funcignore` keeps
`tests/`, `data/`, and `README.md` out of the deployed package)

## Layout

```
process_saas_data_local.py   # existing per-file transform script, unchanged
run_pipeline.py              # CLI orchestrator: split -> process -> upload (cron/manual use)
function_app.py              # Azure Function HTTP trigger: SharePoint fetch -> same pipeline -> upload
host.json                    # Azure Functions runtime config
local.settings.json.example  # template for local Function config (copy to local.settings.json)
saas_pipeline/
  config.py                  # provider list, month names, column names
  split_monthly.py           # workbook -> per-month raw CSVs
  s3_sync.py                 # per-month gap check (trailing 12-month window) + upload
  sharepoint_client.py       # Microsoft Graph auth + file lookup/download
tests/                       # synthetic workbook + moto-mocked S3 + mocked Graph calls, no customer data
```

## Tests

```bash
pip install pytest moto
python -m pytest tests/ -q
```
