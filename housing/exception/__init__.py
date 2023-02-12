import os
import sys

# create custom class by inheriting Exception, the parent class from python
class HousingException(Exception):
    
    def __init__(self, error_message:Exception, error_detail:sys):
        '''error_message is the object, captures what error occured in the file,
        error_detail:sys captures which file, which line had an error'''
        super().__init__(error_message)
        '''pass error_message to parent class, Exception, equlivalent to 
                Exception(error_message)
        prepare the error message'''
        self.error_message = HousingException.get_detailed_error_message(error_message=error_message,
                                                                       error_detail=error_detail
                                                                        )

        # self.error_message=error_message
        
    ## prepare nice format for error_message and error_detail
    @staticmethod
    def get_detailed_error_message(error_message:Exception, error_detail:sys) -> str: 
        '''
        method returns o/p as str
        
        error_message: Exception object
        error_detail: object of sys
        '''
        _,_,exec_tb = error_detail.exc_info() 
        ''' returns tuple (type, info, traceback); since i need only 3rd element i.e 
        traceback means what file, what line has error, i used _,_,_exec_tb'''
        exception_block_line_number = exec_tb.tb_frame.f_lineno # get the line number
        try_block_line_number = exec_tb.tb_lineno
        file_name = exec_tb.tb_frame.f_code.co_filename # file name in which error is there
        
        error_message = f"""
        
        Error occured in script: 
        [ {file_name} ] at 
        try block line number: [{try_block_line_number}] and exception block line number: [{exception_block_line_number}] 
        error message: [{error_message}]
        """
        return error_message
        
    # write dunder method
    def __str__(self):
        return self.error_message


    def __repr__(self) -> str:
        return HousingException.__name__.str()
