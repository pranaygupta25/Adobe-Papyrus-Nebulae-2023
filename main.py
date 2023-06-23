import os
from zipfile import ZipFile

from src.ContentExtractor import ContentExtractor
from src.PDFDataExtractor import PDFDataExtractor
from src.utils import setup_output_csv, delete_directory as cleanup



#Path to the directory containing the input PDFs
input_folder_path = './res'
#Path to the directory where the output CSV will be saved
output_folder_path = './out'
#Path to the output CSV
output_file_path = f'{output_folder_path}/result.csv'



if __name__ == '__main__':
    
    intermediate = './temp'
    #Setting up the output CSV
    setup_output_csv(output_file_path)

    num_files = len(os.listdir(input_folder_path))

    #Iterating over files in the input directory
    for index, filename in enumerate(os.listdir(input_folder_path)):

        print(f'Processing File {index+1:>4}/{num_files:<4}: {filename}')
        
        file = os.path.join(input_folder_path, filename)
        if os.path.isfile(file):

            #Extracting JSON and table data CSVs from the PDF using Adobe ExtractPDF API
            pdf_extractor = PDFDataExtractor(file, f'{intermediate}.zip')
            pdf_extractor.set_credentials('./pdfservices-api-credentials.json')
            pdf_extractor.initialize_operation()
            pdf_extractor.set_ExtractPDF_options()
            pdf_extractor.extract()

            #Unzipping the output from the API to an intermediate directory
            with ZipFile(f'{intermediate}.zip', 'r') as zip:
                zip.extractall(intermediate)
            #Deleting the original zip file
            pdf_extractor.cleanup()

            #Extracting contents from the outputs of the API
            content_extractor = ContentExtractor(f'{intermediate}')
            content_extractor.extract()
            content_extractor.save_extracted_content(output_file_path)
            #Deleting the intermediate directory with contents
            cleanup(intermediate)
    
    print(f'All {num_files} files extracted successfully!')