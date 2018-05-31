import boto3
from prettytable import PrettyTable
from re import compile
import re

x = PrettyTable(["Action", "ResourceID", "ResourceType"])

class Change_Set(object):

    def __init__(self):
        self.create_clients()
        self.get_stacks()

    def create_clients(self):
        self.cf = boto3.client('cloudformation', region_name='eu-west-1')
        self.s3 = boto3.client('s3', region_name='eu-west-1')

    def check_bucket_name(self):
        if '..' in self.new_name:
            raise ValueError("%s is not a valid s3 bucket name" % self.new_name)

        ip_re = compile(r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$')
        if ip_re.match(self.new_name):
            raise ValueError("%s is not a valid s3 bucket name" % self.new_name)

        bucket_name_re = compile(r'^[a-z\d][a-z\d\.-]{1,61}[a-z\d]$')
        if bucket_name_re.match(self.new_name):
            return self.new_name
        else:
            raise ValueError("%s is not a valid s3 bucket name" % self.new_name)

    def get_stacks(self):
        d = self.cf.describe_stacks()
        s = d['Stacks']
        STACK_CHECK = []
        for stack in s:
            print(stack['StackName'])
            STACK_CHECK.append(stack['StackName'])
        print("\n")
        self.stack_name = input("What stack do you want to create a change set for?")
        if self.stack_name in STACK_CHECK:
            self.upload_new_template()
        else:
            print("%s is not a stack that exists" % self.stack_name)


    def upload_new_template(self):
        b = self.s3.list_buckets()
        bu = b['Buckets']
        choice = input("Do you want to create a new bucket to upload the template or upload to an existing?")
        print("\n")
        if choice == "existing":
            for bucket in bu:
                if re.search('cf-templates*', bucket['Name']):
                    print (bucket['Name'])
                else:
                    pass
        else:
            self.new_name = input("What do you want to call the bucket?")
            self.check_bucket_name()
            self.s3.create_bucket(ACL='private', Bucket=self.new_name)
        print("\n")
        self.upload_bucket = input("Which bucket do you want to upload your new template to?")
        file_path = input("Where is your file stored, please enter full path name?")
        self.file_name = input("What do you want the file to be called on s3?")
        data = open(file_path, 'rb')
        try:
            self.s3.put_object(Bucket=self.upload_bucket, Key=self.file_name, Body=data)
        except Exception as e:
            print(e)

        self.create_change_set()


    def create_change_set(self):
        desc = input("Enter Description for change set?")
        self.cf.create_change_set(
            StackName=self.stack_name,
            TemplateURL="https://s3-eu-west-1.amazonaws.com/{0}/{1}".format(self.upload_bucket, self.file_name),
            ChangeSetName="ChangeSetScript",
            Description=desc
        )

    def describe_change_set(self):
        c = self.cf.describe_change_set(
            ChangeSetName='ChangeSetScript',
            StackName=self.stack_name
        )
        change = c['Changes']
        for each in change:
            res = each['ResourceChange']
            x.add_row([res['Action'], res['LogicalResourceId'], res['ResourceType']])
        print(x)


Change_Set()