import datetime
import boto3
import argparse

parser=argparse.ArgumentParser(
    description='Finds latest ami for bastion server, platform_name accepts names in following formats:'
                'Windows: Windows*YYYY*English*Base'
                'AmazonLinux: amzn*ami-hvm*YYYY*'
                'RHEL: RHEL*7'
                'If you dont specify a platform windows will be chosen by default.')

args=parser.parse_args()
year = datetime.datetime.now()
ec2client = boto3.client('ec2', region_name='eu-west-1')
platform = raw_input("Are you building a linux or windows bastion server?")
platform_name = raw_input("What platform are you looking for?")

if platform == 'linux':
    r = ec2client.describe_images(Filters=[
            {
                'Name': 'name',
                'Values': [platform_name]
            }
        ],
    )

    amis = r['Images']

    for image in amis:
        if image['CreationDate'][:4] == str(year.year):
            print image['ImageId'] + ' | ' + image['Name'] + ' | ' + image['CreationDate'][:10]
        else:
            pass
else:
    r = ec2client.describe_images(Filters=[
            {
                'Name': 'platform',
                'Values': [platform]
            },
            {
                'Name': 'name',
                'Values': [platform_name]
            }
        ],
    )
    amis = r['Images']

    for image in amis:
        if image['CreationDate'][:4] == str(year.year):
            print image['ImageId'] + ' | ' + image['Name'] + ' | ' + image['CreationDate'][:10]
        else:
            pass