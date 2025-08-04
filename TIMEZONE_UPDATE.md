# Pakistan Standard Time (PST) Implementation

## Overview
This document outlines the changes made to implement Pakistan Standard Time (Asia/Karachi) across the Product Registry Application.

## Changes Made

### 1. Models (models.py)
- **Modified `utc_to_pakistan()` function**: Now returns formatted string instead of datetime object
- **Format**: `'%d-%m-%Y %I:%M %p'` (e.g., "31-07-2025 04:43 PM")
- **Handles None values**: Returns "None" for null datetime inputs
- **Timezone Aware**: Properly converts UTC timestamps to Pakistan timezone

### 2. PDF Generation (pdf_generator.py)
- **ReportLab PDF Generator**: Updated all datetime fields to use Pakistan timezone
  - Deal creation date
  - Approval date and time
  - Document generation timestamp
  - Header date display
- **Import**: Added `from models import utc_to_pakistan`
- **Consistent Format**: All dates follow DD-MM-YYYY HH:MM AM/PM format

### 3. HTML Templates
Updated the following templates to use Pakistan timezone:

#### Deal PDF Template (deal_pdf.html)
- Generated on timestamp
- Deal creation date
- Approval date

#### Deal Details Template (deal_details.html)
- Created date in deal information
- Created date in summary sidebar

#### User Deals Template (user_deals.html)
- Deal creation dates in table

#### Admin Deals Template (admin_deals.html)
- Deal creation dates in admin table

#### User Dashboard Template (user_dashboard.html)
- Product registration dates

### 4. Application Context (app.py)
- **Template Context Function**: Added `utc_to_pakistan()` to global template context
- **Available in all templates**: Function can be used as `{{ utc_to_pakistan(datetime_field) }}`
- **Existing Filters**: Maintained existing `pakistan_time` and `pakistan_date` filters

## Format Standards

### Date and Time Display
- **Full DateTime**: `31-07-2025 04:43 PM`
- **Date Only**: `31-07-2025`
- **Time Zone**: Asia/Karachi (GMT+5)

### Usage in Templates
```html
<!-- Full date and time -->
{{ utc_to_pakistan(deal.created_at) }}

<!-- Date only -->
{{ utc_to_pakistan(deal.created_at).split(' ')[0] }}
```

### Usage in Python Code
```python
from models import utc_to_pakistan

# Convert UTC datetime to Pakistan timezone string
pakistan_time_str = utc_to_pakistan(deal.created_at)
```

## Files Modified

1. `models.py` - Updated timezone conversion function
2. `pdf_generator.py` - Updated PDF generation with Pakistan timezone
3. `app.py` - Added template context function
4. `templates/deal_pdf.html` - Updated datetime displays
5. `templates/deal_details.html` - Updated datetime displays
6. `templates/user_deals.html` - Updated datetime displays
7. `templates/admin_deals.html` - Updated datetime displays
8. `templates/user_dashboard.html` - Updated datetime displays

## Testing

A test script `test_timezone.py` has been created to verify the timezone functionality:

```bash
python test_timezone.py
```

Expected output format: `01-08-2025 05:17 AM`

## Benefits

1. **Consistent User Experience**: All timestamps show local Pakistan time
2. **User Friendly Format**: 12-hour format with AM/PM indicator
3. **Regional Compliance**: Matches local time zone expectations
4. **PDF Documents**: Generated documents show correct local timestamps
5. **Admin/User Panels**: Both interfaces show consistent timezone information

## Future Considerations

- All new datetime fields should use the `utc_to_pakistan()` function for display
- Database timestamps remain in UTC for consistency
- Additional timezone support can be added by extending the current framework
