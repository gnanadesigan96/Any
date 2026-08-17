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
3. The Function finds the most recently modified file in that folder whose
   name contains `SP_FILENAME_CONTAINS`, downloads it, and runs the pipeline.

Same safety property as `run_pipeline.py`: every invocation re-checks S3 for
each provider's latest uploaded month and only processes what's new, so it's
safe for Power Automate to call this on every file drop, or more than once for
the same file, without double-processing anything.

### Required Function App configuration

Set these as Application Settings (Key Vault references for the two secrets -
see the Key Vault setup steps from earlier in this conversation):

| Setting | Description |
|---|---|
| `SP_TENANT_ID` | Azure AD tenant ID |
| `SP_CLIENT_ID` | App registration (client) ID, granted Graph `Sites.Selected` or `Sites.Read.All` with admin consent |
| `SP_CLIENT_SECRET` | That app registration's client secret - **Key Vault reference** |
| `SP_SITE_HOSTNAME` | e.g. `yourtenant.sharepoint.com` |
| `SP_SITE_PATH` | e.g. `sites/YourSiteName` |
| `SP_FOLDER_PATH` | Document library path the workbook lands in, e.g. `Shared Documents/Customer Uploads` |
| `SP_FILENAME_CONTAINS` | Substring to match the workbook's filename, e.g. `Consumption Costs` |
| `S3_BUCKET` | Target S3 bucket |
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

It returns a JSON summary per provider: the latest month that was already in
S3 before the run, and which new months got processed.

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
  s3_sync.py                 # latest-month detection + upload
  sharepoint_client.py       # Microsoft Graph auth + file lookup/download
tests/                       # synthetic workbook + moto-mocked S3 + mocked Graph calls, no customer data
```

## Tests

```bash
pip install pytest moto
python -m pytest tests/ -q
```
