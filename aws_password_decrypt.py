"""Windows Password Decrypter"""

import boto3
import StringIO
from Crypto.PublicKey import RSA
import base64


"""Decrypt Password of instances"""
session = boto3.session.Session(profile_name='', region_name='eu-west-1')
ec2Client = session.client('ec2')

ec2_response = ec2Client.describe_instances(
    Filters=[
        {
            'Name': 'tag-key',
            'Values': [
                '',
            ]
        },
    ],
)

instance = ec2_response['Reservations']
ids = []

# Get the instance ID's so we can loop through them all and decrypt the passwords.
for i in instance:
    instance = i['Instances'][0]
    instanceid = instance['InstanceId']
    ids.append(instanceid)

# Start to decrypt the passwords via the pem key inside jungle disk.
for id in ids:
    pass_response = ec2Client.get_password_data(InstanceId=id)
    output = StringIO.StringIO()
    output.write((pass_response['PasswordData']))
    contents = output.getvalue()
    f = open('./liam.pem', 'r')
    r = RSA.importKey(f.read())
    dmsg = r.decrypt(base64.b64decode(contents))

    # Return the instance ID and the associated password.
    print "Instance ID: {} & Pass: {}".format(id, dmsg[-11:])
