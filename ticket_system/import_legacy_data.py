
import os
import sys
import django
import csv
import glob
import re
from datetime import datetime
from decimal import Decimal, InvalidOperation

# Setup Django environment
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ticket_system.settings')
django.setup()

from reports.models import (
    SLArea,
    SLCustomerMaster,
    SLInventoryMaster,
    SLItem,
    SLJobMaster,
    SLOperator,
    SLSaleOrderDetail,
    SLSaleOrderMaster,
    SLTransactionProduction
)

# Configuration
CSV_DIR = r'c:\Ticket-system\database_files'

# Mapping CSV Filenames to Models
# Add any manual field overrides here if auto-mapping fails
FILE_MAPPING = {
    'SL_AreaTAB.csv': SLArea,
    'SL_CustomerMasterTAB.csv': SLCustomerMaster,
    'SL_InventoryMasterTAB.csv': SLInventoryMaster,
    'SL_ItemTAB.csv': SLItem,
    'SL_JobMasterTAB.csv': SLJobMaster,
    'SL_OperatorTAB.csv': SLOperator,
    'SL_SaleOrderDetailTAB.csv': SLSaleOrderDetail,
    'SL_SaleOrderMasterTAB.csv': SLSaleOrderMaster,
    'SL_TransactionProductionTAB.csv': SLTransactionProduction,
}

# Specific Field Overrides (CSV Header -> Model Field)
FIELD_OVERRIDES = {
    'SalesManCode': 'salesman_code',
    'Creditlimit': 'credit_limit',
    'WithOutOC': 'without_oc',
    'JobUnSettle': 'job_unsettle',
    'AreaCode': 'area_code',
    'SystemCode': 'system_code',
    'QtyUsed': 'qty_used',
    'OQtyUsed': 'oqty_used',
}

def to_snake_case(name):
    """Converts CamelCase or PascalCase to snake_case."""
    # Handle specific edge cases in headers if known, otherwise generic regex
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()

def clean_value(field, value):
    """Cleans and converts values based on Django model field type."""
    if value == '' or value is None:
        return None
    
    internal_type = field.get_internal_type()

    if internal_type in ('DecimalField', 'FloatField'):
        try:
            # Remove currency symbols or commas if present
            clean_val = str(value).replace(',', '').strip()
            return Decimal(clean_val)
        except InvalidOperation:
            return None
    
    if internal_type in ('IntegerField', 'BigIntegerField'):
        try:
            return int(float(value)) # float handle cases like "1.0"
        except ValueError:
            return None

    if internal_type in ('DateField', 'DateTimeField'):
        # Try common date formats
        formats = [
            '%Y-%m-%d', '%d/%m/%Y', '%m/%d/%Y', '%Y/%m/%d',
            '%Y-%m-%d %H:%M:%S', '%d-%b-%y', '%d-%b-%Y',
            '%Y-%m-%d 00:00:00'
        ]
        val_str = str(value).strip()
        for fmt in formats:
            try:
                # Truncate time part for DateField if needed, or parse full for DateTime
                # For safety, parse first part if space exists for simple dates
                if internal_type == 'DateField' and ' ' in val_str:
                     parsed = datetime.strptime(val_str.split(' ')[0], fmt.split(' ')[0])
                     return parsed.date()
                
                dt = datetime.strptime(val_str, fmt)
                if internal_type == 'DateField':
                    return dt.date()
                return dt
            except ValueError:
                continue
        # Fallback for "2024-01-01 00:00:00" style when field is DateField
        try:
            dt = datetime.strptime(val_str.split(' ')[0], '%Y-%m-%d')
            if internal_type == 'DateField':
                return dt.date()
        except:
             pass
             
        return None

    return value

def clean_header(header):
    """Clean header name to handle potential BOM or whitespace."""
    return header.strip().replace('\ufeff', '')

def get_header_map(fieldnames, model_fields):
    """Generates mapping from CSV headers to Model Fields."""
    header_map = {}
    for header in fieldnames:
        # 1. Check overrides
        if header in FIELD_OVERRIDES:
            target = FIELD_OVERRIDES[header]
            if target in model_fields:
                header_map[header] = target
                continue

        # 2. Try snake_case
        normalized = to_snake_case(header)
        if normalized in model_fields:
            header_map[header] = normalized
            continue
        
        # 3. Try exact lower case match
        if header.lower() in model_fields:
            header_map[header] = header.lower()
            continue
    return header_map

def import_file(filename, model_class):
    file_path = os.path.join(CSV_DIR, filename)
    if not os.path.exists(file_path):
        print(f"File not found: {file_path}")
        return

    print(f"\nImporting {filename} into {model_class.__name__}...")
    
    # CLEAR EXISTING DATA
    print(f"  Clearing existing data for {model_class.__name__}...")
    model_class.objects.all().delete()

    model_fields = {f.name: f for f in model_class._meta.get_fields()}
    batch_size = 1000
    objs = []
    
    try:
        with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
            # Smart delimiter detection
            sample = f.read(4096)
            f.seek(0)
            try:
                dialect = csv.Sniffer().sniff(sample)
                delimiter = dialect.delimiter
                print(f"  Detected delimiter: {repr(delimiter)}")
            except:
                delimiter = ','
                print("  Could not sniff delimiter, defaulting to ','")

            # Try reading with detected delimiter
            f.seek(0)
            reader = csv.DictReader(f, delimiter=delimiter)
            raw_fieldnames = reader.fieldnames or []
            fieldnames = [clean_header(h) for h in raw_fieldnames]
            reader.fieldnames = fieldnames # Important fix for DictReader to use cleaned keys

            header_map = get_header_map(fieldnames, model_fields)
            
            # FALLBACK LOGIC: If mapping is poor (0 columns), try forcing comma
            if len(header_map) == 0 and delimiter != ',':
                print("  Mapping failed with detected delimiter. Retrying with ','...")
                f.seek(0)
                reader = csv.DictReader(f, delimiter=',')
                raw_fieldnames = reader.fieldnames or []
                fieldnames = [clean_header(h) for h in raw_fieldnames]
                reader.fieldnames = fieldnames
                header_map = get_header_map(fieldnames, model_fields)
            
            print(f"  Mapped {len(header_map)} columns.")
            
            if not header_map:
                print("  No columns mapped! Skipping file.")
                print(f"  Headers found: {fieldnames[:10]}...")
                return

            row_count = 0
            for row_idx, row in enumerate(reader, start=1):
                data = {}
                for csv_header, model_field_name in header_map.items():
                    raw_value = row.get(csv_header)
                    field_def = model_fields[model_field_name]
                    cleaned = clean_value(field_def, raw_value)
                    data[model_field_name] = cleaned
                
                objs.append(model_class(**data))
                
                if len(objs) >= batch_size:
                    model_class.objects.bulk_create(objs, ignore_conflicts=True)
                    row_count += len(objs)
                    print(f"  Inserted {row_count} rows...", end='\r')
                    objs = []
            
            if objs:
                model_class.objects.bulk_create(objs, ignore_conflicts=True)
                row_count += len(objs)
            
            print(f"\n  Final count: {row_count} rows.")

    except Exception as e:
        print(f"  Error processing {filename}: {e}")

def run():
    print("Starting import process...")
    for filename, model in FILE_MAPPING.items():
        import_file(filename, model)
    print("\nAll Done.")

if __name__ == '__main__':
    run()
