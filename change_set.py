import boto3
from prettytable import PrettyTable
from re import compile
import re
import os


x = PrettyTable(["Action", "ResourceID", "ResourceType", "Replacement", "Scope", "Details"])
x1 = PrettyTable(["Action", "ResourceID", "ResourceType", "Scope", "Details"])

class Change_Set(object):

    def __init__(self):
        self.create_clients()
        self.get_stacks()

    def create_clients(self):
        print ("You're cwd is {}".format(os.getcwd()))
        self.cf = boto3.client('cloudformation', region_name='eu-west-1')
        self.s3 = boto3.client('s3', region_name='eu-west-1')
        self.waiter = self.cf.get_waiter('stack_update_complete')

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
        elif choice == "new":
            self.new_name = input("What do you want to call the bucket?")
            self.check_bucket_name()
            self.s3.create_bucket(ACL='private', Bucket=self.new_name)
        elif choice != "new" or "existing":
            print("That is not a valid entry...")
            self.upload_new_template()
        print("\n")
        self.upload_bucket = input("Which bucket do you want to upload your new template to?")
        print("\n")
        local_file = input("Please enter the template name you wish to upload.")
        print("\n")
        self.file_name = input("What do you want the file to be called on s3?")
        data = open(os.getcwd()+"/" + local_file, 'rb')
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
        self.waiter.wait(StackName=self.stack_name,
                         WaiterConfig={'Delay': 15})
        self.describe_change_set()

    def describe_change_set(self):
        c = self.cf.describe_change_set(
            ChangeSetName='ChangeSetScript',
            StackName=self.stack_name
        )
        change = c['Changes']
        for each in change:
            res = each['ResourceChange']
            if res['Action'] == "Modify":
                x.add_row([res['Action'], res['LogicalResourceId'], res['ResourceType'], res['Replacement'],res['Scope'],
                       res['Details']])
            else:
                x1.add_row(
                    [res['Action'], res['LogicalResourceId'], res['ResourceType'], res['Replacement'], res['Scope'],
                     res['Details']])
        print(x)
        print(x1)

        choice = input("Do you want to execute, delete or keep change-set?")
        if choice == "execute":
            self.execute_change_set()
        elif choice == "delete":
            self.delete_change_set()
        elif choice == "keep":
            print("Your change set will be kept")

    def execute_change_set(self):
        self.cf.execute_change_set(
            ChangeSetName='ChangeSetScript',
            StackName=self.stack_name
        )

        e = self.cf.describe_stack_events(
            StackName=self.stack_name
        )

        events = e['StackEvents']
        for event in events:
            self.waiter.wait(StackName=self.stack_name,
                             WaiterConfig={'Delay': 15})



    def delete_change_set(self):
        r = self.cf.delete_change_set(
            ChangeSetName='ChangeSetScript',
            StackName=self.stack_name
        )
        if r == {}:
            print("Change set deleted successfully...")


Change_Set()