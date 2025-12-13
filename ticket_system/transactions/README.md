# Transactions App Documentation

This app manages the **Daily Operations** and **Production Workflow** for the Ticket System ERP.

## Models & Forms

| Frontend File | Model | Form Class | Editable State | Validation Rules Summary |
| :--- | :--- | :--- | :--- | :--- |
| `sales_order_touch.html` | `SalesOrder` | `SalesOrderForm` | **Draft**: Full <br> **Approved**: Locked | • Delivery Date >= Order Date. <br> • Status Flow: Draft -> Approved -> In Production -> Closed. <br> • Cannot revert from Approved to Draft easily. |
| `job.html` | `JobOrder` | `JobOrderForm` | **Pending**: Full <br> **In Progress**: Restricted | • **Strict Link**: One Job per SO. <br> • Customer derived from SO (ReadOnly). <br> • Cannot create for Draft SO. |
| `print.html` | `PrintingTransaction` | `PrintingTransactionForm` | **Immutable** | • **Mass Balance**: `Input >= Printed + Wastage` <br> • Machine & Operator must be Active. |
| `rewinding.html` | `RewindingTransaction` | `RewindingTransactionForm` | **Immutable** | • **Mass Balance**: `Input >= Output + Wastage` <br> • Machine & Operator must be Active. |
| `sliting.html` | `SlittingTransaction` | `SlittingTransactionForm` | **Immutable** | • **Mass Balance**: `Waste <= Input` <br> • Machine & Operator must be Active. |
| `laminating.html` | `LaminationTransaction` | `LaminationTransactionForm` | **Immutable** | • **Mass Balance**: `Total Input (Plain+Print) >= Output + Wastage` <br> • Machine & Operator must be Active. |
| `core.html` | `CoreTransaction` | `CoreTransactionForm` | **Immutable** | • **Mass Balance**: `Input >= Output + Wastage` <br> • Machine & Operator must be Active. |

## Key Features

### Business Logic
- **Strict Status Flow**: Sales Orders must follow a specific lifecycle (`Draft` -> `Approved` -> ...). Critical fields are locked once Approved.
- **Mass Balance**: All production transactions strictly validate that inputs account for outputs and wastage. You cannot produce more than you consumed.

### Integration
- **Foreign Key Constraints**: `JobOrder` is strictly linked to `SalesOrder`. Transactions are strictly linked to `JobOrder`.
- **Resource Validation**: Forms ensure that only Active Machines and Active Operators can be selected for new transactions.
