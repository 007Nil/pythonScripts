import boto3
from pprint import pprint
from datetime import datetime, timezone
import json
import datetime
from botocore.exceptions import ClientError

# Declaring Variable
tempList = []
instanceRequiredDetails = []
listOfTags = []
nodeCountList = []
nodeDetails = []
listOfNodeDetails = []
clusterDetails = []
publishObject = []


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
    def __init__(self, clusterName=None, nodename=None, node_state=None, launchDate=None, launchTime=None,
                 runtimeEC2instance=None):
        self.clusterName = clusterName
        self.runtimeEC2instance = runtimeEC2instance
        self.launchTime = launchTime
        self.launchDate = launchDate
        self.nodename = nodename
        self.node_state = node_state

    def dict(self):
        dict = {"Cluster Name": self.clusterName, "Node Name": self.nodename, "Node State": self.node_state,
                "Launch Time": self.launchTime,
                "Launch Date": self.launchDate, "Up Time": self.runtimeEC2instance}
        return dict


class ClusterDetails:
    def __init__(self, clusterName=None, numberOfNodes=None, NodeDetails=None):
        self.NodeDetails = NodeDetails
        self.numberOfNodes = numberOfNodes
        self.clusterName = clusterName

    def dict(self):
        dict = {"Cluster Name": self.clusterName, "Number Of Nodes": self.numberOfNodes,
                "Node Details": self.NodeDetails}
        return dict


def sesFunction(infoData):
    dynamicHtmlData = ""

    for eachClusterDetails in infoData:
        dynamicHtmlData += "<p align='center'>" \
                           "Cluster Name: " + eachClusterDetails["Cluster Name"] + "</p>" \
                           "<p align='center'>Node Count: " + str(eachClusterDetails["Number Of Nodes"]) + "</p>" \
                           "<p align='center'>Node details</p>" \
                           "<table style='width:50%' align='center'>" \
                           "<tr>" \
                           "<th>Node Name</th>" \
                           "<th>Node State</th>" \
                           "<th>Node Start Date and Time</th>" \
                           "<th>Up Time</th>" \
                           "</tr>"
        for eachNodeDetails in eachClusterDetails["Node Details"]:
            dynamicHtmlData += "<tr>" \
                               "<td align='center'>" + eachNodeDetails["Node Name"] + "</td>" \
                               "<td align='center'>" + eachNodeDetails["Node State"] + "</td>" \
                               "<td align='center'>" \
                               + eachNodeDetails["Launch Date"] + \
                               " " + \
                               eachNodeDetails["Launch Time"] + \
                               "</td>" \
                               "<td align='center'>" + eachNodeDetails["Up Time"] + "</td>"
        dynamicHtmlData += "</table>" \
                           "<br><br>"


 #   sender = ""
 #   recipient = ""
    aws_region = "ap-south-1"
    subject = "EC2 instance monitoring details based on Cluster<Chamber> Name"
    body_text = "This email was sent with Amazon SES using the AWS SDK for Python (Boto3)."
    #
    body_html = "<!DOCTYPE html>" \
                "<html lang='en'>" \
                "<head>" \
                "<meta charset='UTF-8'>" \
                "<meta name='viewport' content='width=device-width, initial-scale=1.0'>" \
                "<title>Document</title>" \
                "</head>" \
                "<body>" + \
                dynamicHtmlData + \
                "</body>" \
                "</html>"
    # print(body_html)
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


def getEC2Details():
    # EC2 INSTANCE CLIENT
    ec2Client = boto3.client(service_name="ec2", region_name="ap-south-1")
    ec2InstanceDetails = ec2Client.describe_instances()
    # preparing required Data
    for eachInstance in ec2InstanceDetails['Reservations']:

        for eachInstanceRequiredDetails in eachInstance['Instances']:
            launchTimeUTC = eachInstanceRequiredDetails["LaunchTime"]
            nowUTC = launchTimeUTC.replace(tzinfo=timezone.utc)
            nowLocal = nowUTC.astimezone()
            runTimeEC2Instance = "--"
            if eachInstanceRequiredDetails["State"]["Name"] != "terminated":
                endTime = datetime.datetime.now().replace(microsecond=0)
                runTimeEC2Instance = (endTime - nowLocal.replace(tzinfo=None))
                # print(runTimeEC2Instance)
                instanceRequiredDetails.append(Ec2InstanceDetails(eachInstanceRequiredDetails["InstanceId"],
                                                                  eachInstanceRequiredDetails["Tags"],
                                                                  eachInstanceRequiredDetails["State"]["Name"],
                                                                  str(nowLocal.date()),
                                                                  str(nowLocal.time()),
                                                                  str(runTimeEC2Instance)
                                                                  ))

                for eachClusterName in eachInstanceRequiredDetails["Tags"]:
                    if eachClusterName["Key"] == "Cluster":
                        tempList.append(eachClusterName["Value"])

    listOfClusters = list(dict.fromkeys(tempList))
    # listOfClusters = tempList
    # pprint(listOfClusters)
    tempListOfEachTags = []
    for eachInstanceListData in instanceRequiredDetails:
        listOfTags.append(eachInstanceListData.tags)
        for each in eachInstanceListData.tags:
            tempListOfEachTags.append(each)

    for eachClusterName in listOfClusters:
        # print(eachClusterName)
        nodeCountList.append(tempListOfEachTags.count({'Key': 'Cluster', 'Value': '' + eachClusterName + ''}))
        # print(eachClusterName)

    # print(nodeCountList)
    for eachInstanceListData in instanceRequiredDetails:
        for eachTags in eachInstanceListData.tags:
            for eachClusterName in listOfClusters:
                # print(eachTags["Value"])
                if eachTags["Value"] == eachClusterName:
                    # print(eachTags["Value"])
                    for tagName in eachInstanceListData.tags:
                        # print(tagName)
                        if tagName["Key"] == "Name":
                            # print("HIT")
                            nodeDetails.append(
                                NodeDetails(eachClusterName, tagName["Value"], eachInstanceListData.state,
                                            eachInstanceListData.launchDate,
                                            eachInstanceListData.launchTime,
                                            eachInstanceListData.runtimeEC2instance).dict())
    loopCounter = 0
    for eachCluster in listOfClusters:
        listOfNodeDetails = filter(lambda x: x["Cluster Name"] == eachCluster, nodeDetails)
        publishObject.append(ClusterDetails(eachCluster, nodeCountList[loopCounter], list(listOfNodeDetails)).dict())
        loopCounter += 1

    # pprint(publishObject)

    # publishObject = {"Cluster Name": listOfClusters, "Node Count": str(nodeCountList),
    #                  "Node details": nodeDetails}

    jsonData = json.dumps(publishObject)
    info = json.loads(jsonData)
    pprint(info)
    # sesFunction(info)


def main():
    getEC2Details()


if __name__ == "__main__":
    main()
