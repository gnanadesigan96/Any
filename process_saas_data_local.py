from datetime import datetime, timedelta
from pathlib import Path
import argparse
import logging
import re
import time

import pandas as pd


logging.basicConfig(
    level="INFO",
    format="%(asctime)s|%(levelname)-8s|%(filename)15s:%(lineno)s - %(funcName)-20s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logging.Formatter.converter = time.gmtime
logger = logging.getLogger(__name__)


CSV_COLUMNS = {
    "provider": str,
    "billing_month": str,
    "payer_account_id": str,
    "account_name": str,
    "account_number": str,
    "charge_type": str,
    "bill_type": str,
    "usage_start_date": str,
    "usage_end_date": str,
    "region": str,
    "product": str,
    "service": str,
    "usage_type": str,
    "cost": str,
}


REQUIRED_COLUMNS = [
    "payer_account_id",
    "account_name",
    "account_number",
    "charge_type",
    "bill_type",
    "usage_start_date",
    "usage_end_date",
    "region",
    "product",
    "service",
    "usage_type",
    "cost",
]


OUTPUT_COLUMNS = [
    "ProviderName",
    "BillingMonth",
    "BillingAccountId",
    "BillingAccountName",
    "BillingAccountNumber",
    "ChargeCategory",
    "ChargeFrequency",
    "ChargePeriodStart",
    "ChargePeriodEnd",
    "RegionName",
    "ServiceName",
    "ProductFamily",
    "UsageType",
    "BilledCost",
    "EffectiveCost",
    "Tags",
]


RENAME_COLUMNS = {
    "provider": "ProviderName",
    "billing_month": "BillingMonth",
    "payer_account_id": "BillingAccountId",
    "account_name": "BillingAccountName",
    "account_number": "BillingAccountNumber",
    "charge_type": "ChargeCategory",
    "bill_type": "ChargeFrequency",
    "usage_start_date": "ChargePeriodStart",
    "usage_end_date": "ChargePeriodEnd",
    "region": "RegionName",
    "product": "ServiceName",
    "service": "ProductFamily",
    "usage_type": "UsageType",
    "cost": "BilledCost",
    "amortized_cost": "EffectiveCost",
    "tags": "Tags",
}


def _get_output_file_path(input_file_path: Path) -> Path:
    return input_file_path.with_name(f"{input_file_path.stem}_output{input_file_path.suffix}")


def _get_all_dates_in_range(start_date_str: str, end_date_str: str) -> list:
    start_date = _parse_date(start_date_str)
    end_date = _parse_date(end_date_str)

    if start_date is None or end_date is None:
        return []

    date_list = []
    current_date = start_date
    while current_date <= end_date:
        date_list.append(current_date.strftime("%Y-%m-%d"))
        current_date += timedelta(days=1)

    return date_list


def _get_cost_value(row) -> float:
    try:
        cost = row.get("cost", "")
        return float(cost) if not pd.isna(cost) and str(cost).strip() != "" else 0.0
    except (TypeError, ValueError):
        return 0.0


def _get_cash_cost_for_row(row, index: int) -> float:
    cost = _get_cost_value(row) if index == 0 else 0.0

    return cost


def _get_amortized_cost_for_row(row, days: int) -> float:
    return _get_cost_value(row) / days


def _parse_date(s):
    if s is None:
        return None
    if isinstance(s, datetime):
        return s
    s = str(s).strip()
    if s == "":
        return None
    if re.match(r"^\d{4}-\d{2}-\d{2}$", s):
        try:
            return datetime.strptime(s, "%Y-%m-%d")
        except ValueError:
            return None

    if re.match(r"^\d{1,2}/\d{1,2}/\d{4}$", s):
        try:
            return datetime.strptime(s, "%d/%m/%Y")
        except ValueError:
            return None

    if re.match(r"^\d{1,2}/\d{1,2}/\d{2}$", s):
        try:
            return datetime.strptime(s, "%d/%m/%y")
        except ValueError:
            return None

    return None


def _get_row_value(row, column_name: str, default: str = ""):
    return row.get(column_name, default)


def _transform_saas_data(input_file_path: Path) -> bytes:
    df = pd.read_csv(input_file_path, dtype=CSV_COLUMNS)
    df = df.astype(object).where(pd.notnull(df), "")
    df.columns = [c.replace(" ", "_") for c in df.columns]

    missing_columns = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    if missing_columns:
        raise ValueError(f"Input CSV is missing required columns: {', '.join(missing_columns)}")

    core_columns = list(CSV_COLUMNS.keys())
    transformed_rows = []

    for _, row in df.iterrows():
        days_in_range = _get_all_dates_in_range(row["usage_start_date"], row["usage_end_date"])
        days_count = len(days_in_range)

        for index, day in enumerate(days_in_range):
            cash_cost = _get_cash_cost_for_row(row, index)
            amortized_cost = _get_amortized_cost_for_row(row, days_count)

            new_row = {
                "provider": str(_get_row_value(row, "provider")),
                "billing_month": str(_get_row_value(row, "billing_month")),
                "payer_account_id": str(row["payer_account_id"]),
                "account_name": str(row["account_name"]),
                "account_number": str(row["account_number"]),
                "charge_type": str(row["charge_type"]),
                "bill_type": str(row["bill_type"]),
                "usage_start_date": _parse_date(day),
                "usage_end_date": _parse_date(day),
                "region": str(row["region"]),
                "product": str(row["product"]),
                "service": str(row["service"]),
                "usage_type": str(row["usage_type"]),
                "cost": cash_cost,
                "amortized_cost": amortized_cost,
            }

            tags = {col: row[col] for col in df.columns if col not in core_columns}
            new_row["tags"] = tags

            transformed_rows.append(new_row)

    result = pd.DataFrame(transformed_rows).rename(columns=RENAME_COLUMNS)
    result = result.reindex(columns=OUTPUT_COLUMNS)

    return result.to_csv(index=False, date_format="%Y-%m-%d", float_format="%.6f").encode("utf-8")


def process_saas_data_local(input_file_path: str) -> str:
    input_path = Path(input_file_path).expanduser()
    if not input_path.is_file():
        raise FileNotFoundError(f"Input file does not exist: {input_path}")

    output_path = _get_output_file_path(input_path)

    logger.info(f"Reading input file from {input_path}")
    processed_data = _transform_saas_data(input_path)

    logger.info(f"Writing processed data to {output_path}")
    output_path.write_bytes(processed_data)

    logger.info("Data processing completed successfully.")
    return str(output_path)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process one local SaaS cost CSV file.")
    parser.add_argument("input_file_path", help="Path to the input CSV file.")
    args = parser.parse_args()

    process_saas_data_local(args.input_file_path)
