import os

from adobe.pdfservices.operation.auth.credentials import Credentials
from adobe.pdfservices.operation.execution_context import ExecutionContext
from adobe.pdfservices.operation.io.file_ref import FileRef
from adobe.pdfservices.operation.pdfops.extract_pdf_operation import \
    ExtractPDFOperation
from adobe.pdfservices.operation.pdfops.options.extractpdf.extract_element_type import \
    ExtractElementType
from adobe.pdfservices.operation.pdfops.options.extractpdf.extract_pdf_options import \
    ExtractPDFOptions
from adobe.pdfservices.operation.pdfops.options.extractpdf.table_structure_type import \
    TableStructureType



class PDFDataExtractor:
    

    def __init__(self, inputFile, outputZipFile):

        self.input_file = inputFile
        self.output_zip_file = outputZipFile
        self.api_credentials_JSON = None
        self.execution_context = None
        self.extract_pdf_operation = ExtractPDFOperation.create_new()


    def set_credentials(self, credentialFile):

        self.api_credentials_JSON = credentialFile

        #Initial setup, create credentials instance.
        credentials = Credentials.service_account_credentials_builder()\
            .from_file(self.api_credentials_JSON) \
            .build()
        
        #Create an ExecutionContext using credentials and create a new operation instance.
        self.execution_context = ExecutionContext.create(credentials)

        
    def initialize_operation(self):

        #Set operation input from a source file.
        source = FileRef.create_from_local_file(self.input_file)
        self.extract_pdf_operation.set_input(source)

    
    def set_ExtractPDF_options(self, options= None):
        
        #If not passed as an argument, build ExtractPDF options as per requirements of the 
        #Papyrus Nebulae 2023 
        if(not options):
            options: ExtractPDFOptions = ExtractPDFOptions.builder() \
                .with_elements_to_extract([ExtractElementType.TEXT, ExtractElementType.TABLES]) \
                .with_table_structure_format(TableStructureType.CSV) \
                .with_include_styling_info(True) \
                .build()
        
        #Set options into the operation
        self.extract_pdf_operation.set_options(options)

    
    def extract(self):

        #Execute the actual extraction operation
        result: FileRef = self.extract_pdf_operation.execute(self.execution_context)

        #Save the result to the specified location
        result.save_as(self.output_zip_file)

    
    def cleanup(self):
        if os.path.isfile(self.output_zip_file):
            os.remove(self.output_zip_file)