import csv
import json
import re

import pandas as pd

from src.RegionContentExtractor import RegionContentExtractor



class ContentExtractor:


    def __init__(self, folder):
        """
        Initializes the ContentExtractor object.

        Args:
        - folder: The folder path where the input and output files are located.
        """

        self.folder_path = folder
        self.output_file_path = f'output.csv'
        self.input_file = open(f'{folder}/structuredData.json')
        self.data = json.load(self.input_file)
        self.input_file.close()

        self.bill_table = None
        self.tables_name = None

        self.region_content_extractor = RegionContentExtractor(self.data)
        
        self.business_name = None
        self.business_description = None
        self.tax = 10

    
    def __construct_dictionary(self, keys: list, values: list) -> dict:
        """
        Constructs a dictionary using the given keys and values.

        Args:
        - keys: List of keys for the dictionary.
        - values: List of values for the dictionary.

        Returns:
        - dict: Dictionary constructed using the keys and values.

        Raises:
        - Exception: If the number of keys and values is different.
        """

        if(len(keys) != len(values)):
            raise Exception('Unequal number of keys and values passed for dictionary construction')
        
        #Constructing a dictionary while also stripping whitespaces from the start and end of the 
        #strings. The Extract API often adds whitespaces at the end of texts. 
        output = dict()
        for i, key in enumerate(keys):
            output[key] = str(values[i]).strip()
        
        return output
    

    def __get_business_details(self, name: str, description: str, address: list) -> dict:
        """
        Extracts the business details from the given information.

        Args:
        - name: The business name.
        - description: The business description.
        - address: List of lines in the business address.

        Returns:
        - dict: Dictionary containing the extracted business details.
        """
        # address format: 'Name StreetAddress, City, Country Zipcode '
        address = ''.join(address)
        address = address[len(name):]

        # address format: 'StreetAddress, City, Country Zipcode '
        # Zipcode is a 5 digit code and the string ends with a space
        zipcode = address[-6:-1]
        address = address[:-6]

        # address format: 'StreetAddress, City, Country '
        streetAddressEndingIndex = address.find(',')
        streetAddress = address[:streetAddressEndingIndex]
        address = address[streetAddressEndingIndex+2:]

        # address format: 'City, Country '
        cityEndingIndex = address.find(',')
        city = address[:cityEndingIndex]
        address = address[cityEndingIndex+2:]

        # address format: 'Country '
        country = address
        
        keys = ['City', 'Country', 'Description', 'Name', 'StreetAddress', 'Zipcode']
        values = [city, country, description, name, streetAddress, zipcode]

        return self.__construct_dictionary(keys, values)


    def __get_customer_details(self, customerData: list) -> dict:
        """
        Extracts the customer details from the given information.

        Args:
        - customerData: List of lines containing customer data.

        Returns:
        - dict: Dictionary containing the extracted customer details.
        """

        #The text in the customer region contains the 'BILL TO ' substring which is not required
        customerData.remove('BILL TO ')
        
        name = customerData[0].strip()
        customerData = customerData[1:]
        #Accounting for longer names which may get split into multiple lines on the PDF
        #name is followed by email which'll include an '@' symbol
        while(not re.search('@', customerData[0])):
            name += customerData[0].strip()
            customerData = customerData[1:]

        email = customerData[0].strip()
        customerData = customerData[1:]
        #Accounting for longer emails which may get split into multiple lines on the PDF
        #email is followed by phone number which'll include '-' symbols
        while(not re.search('-', customerData[0])):
            email += customerData[0].strip()
            customerData = customerData[1:]

        #Extracting the phone number
        phone = customerData[0]
        customerData = customerData[1:]

        #Extracting address lines
        addressLine1, addressLine2 = customerData[0], customerData[1]
        
        keys = ['Address__line1', 'Address__line2', 'Email', 'Name', 'PhoneNumber']
        values = [addressLine1, addressLine2, email, name, phone]

        return self.__construct_dictionary(keys, values)
    

    def __get_ivoice_details(self, billRow: pd.core.series.Series, tax: str, \
                             numberAndIssueDate: list, description: list, dueDate: list) -> dict:
        """
        Extracts the invoice details from the given information.

        Args:
        - billRow: The bill row containing details.
        - tax: The tax value.
        - numberAndIssueDate: List of lines containing the invoice number and issue date.
        - description: List of lines containing the invoice description.
        - dueDate: List of lines containing the due date.

        Returns:
        - dict: Dictionary containing the extracted invoice details.
        """

        #The text in the invoice region may contain the 'DETAILS ' substring which is not required
        if 'DETAILS ' in description:
            description.remove('DETAILS ')
        description = ''.join(description)

        #Extracting the due date using regular expressions
        dueDate = ''.join(dueDate)
        dueDate = re.search('[0-9]{2}-[0-9]{2}-[0-9]{4}', dueDate) \
            .group()

        #Extracting the issue date using regular expressions
        numberAndIssueDate = ''.join(numberAndIssueDate)
        issueDate = re.search('[0-9]{2}-[0-9]{2}-[0-9]{4}', numberAndIssueDate) \
            .group()
        
        #Replacing the following substring with blank strings leaves us with the invoice number
        numberAndIssueDate = numberAndIssueDate.replace(issueDate, '') \
            .replace('Invoice# ', '') \
            .replace(' Issue date ', '')
        invoiceNumber = numberAndIssueDate

        #Extracting the bill details from the pandas table created using CSV from the ExportPDF API  
        billName, billQuantity, billRate = billRow.iloc[:3]    

        keys = ['BillDetails__Name', 'BillDetails__Quantity', 'BillDetails__Rate', \
                'Description', 'DueDate', 'IssueDate', 'Number', 'Tax']
        values = [billName, billQuantity, billRate, \
                  description, dueDate, issueDate, invoiceNumber, tax]

        return self.__construct_dictionary(keys, values)
    

    def extract(self):
        """
        Extracts the content from the input data.
        """

        #Extracting region based contents
        self.region_content_extractor.extract()

        titleFlag = False
        taxFlag = False
        tableFlag = False

        for element in self.data['elements']:
            
            #Extracting a level deeper components inside nested elements
            components = list()
            if 'Kids' in element.keys():
                for kidElement in element['Kids']:
                    components.append(kidElement)
            else:
                components.append(element)
            
            #The element immediately after the element with text as 'Tax % ' contains the tax value
            for component in components:
                if taxFlag and 'Text' in component.keys():
                    if '$' not in component['Text']:
                        taxFlag = False
                        self.tax = component['Text']
                if 'Text' in component.keys() and component['Text'] == 'Tax % ':
                    taxFlag = True

            #Extracting the business name and description
            if titleFlag:
                self.business_description = element['Text']
                titleFlag = False
            if 'TextSize' in element.keys() and element['TextSize'] > 24:
                self.business_name = element['Text']
                titleFlag = True

            #Extracting the bill tables
            if 'attributes' in element.keys():
                if 'NumCol' in element['attributes'].keys():
                    if element['attributes']['NumCol'] == 4:
                        if tableFlag:
                            self.tables_name = element['filePaths']
                            tableFlag = False
                        else:
                            tableFlag = True
            

    def __create_output_dictionary(self, businessDetails, customerDetails, invoiceDetails):
        """
        Creates the output dictionary by combining business, customer, and invoice details.

        Args:
        - businessDetails: Dictionary containing business details.
        - customerDetails: Dictionary containing customer details.
        - invoiceDetails: Dictionary containing invoice details.

        Returns:
        - dict: Dictionary containing the combined output.
        """

        output = dict()
        for prefix, container in zip(['Business', 'Customer', 'Invoice'], \
                                     [businessDetails, customerDetails, invoiceDetails]):
            for key in container.keys():
                output[f'{prefix}__{key}'] = container[key]

        return output
    

    def save_extracted_content(self, outputFilePath):
        """
        Saves the extracted content to the output file.
        
        Args:
        - outputFilePath: Path of the CSV where the data needs to be appended/saved.
        """

        #Extracting all business details
        businessAddress = self.region_content_extractor.get_business_address()
        business_details = self.__get_business_details(
            self.business_name, 
            self.business_description, 
            businessAddress
        )

        #Extracting all customer details
        customerData = self.region_content_extractor.get_customer_data()
        customer_details = self.__get_customer_details(customerData)

        for table in self.tables_name:
            self.bill_table = pd.read_csv(f'{self.folder_path}/{table}', header=None, dtype=str)
            #Iterating over item rows in the invoice
            for index, row in self.bill_table.iterrows():
                #Extracting all invoice details
                invoiceData = self.region_content_extractor.get_invoice_data()
                invoice_details = self.__get_ivoice_details(row, self.tax, **invoiceData)

                output_dictionary = self.__create_output_dictionary(
                    business_details, 
                    customer_details, 
                    invoice_details
                )
                
                #Appending to the output file
                with open(outputFilePath, 'a', newline='') as file:
                    writer = csv.writer(file)
                    writer.writerow(output_dictionary.values())
