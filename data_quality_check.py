# data_quality_check.py - Quick data quality assessment

import pandas as pd
import numpy as np

print("🔍 RPO-DRA Data Quality Check")
print("=" * 70)

# Load your dataset - UPDATE THIS PATH!
CSV_PATH = "~/Downloads/california_wildfire_structures.csv"  # <-- CHANGE THIS!

df = pd.read_csv(CSV_PATH)

print(f"\n📊 Dataset Overview:")
print(f"   Total Records: {len(df):,}")
print(f"   Total Columns: {len(df.columns)}")

# === KEY COLUMNS FOR RPO-DRA ===
key_columns = {
    'Target': ['* Damage'],
    'Structure Features': [
        '* Structure Type',
        'Structure Category',
        '* Roof Construction',
        '* Exterior Siding',
        '* Window Pane',
        'Year Built (parcel)',
        'Assessed Improved Value (parcel)'
    ],
    'Need Indicators': [
        '# Units in Structure (if multi unit)',
        '# of Damaged Outbuildings < 120 SQFT',
        '# of Non Damaged Outbuildings < 120 SQFT'
    ],
    'Defense Actions': [
        'Structure Defense Actions Taken'
    ],
    'Location': [
        'Latitude',
        'Longitude',
        '* Street Number',
        '* Street Name'
    ]
}

print(f"\n📋 Checking Key Columns...")

for category, cols in key_columns.items():
    print(f"\n{category}:")
    for col in cols:
        if col in df.columns:
            missing = df[col].isna().sum()
            missing_pct = (missing / len(df)) * 100
            unique = df[col].nunique()
            print(f"   ✓ {col}")
            print(f"      Missing: {missing:,} ({missing_pct:.1f}%)")
            print(f"      Unique values: {unique:,}")
            
            # Show value distribution for categorical
            if df[col].dtype == 'object' and unique < 20:
                print(f"      Top values: {df[col].value_counts().head(3).to_dict()}")
        else:
            print(f"   ✗ {col} - NOT FOUND!")

# === DAMAGE DISTRIBUTION ===
print(f"\n🔥 Damage Category Distribution:")
if '* Damage' in df.columns:
    damage_dist = df['* Damage'].value_counts()
    for category, count in damage_dist.items():
        pct = (count / len(df)) * 100
        print(f"   {category}: {count:,} ({pct:.1f}%)")

# === MISSING VALUE ANALYSIS ===
print(f"\n⚠️  Columns with HIGH Missing Values (>30%):")
missing_summary = df.isnull().sum()
high_missing = missing_summary[missing_summary > len(df) * 0.3].sort_values(ascending=False)

if len(high_missing) > 0:
    for col, count in high_missing.items():
        pct = (count / len(df)) * 100
        print(f"   {col}: {count:,} ({pct:.1f}%)")
else:
    print("   ✓ No columns with >30% missing values!")

# === DATA TYPE ISSUES ===
print(f"\n🔢 Numeric Columns Check:")
numeric_cols = ['Year Built (parcel)', 'Assessed Improved Value (parcel)', 
                '# Units in Structure (if multi unit)',
                '# of Damaged Outbuildings < 120 SQFT',
                '# of Non Damaged Outbuildings < 120 SQFT']

for col in numeric_cols:
    if col in df.columns:
        dtype = df[col].dtype
        if dtype == 'object':
            print(f"   ⚠️  {col}: STRING (should be numeric!)")
            print(f"      Sample values: {df[col].dropna().head(3).tolist()}")
        else:
            print(f"   ✓ {col}: {dtype}")

# === CATEGORICAL VALUE ISSUES ===
print(f"\n📝 Categorical Columns Check:")
categorical_cols = ['* Roof Construction', '* Exterior Siding', '* Window Pane']

for col in categorical_cols:
    if col in df.columns:
        unique_vals = df[col].nunique()
        has_unknown = 'Unknown' in df[col].values
        
        print(f"   {col}: {unique_vals} unique values")
        if has_unknown:
            unknown_count = (df[col] == 'Unknown').sum()
            print(f"      ⚠️  'Unknown' count: {unknown_count}")
        
        # Check for inconsistent formatting
        sample_vals = df[col].dropna().unique()[:5]
        print(f"      Sample: {list(sample_vals)}")

# === RECOMMENDATIONS ===
print(f"\n\n💡 DATA CLEANING RECOMMENDATIONS:")
print("=" * 70)

issues_found = []

# Check missing values
if '# Units in Structure (if multi unit)' in df.columns:
    if df['# Units in Structure (if multi unit)'].isna().sum() > len(df) * 0.3:
        issues_found.append("FILL: '# Units in Structure' with 1 (default single unit)")

if 'Year Built (parcel)' in df.columns:
    if df['Year Built (parcel)'].isna().sum() > 0:
        issues_found.append("FILL: 'Year Built' with median year")

if 'Assessed Improved Value (parcel)' in df.columns:
    if df['Assessed Improved Value (parcel)'].isna().sum() > 0:
        issues_found.append("FILL: 'Assessed Value' with median value")

# Check for outbuildings
if '# of Damaged Outbuildings < 120 SQFT' in df.columns:
    if df['# of Damaged Outbuildings < 120 SQFT'].isna().sum() > 0:
        issues_found.append("FILL: Outbuilding counts with 0 (assume none if missing)")

# Check defense actions
if 'Structure Defense Actions Taken' in df.columns:
    if df['Structure Defense Actions Taken'].isna().sum() > len(df) * 0.5:
        issues_found.append("FILL: 'Defense Actions' with 'Unknown' (many missing)")

# Check for Unknown values
for col in ['* Roof Construction', '* Exterior Siding', '* Window Pane']:
    if col in df.columns:
        if 'Unknown' in df[col].values:
            unknown_pct = ((df[col] == 'Unknown').sum() / len(df)) * 100
            if unknown_pct > 20:
                issues_found.append(f"HANDLE: '{col}' has {unknown_pct:.0f}% 'Unknown' values")

if len(issues_found) > 0:
    print("\n🔧 CLEANING NEEDED:")
    for i, issue in enumerate(issues_found, 1):
        print(f"   {i}. {issue}")
    print("\n✅ Run the data cleaning script next!")
else:
    print("\n✅ DATA IS CLEAN! Ready to train models directly.")

# === SAVE REPORT ===
print(f"\n📄 Detailed Report:")
report = {
    'total_records': len(df),
    'total_columns': len(df.columns),
    'missing_summary': missing_summary.to_dict(),
    'damage_distribution': df['* Damage'].value_counts().to_dict() if '* Damage' in df.columns else {}
}

print(f"   Records: {report['total_records']:,}")
print(f"   Damage categories found: {len(report['damage_distribution'])}")

print("\n" + "=" * 70)
print("🎯 NEXT STEP:")

if len(issues_found) > 0:
    print("   Run: python clean_data.py")
    print("   Then: python train_models.py")
else:
    print("   Run: python train_models.py (data is already clean!)")
print("=" * 70)
