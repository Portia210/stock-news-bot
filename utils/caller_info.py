import inspect

def get_caller_info():
    """Get information about the calling function"""
    try:
        # Get the stack trace
        stack = inspect.stack()
        # The caller is at index 2 (0=current function, 1=this function, 2=caller)
        if len(stack) >= 3:
            caller_frame = stack[2]
            filename = caller_frame.filename.split('/')[-1]  # Just the filename
            line_number = caller_frame.lineno
            return f"{filename}:{line_number}"
        else:
            return "unknown"
    except Exception:
        return "unknown" 