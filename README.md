 **Project: Carbon Footprint Tracking Application**

 **Description:**
 *This application tracks and calculates carbon emissions based on user inputs. It utilizes the Carbon Interface API for emission factor data and stores data in AWS DynamoDB. Users can download generated tables and charts from AWS S3 and receive monthly emission notifications via AWS SNS.*

**Dependencies:**

*Libraries:*
asttokens==3.0.0
attrs==25.2.0
backcall==0.2.0
backports.tarfile==1.2.0
bcrypt==4.3.0
beautifulsoup4==4.13.3
bleach==6.2.0
blessed==1.20.0
boto3==1.37.11
build==1.2.2.post1
cached-property==1.5.2
carbon_footprint_cal==2.0.1
cement==2.10.14
certifi==2025.1.31
cffi==1.17.1
charset-normalizer==2.0.12
colorama==0.4.6
contourpy==1.3.0
cryptography==44.0.2
cycler==0.12.1
decorator==5.2.1
defusedxml==0.7.1
Django==2.1.15
django-jsonfield==1.4.1
docker==4.4.4
docker-compose==1.25.5
dockerpty==0.4.1
docopt==0.6.2
docutils==0.21.2
executing==2.2.0
fastjsonschema==2.21.1
fonttools==4.56.0
future==0.16.0
gunicorn==23.0.0
id==1.5.0
idna==3.10
importlib_metadata==8.6.1
importlib_resources==6.5.2
ipython==8.12.3
jaraco.classes==3.4.0
jaraco.context==6.0.1
jaraco.functools==4.1.0
jedi==0.19.2
jeepney==0.9.0
Jinja2==3.1.6
jmespath==0.10.0
jsonschema==3.2.0
jsonschema-specifications==2024.10.1
jupyter_client==8.6.3
jupyter_core==5.7.2
jupyterlab_pygments==0.3.0
keyring==25.6.0
kiwisolver==1.4.7
markdown-it-py==3.0.0
MarkupSafe==3.0.2
matplotlib==3.9.4
matplotlib-inline==0.1.7
mdurl==0.1.2
mistune==3.1.2
more-itertools==10.6.0
moto==5.1.1
nbclient==0.10.2
nbconvert==7.16.6
nbformat==5.10.4
nh3==0.2.21
numpy==2.0.2
packaging==24.2
pandocfilters==1.5.1
paramiko==3.5.1
parso==0.8.4
pathspec==0.10.1
pexpect==4.9.0
pickleshare==0.7.5
pillow==11.1.0
pipreqs==0.5.0
platformdirs==4.3.6
prompt_toolkit==3.0.50
ptyprocess==0.7.0
pure_eval==0.2.3
pycparser==2.22
Pygments==2.19.1
PyNaCl==1.5.0
pyparsing==3.2.1
pyproject_hooks==1.2.0
pyrsistent==0.20.0
python-dateutil==2.9.0.post0
python-dotenv==1.0.1
pytz==2025.1
PyYAML==5.4.1
pyzmq==26.3.0
readme_renderer==44.0
referencing==0.36.2
requests==2.32.3
requests-mock==1.12.1
requests-toolbelt==1.0.0
responses==0.25.7
rfc3986==2.0.0
rich==13.9.4
rpds-py==0.23.1
s3transfer==0.11.4
SecretStorage==3.3.3
semantic-version==2.10.0
six==1.14.0
soupsieve==2.6
stack-data==0.6.3
termcolor==2.5.0
texttable==1.7.0
tinycss2==1.4.0
tomli==2.2.1
tornado==6.4.2
traitlets==5.14.3
twine==6.1.0
typing_extensions==4.12.2
urllib3==1.26.20
wcwidth==0.2.13
webencodings==0.5.1
websocket-client==0.59.0
Werkzeug==3.1.3
xmltodict==0.14.2
yarg==0.1.9
zipp==3.21.0


*AWS Services:*
- AWS Lambda
- AWS DynamoDB
- AWS S3
- AWS SNS
- AWS EventBridge
- AWS Elastic Beanstalk
- AWS Secrets Manager
- Amazon EventBridge
- Cloud9

*External API:*
- Carbon Interface API (API Key required)

**Deployment Steps:**
1.  **Install Python Dependencies:**
    * Activate virtual environment:
        ```bash
        source venv/bin/activate  # On macOS/Linux
        venv\Scripts\activate      # On Windows
        ```
2. **Push code to git to trigger Github Actions which will run the unit tests and install all dependencies**

3.  **Deploy Lambda Function:**
    * Use the `deploy_lambda.py` script to create or update your Lambda function.
    * Ensure the script includes the correct IAM role ARN, runtime, handler, and environment variables.
    * Run the script:
        ```bash
        python deploy_lambda.py
        ```
    * Verify the Lambda function in the AWS console.
	* The `deploy_lambda.py` script should create the CloudWatch Events rule to trigger the Lambda function monthly.
    * Verify the rule in the AWS console.

4. **Elastic Beanstalk deployment:**
    *Create Elastic Beanstalk application using eb init command.*

    *Create Elastic Beanstalk environment using eb create.*

.   *Once the application is created configure Environment Variables in Elastic Beanstalk to allow password reset email triggers :*
    * Set the following environment variables:
        * `EMAIL_HOST`: smtp.gmail.com
        * `EMAIL_HOST_PASSWORD`: <app password>.
        * `EMAIL_HOST_USER`: emissions.tracker@gmail.com
        * `EMAIL_PORT`: 587
		* `EMAIL_USE_TLS`: True
		
	*Deploy manually using eb deploy command*


