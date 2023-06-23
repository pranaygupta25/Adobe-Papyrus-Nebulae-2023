class RegionContentExtractor():


    def __init__(self, data, regionBoundaries= None):
        """
        Initializes the RegionContentExtractor object.

        Args:
        - data: The input data containing elements and their properties.
        - regionBoundaries: Optional. Dictionary defining the boundaries for each region. 
        If not provided, default boundaries will be used.
        """

        self.data = data
        self.region_contents = {
            'businessAddress': list(),
            'invoiceNumberAndIssueDate': list(),
            'customerDetails': list(),
            'invoiceDescription': list(),
            'invoiceDueDate': list()
        }

        if(regionBoundaries and \
           regionBoundaries.keys() == self.region_contents.keys()):
            self.__region_boundaries = regionBoundaries
        else:
            self.__region_boundaries = {
                'businessAddress': (0, 675, 306, 792),
                'invoiceNumberAndIssueDate': (306, 675, 612, 792),
                'customerDetails': (0, 475, 220, 600),
                'invoiceDescription': (220, 475, 400, 600),
                'invoiceDueDate': (400, 475, 612, 600)
            }
    

    def __is_inside_bounds(self, element_box: list, region: str) -> bool:
        """
        Checks if the given element is inside the boundaries of a specific region.

        Args:
        - element_box: List containing the bounding box coordinates of the element.
        - region: The region to check.

        Returns:
        - bool: True if the element is inside the boundaries, False otherwise.
        """

        #Unpacking the directional extremities of the element and boundary
        leftElement, bottomElement, rightElement, topElement = element_box
        leftBoundary, bottomBoundary, rightBoundary, topBoundary = self.__region_boundaries[region]

        #Checking for the element to be contained within the boundaries along both axes
        horizontallyInBounds = leftElement >= leftBoundary and rightElement <= rightBoundary
        verticallyInBounds = bottomElement >= bottomBoundary and topElement <= topBoundary

        return horizontallyInBounds and verticallyInBounds
    

    def __get_content_from_region(self, element: dict, region: str) -> list:
        """
        Extracts the text content from a specific region of an element.

        Args:
        - element: Dictionary containing the properties of the element.
        - region: The region to extract content from.

        Returns:
        - list: List of extracted text content from the region. Using a list helps in cases where a 
        single component is split into multiple components because of errors from the API
        """

        content = []
        #Text is added to the output only if it is present inside the region boundaries
        if(element['Page'] == 0 and \
           self.__is_inside_bounds(element['Bounds'], region)):
            if('Text' in element.keys()):
                content.append(element['Text'])
        
        return content
    

    def extract(self):
        """
        Extracts the text content from each region for all elements in the data.
        """

        for element in self.data['elements']:
            
            #Extracting a level deeper components inside nested elements
            components = list()
            if 'Kids' in element.keys():
                for kidElement in element['Kids']:
                    components.append(kidElement)
            else:
                components.append(element)
            
            #Extracting the region-wise contents of the components
            for component in components:
                for region in self.__region_boundaries.keys():
                    self.region_contents[region]. \
                        extend(self.__get_content_from_region(component, region))
                    
    
    def get_business_address(self):
        """
        Returns the extracted business address.

        Returns:
        - list: Extracted business address.
        """

        return self.region_contents['businessAddress']
    

    def get_customer_data(self):
        """
        Returns the extracted customer details.

        Returns:
        - list: Extracted customer details.
        """

        return self.region_contents['customerDetails']


    def get_invoice_data(self):
        """
        Returns the extracted invoice data.

        Returns:
        - dict: Dictionary containing extracted invoice data, including 
            - number and issue date, 
            - description, and 
            - due date.
        """

        return {
            'numberAndIssueDate': self.region_contents['invoiceNumberAndIssueDate'],
            'description': self.region_contents['invoiceDescription'],
            'dueDate': self.region_contents['invoiceDueDate']
        }
