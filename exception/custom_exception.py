import sys
import traceback

from logger.custom_logger import CustomLogger
logger=CustomLogger().get_logger(__file__)

class DocumentPortalException(Exception):
    """Custom exception for Document Portal"""
    def __init__(self, error_message, error_details=None):
        if error_details is None:
            error_details = sys
        
        # Check if error_details is the sys module or has exc_info method
        if hasattr(error_details, 'exc_info'):
            exc_info = error_details.exc_info()
        else:
            # If error_details is not sys module, get current exception info
            exc_info = sys.exc_info()
        
        _, _, exc_tb = exc_info
        
        if exc_tb is not None:
            self.file_name = exc_tb.tb_frame.f_code.co_filename
            self.lineno = exc_tb.tb_lineno
            self.traceback_str = ''.join(traceback.format_exception(*exc_info))
        else:
            # Fallback if no traceback available
            self.file_name = "Unknown"
            self.lineno = "Unknown"
            self.traceback_str = "No traceback available"
            
        self.error_message = str(error_message) 
        
    def __str__(self):
       return f"""
        Error in [{self.file_name}] at line [{self.lineno}]
        Message: {self.error_message}
        Traceback:
        {self.traceback_str}
        """
    
if __name__ == "__main__":
    try:
        # Simulate an error
        a = 1 / 0
        print(a)
    except Exception as e:
        app_exc=DocumentPortalException(e,sys)
        logger.error(app_exc)
        raise app_exc