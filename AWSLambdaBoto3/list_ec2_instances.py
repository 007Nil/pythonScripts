# Author : Sagnik Sarkar
import boto3
from botocore.exceptions import ClientError
import json
from pprint import pprint
from datetime import datetime, timezone
import time
import datetime

# Declare variables for search instances
cluster_name = "c01"
count_node = 0
terminated = "terminated"
# Defining Lists
instance_required_details = []
list_of_tags = []
node_details = []


#  Class Definition
class Ec2InstanceDetails:
    def __init__(self, instance_id=None, tags=None, state=None, launchDate=None, launchTime=None,
                 runtimeEC2instance=None):
        self.runtimeEC2instance = runtimeEC2instance
        self.launchTime = launchTime
        self.launchDate = launchDate
        self.state = state
        self.tags = tags
        self.instance_id = instance_id


class NodeDetails:
    def __init__(self, nodename=None, node_state=None, launchDate=None, launchTime=None, runtimeEC2instance=None):
        self.runtimeEC2instance = runtimeEC2instance
        self.launchTime = launchTime
        self.launchDate = launchDate
        self.nodename = nodename
        self.node_state = node_state

    def dict(self):
        dict = {"Node Name": self.nodename, "Node State": self.node_state, "Launch Time": self.launchTime,
                "Launch Date": self.launchDate,"Up Time":self.runtimeEC2instance}
        return dict


# ses configurations
def ses_function(info_data):
    sender = ""
    recipient = ""
    aws_region = "ap-south-1"
    table_details = ""
    for info_data_each_node_details in info_data['Node details']:
        table_details += "<tr>" \
                         "<td align='center'>" + info_data_each_node_details['Node Name'] + "</td>" \
                         "<td align='center'>" + \
                         info_data_each_node_details['Node State'] +\
                         "</td>" \
                         "<td align='center'>" + \
                         info_data_each_node_details['Launch Date'] + \
                         " " + \
                         info_data_each_node_details["Launch Time"] + "</td>" \
                         "<td align='center'>" + \
                         info_data_each_node_details["Up Time"] + "</td>" \
                         "</tr>"

    # print(table_details)
    subject = "EC2 instance monitoring details based on Cluster<Chamber> Name"

    body_text = "This email was sent with Amazon SES using the AWS SDK for Python (Boto3)."

    body_html = "<!DOCTYPE html>" \
                "<html lang='en'>" \
                "<head>" \
                "<meta charset='UTF-8'>" \
                "<meta name='viewport' content='width=device-width, initial-scale=1.0'>" \
                "<title>Document</title>" \
                "</head>" \
                "<body>" \
                "<p align='center'>Cluster Name: " + info_data["Cluster Name"] + "</p>" \
                "<p align='center'>Node Count: " + info_data["Node Count"] + "</p>" \
                "<p align='center'>Node details</p>" \
                "<table style='width:50%' align='center'>" \
                "<tr>" \
                "<th>Node Name</th>" \
                "<th>Node State</th>" \
                "<th>Node Start Date and Time</th>" \
                "<th>Up Time</th>" \
                "</tr>" + table_details + \
                "</table>" \
                "</body>" \
                "</html>"
    print(body_html)
    CHARSET = "UTF-8"

    # Create a new SES resource and specify a region.
    client = boto3.client('ses', region_name=aws_region)

    # Try to send the email.
    try:
        # Provide the contents of the email.
        response = client.send_email(
            Destination={
                'ToAddresses': [
                    recipient,
                ],
            },
            Message={
                'Body': {
                    'Html': {
                        'Charset': CHARSET,
                        'Data': body_html,
                    },
                    'Text': {
                        'Charset': CHARSET,
                        'Data': body_text,
                    },
                },
                'Subject': {
                    'Charset': CHARSET,
                    'Data': subject,
                },
            },
            Source=sender,
        )
    # Display an error if something goes wrong.
    except ClientError as e:
        print(e.response['Error']['Message'])
    else:
        print("Email sent! Message ID:"),
        print(response['MessageId'])


# sns topic function
def sns_function(json_data):
    topic_arn = "arn:aws:sns:ap-south-1:254018427142:EC2TestTopic"
    sns_client = boto3.client(
        'sns',
        region_name="ap-south-1"
    )

    publicObject = json_data
    # print(publicObject)

    response = sns_client.publish(TopicArn=topic_arn,
                                  Message=publicObject,
                                  )

    print(response["ResponseMetadata"]["HTTPStatusCode"])


# EC2 INSTANCE CLIENT
ec2_client = boto3.client(service_name="ec2", region_name="ap-south-1")
ec2_instance_details = ec2_client.describe_instances()

# preparing required Data
for each_instance in ec2_instance_details['Reservations']:

    # print(each_instance)
    for each_instance_requried_details in each_instance['Instances']:
        launchTime_utc = each_instance_requried_details["LaunchTime"]
        now_utc = launchTime_utc.replace(tzinfo=timezone.utc)
        now_local = now_utc.astimezone()
        run_time_EC2_instance = "--"
        # end = datetime.now()
        if each_instance_requried_details["State"]["Name"] != "terminated":
            end_time = datetime.datetime.now().replace(microsecond=0)
            print(end_time)
            run_time_EC2_instance= (end_time - now_local.replace(tzinfo=None))
        instance_required_details.append(Ec2InstanceDetails(each_instance_requried_details["InstanceId"],
                                                            each_instance_requried_details["Tags"],
                                                            each_instance_requried_details["State"]["Name"],
                                                            str(now_local.date()),
                                                            str(now_local.time()),
                                                            str(run_time_EC2_instance)))

# print(instance_requried_details[0].tags[0]["Key"])
# print(instance_requried_details[0].state,'Cluster Name='+instance_requried_details[0].tags[0]["Value"]
#       ,'Node Name='+instance_requried_details[0].tags[1]["Value"])

for each_instance_list_data in instance_required_details:
    list_of_tags.append(each_instance_list_data.tags)
    # print(each_instance_list_data.tags)
for each_list_of_tags in list_of_tags:
    for each_key_in_list_of_tags in each_list_of_tags:
        # print(each_key_in_list_of_tags["Key"])
        if cluster_name == each_key_in_list_of_tags["Value"] and each_key_in_list_of_tags["Key"] == "Cluster":
            # print(each_key_in_list_of_tags)
            count_node += 1

        # else:
        #     print("Cluster Not Found")

    # print("Cluster ")

if count_node > 0:
    # print("Cluster " + cluster_name + " contains " + str(count_node) + " nodes")
    # print("Node status Details -----")

    for each_instance_list_data in instance_required_details:
        for each_instance_list_data_in_tags in each_instance_list_data.tags:
            # print(each_instance_list_data_in_tags["Value"])
            if each_instance_list_data_in_tags["Value"] == cluster_name:

                for tag_name in each_instance_list_data.tags:
                    # print()
                    if tag_name["Key"] == "Name":
                        node_details.append(NodeDetails(tag_name["Value"], each_instance_list_data.state,
                                                        each_instance_list_data.launchDate,
                                                        each_instance_list_data.launchTime,
                                                        each_instance_list_data.runtimeEC2instance).dict())

    publish_object = {"Cluster Name": cluster_name, "Node Count": str(count_node),
                      "Node details": node_details}

    # print(publish_object)
    json_data = json.dumps(publish_object)
    info = json.loads(json_data)
    pprint(info)
    ses_function(info)
    # pprint(info['Node details'][1]['Node Name'])
    # for each_node_details in info['Node details']:
    #     print(each_node_details['Node Name'])
    # sns_function(json_date)

else:
    print("Cluster " + cluster_name + " contains 0 nodes, Since it does not exist")
    publish_object = {"Cluster Name": cluster_name, "Node Count": str(count_node), "Node details": node_details}
    print(json.dumps(publish_object))

