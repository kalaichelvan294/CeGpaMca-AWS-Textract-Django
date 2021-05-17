# CeGpaMca-AWS_Textract-Django

A sample GPA Calculation for Semester Result of MCA students studying in College of Engineering Guindy, Anna University, Chennai-25.

Application developed in the purpose of learning Amazon AWS Textract service, PythonAnywhere cloud python Web project Hosting, and Django web framework.

## Authors

Kalai chelvan & Aravindhan

## Architecture

![alt text](https://github.com/kalaichelvan-kn/CeGpaMca-AWS-Textract-Django/blob/master/myarchi.png?raw=true "Architecture Diagram")

## Pre-requisites

- python programming language

- Html, CSS, and JS.

- Django Python Framework. 

- Amazon AWS Textract service. [click here for more info](https://aws.amazon.com/textract/)

## Pre-Installation Steps

- Install python. [click here for more info](https://www.python.org/)

- Install Django. [click here for more info](https://www.djangoproject.com/)

- Amazon AWS
  - IAM Role Account creation (permission to access only Textract service)
  - Getting Access Key Id and Secret Access key
  - Install AWS-cli and configure the IAM account. [click here for more info](https://docs.aws.amazon.com/cli/latest/userguide/cli-chap-install.html)
    
        pip install awscli

  - Install boto3 using the command.

        pip install boto3

## Server Implementation

- Follow Pre-Installation Steps.

- Create Django Web App in pythonanywhere.com

- Import the project

- Run the commands in the bash console for python support inside the project directory, where x.x stands for python version example: python3.8

        pythonx.x manage.py makemigrations
        pythonx.x manage.py migrate

## Live Server @

Website Link : <https://kalaichelvankn.pythonanywhere.com/>

Example Input semester result:

![alt text](https://github.com/kalaichelvan-kn/CeGpaMca-AWS-Textract-Django/blob/master/exampleresult.jpg?raw=true "Example semester result image")

Example Output:

![alt text](https://github.com/kalaichelvan-kn/CeGpaMca-AWS-Textract-Django/blob/master/examplevideo.gif?raw=true "Example output gif")
