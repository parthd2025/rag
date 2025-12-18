# Process Flow Component Documentation

## Overview
The Process Flow component provides a visual horizontal indicator that displays the status of sequential operations in the RAG Chatbot application. It appears on the top-right of the main interface.

## Features

### Status Indicators
- **Grey Circle (◯)** - Pending operation (not started)
- **Yellow Spinning (⟳)** - Processing/In progress
- **Green Checkmark (✓)** - Success completed
- **Red X Mark (✕)** - Error/Failed

### Default Process Flow
The application tracks four main steps:
1. **Upload** - File upload phase
2. **Process** - Document processing phase
3. **Index** - Vector indexing phase
4. **Ready** - System ready state

## Usage

### Import the Component
```python
from components.process_flow import (
    render_process_flow,
    initialize_process_flow,
    update_process_status,
    get_process_flow
)
```

### Initialize Process Flow
```python
# Initialize at app startup
initialize_process_flow(["Upload", "Process", "Index", "Ready"])
```

### Render the Flow
```python
# Display the process flow in a column
with col_flow:
    render_process_flow(get_process_flow())
```

### Update Process Status
```python
# Update status during operations
update_process_status("Upload", "processing")
# ... perform upload ...
update_process_status("Upload", "success")
update_process_status("Process", "processing")
```

### Status Values
- `"pending"` - Not started (grey)
- `"processing"` - In progress (yellow with animation)
- `"success"` - Completed successfully (green)
- `"error"` - Failed (red)

## Visual Example

```
Upload → Process → Index → Ready
(grey)   (yellow)  (green)  (pending)

with symbols:
Upload◯ → Process⟳ → Index✓ → Ready◯
```

## Integration with RAG Chatbot

The process flow is automatically updated during the document upload workflow:

1. **Before Upload**: All steps are pending (grey)
2. **Upload Starts**: Upload step shows processing (yellow)
3. **Upload Completes**: Upload turns green, Process turns yellow
4. **All Steps Done**: All steps turn green after successful indexing
5. **If Error**: Failed step turns red

## Customization

### Customize Process Names
```python
initialize_process_flow(["Validate", "Convert", "Store", "Cache"])
```

### Customize Colors
Edit the CSS in `components/process_flow.py`:
- `.process-step.pending` - Pending color
- `.process-step.processing` - Processing color
- `.process-step.success` - Success color
- `.process-step.error` - Error color

## Technical Details

- **Framework**: Streamlit with HTML/CSS
- **Storage**: Uses Streamlit session state for status persistence
- **Animation**: CSS keyframe animations for processing state
- **Responsive**: Adjusts to container width
