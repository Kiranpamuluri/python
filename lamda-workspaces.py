import json
import boto3
import datetime
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart

AWS_REGION = 'ca-central-1'
SOURCE_EMAIL = 'devopsglobal@aaa.ca'
DESTINATION_EMAIL = 'sandeeepk@aaa.ca'
EMAIL_SUBJECT = 'test'
EMAIL_BODY = 'PFA'

def flatten_json(y):
    out = {}

    def flatten(x, name=''):
        if type(x) is dict:
            for a in x:
                flatten(x[a], name + a + '_')
        elif type(x) is list:
            for a in x:
                flatten(a, name)
        else:
            out[name[:-1]] = x

    flatten(y)
    return out

def lambda_handler(event, context):
    print("Collecting Workspaces Data")
    connection = boto3.client('workspaces',region_name=AWS_REGION)
    response = connection.describe_workspaces()
    workspaces = response['Workspaces']
    workspaces = [workspace for workspace in workspaces if not workspace.get('UserVolumeEncryptionEnabled', False) and not workspace.get('RootVolumeEncryptionEnabled', False)]
    if workspaces:
        n_workspaces = []
        for workspace in workspaces:
            if workspace :
                t = {}
                t['WorkspaceId'] = workspace.get('WorkspaceId','')
                t['DirectoryId'] = workspace.get('DirectoryId','')
                t['State'] = workspace.get('State','')
                t['SubnetId'] = workspace.get('SubnetId','')
                t['UserName'] = workspace.get('UserName','')
                t['VolumeEncryptionKey'] = workspace.get('VolumeEncryptionKey','')
                t['UserVolumeEncryptionEnabled'] = workspace.get('UserVolumeEncryptionEnabled', False)
                t['RootVolumeEncryptionEnabled'] = workspace.get('RootVolumeEncryptionEnabled', False)
                n_workspaces.append(t)
        csv_string = ''
        for count, workspace in enumerate(n_workspaces):
            result = flatten_json(workspace)
            str_result = {str(key): str(value) for key, value in result.items()}
            if count == 0 :
                csv_string = ','.join(str_result.keys())
            csv_string = csv_string + '\n' + ','.join(str_result.values())
        ses_client = boto3.client('ses',region_name=AWS_REGION)
        msg = MIMEMultipart()
        msg['Subject'] = EMAIL_SUBJECT
        msg['From'] = SOURCE_EMAIL
        msg['To'] = DESTINATION_EMAIL
        part = MIMEText(EMAIL_BODY)
        msg.attach(part)
        part = MIMEApplication(str.encode(csv_string))
        part.add_header('Content-Disposition', 'attachment', filename='workspaces.csv')
        msg.attach(part)

        response = ses_client.send_raw_email(
            Source=SOURCE_EMAIL,
            Destinations=[DESTINATION_EMAIL],
            RawMessage={'Data':msg.as_string()}
            )