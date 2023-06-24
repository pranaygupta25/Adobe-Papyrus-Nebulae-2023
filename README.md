# PapyrusNebulae 2023 Document Cloud Hackathon: Round 1

This repository contains the solution for Round 1 of the PapyrusNebulae 2023 Document Cloud Hackathon. The objective of this round is to extract information from PDF invoices using the Adobe PDF Services Extract API. The extracted data should be in the same format as the provided csv file.

<br>

## Problem Description
The problem involves extracting information from PDF invoices using the Adobe PDF Services Extract API. The API documentation can be found at: Adobe PDF Services Extract API.

<br>

## Usage

Follow the below-mentioned steps to use the project on your system:

- Clone this repository to your local machine
    ```
    git clone https://github.com/pranaygupta25/Adobe-Papyrus-Nebulae-2023.git
    ```

- Install the dependencies for the project
    ```
    pip install -r .\requirements.txt
    ```


- You'll need to sign up for an Adobe PDF Services account if you haven't already. [This page](https://developer.adobe.com/document-services/apis/pdf-extract/) has instructions on how to get started with the free trial.

- Copy the ```pdfservices-api-credentials.json``` and ```private.key``` from the previous step into the [root directory](./) of the project.

- Run the [main.py](./main.py) file from the root directory of the project.

- The output file would be ready inside the [out folder](./out/) present in the root directory after completion of the program.
