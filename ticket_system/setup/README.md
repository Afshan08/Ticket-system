# Setup App Documentation

This app manages the **Master Data** for the Ticket System ERP.

## Models & Forms

| Frontend File | Model | Form Class | Editable State | Validation Rules Summary |
| :--- | :--- | :--- | :--- | :--- |
| `area.html` | `Area` | `AreaForm` | **Editable** (Status restricted) | • Cannot Deactivate if linked to active Machines/Customers. <br> • Name must be unique. |
| `customer.html` | `Customer` | `CustomerForm` | **Editable** | • Cannot Deactivate/Suspend if Open Sales Orders exist. <br> • Assigned Area must be Active. <br> • Type restricted to controlled list. |
| `item_category.html` | `ItemCategory` | `ItemCategoryForm` | **Restricted** | • Names unique. <br> • Stable identifiers recommended. |
| `item.html` | `Item` | `ItemForm` | **Conditional** | • Price **ReadOnly** if linked to Approved SO. <br> • Dimensions (GSM, Width) must be positive. |
| `machine.html` | `Machine` | `MachineForm` | **Editable** | • Cannot Disable if Active Job Orders assigned. <br> • Speed/Capacity must be positive. |
| `operator.html` | `Operator` | `OperatorForm` | **Editable** | • Soft-delete only (`is_active`). <br> • Role maps to permission groups. |

## Key Features

### Data Integrity
- **Soft Deletes**: `Area`, `Machine`, and `Operator` use status flags (`active`/`inactive`) instead of hard database deletion to preserve historical data in transactions.
- **Dependency Checks**: Before deactivating a master record (e.g., an Area), the system checks if it is currently in use by active customers or machines.

### Integration
- **Forms**: `ModelForms` are defined in `forms.py` and are designed to prevent invalid states (e.g., `CustomerForm` filters for active Areas only).
