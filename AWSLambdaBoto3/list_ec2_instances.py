import boto3
import json

# using resource
'''
ec2_resource = boto3.resource(service_name="ec2",region_name="ap-south-1")

for each_instance in ec2_resource.instances.all():
    print(each_instance.id, each_instance.state['Name'])
'''


class Ec2InstanceDetails:
    def __init__(self, instance_id=None, tags=None, state=None):
        self.state = state
        self.tags = tags
        self.instance_id = instance_id


class NodeDetails:
    def __init__(self, nodename=None, node_state=None):
        self.nodename = nodename
        self.node_state = node_state

    def dic(self):
        dic = {"Node Name":  self.nodename, "Node State":  self.node_state}
        return dic


def convert_to_dict(list):
    res_dct = {list[i]: list[i + 1] for i in range(0, len(list), 2)}
    return res_dct


def sns_function():
    topic_arn = "arn:aws:sns:ap-south-1:254018427142:EC2TestTopic"
    sns_clinet = boto3.client(
        'sns',
        region_name="ap-south-1"
    )

    publicObject = {}


# Declare variables for search instances
node_name = "c01-1"
cluster_name = "c01"
count_node = 0
count_cluster = 0
terminated = "terminated"
instance_requried_details = []
list_of_tags = []
node_details = []

# EC2 INSTANCE CLIENT
ec2_client = boto3.client(service_name="ec2", region_name="ap-south-1")
ec2_instance_details = ec2_client.describe_instances()

# SNS CLIENT

for each_instance in ec2_instance_details['Reservations']:
    # print(each_instance)
    for each_instance_requried_details in each_instance['Instances']:
        # print(each_instance_requried_details)
        instance_requried_details.append(Ec2InstanceDetails(each_instance_requried_details["InstanceId"],
                                                            each_instance_requried_details["Tags"],
                                                            each_instance_requried_details["State"]["Name"]))
        '''
        instance_tags = each_instance_requried_details["Tags"]
        # print(instance_tags)
        for each_instance_tags in instance_tags:
            # print(each_instance_tags)
            if each_instance_tags["Key"] == "Cluster":
                if each_instance_tags["Value"] not in tag_key_cluster_values:
                    tag_key_cluster_values.append(each_instance_tags["Value"])
                # print(tag_key_cluster_values)
            else:
                tag_key_node_values.append(each_instance_tags["Value"])

print(tag_key_cluster_values)
print(tag_key_node_values)

count_cluster = sum(p == cluster_name for p in tag_key_cluster_values)
# print(count_cluster)
'''
# print(instance_requried_details[0].tags[0]["Key"])
# print(instance_requried_details[0].state,'Cluster Name='+instance_requried_details[0].tags[0]["Value"]
#       ,'Node Name='+instance_requried_details[0].tags[1]["Value"])

for each_instance_list_data in instance_requried_details:
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

    for each_instance_list_data in instance_requried_details:
        for each_instance_list_data_in_tags in each_instance_list_data.tags:
            # print(each_instance_list_data_in_tags["Value"])
            if each_instance_list_data_in_tags["Value"] == cluster_name:

                for tag_name in each_instance_list_data.tags:
                    if tag_name["Key"] == "Name":
                        node_details.append(NodeDetails(tag_name["Value"], each_instance_list_data.state).dic())

    publish_object = {"Cluster Name": cluster_name, "Node Count": str(count_node),
                      "Node details": node_details}

    print(json.dumps(publish_object))

else:
    print("Cluster " + cluster_name + " contains 0 nodes, Since it does not exist")
    publish_object = {"Cluster Name": cluster_name, "Node Count": str(count_node), "Node details": node_details}
    print(json.dumps(publish_object))
