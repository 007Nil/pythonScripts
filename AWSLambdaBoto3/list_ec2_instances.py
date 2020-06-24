import boto3

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


# Declare variables for search instances
node_name = "c01-1"
cluster_name = "c02"
count_node = 0
count_cluster = 0
terminated = "terminated"
# tag_key_cluster_values = []
# tag_key_node_values = []
instance_requried_details = []
list_of_tags = []

ec2_client = boto3.client(service_name="ec2", region_name="ap-south-1")
ec2_instance_details = ec2_client.describe_instances()
# print(ec2_instance_details)
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
    print("Cluster " + cluster_name + " contains " + str(count_node) + " nodes")
    print("Node status Details -----")

    for each_instance_list_data in instance_requried_details:
        for each_instance_list_data_in_tags in each_instance_list_data.tags:
            # print(each_instance_list_data_in_tags["Value"])
            if each_instance_list_data_in_tags["Value"] == cluster_name:
                # print(each_instance_list_data.tags)
                for tag_name in each_instance_list_data.tags:
                    if tag_name["Key"] == "Name":
                        print("Node Name: "+tag_name["Value"]+" State:" +each_instance_list_data.state)
                # print(each_instance_list_data.state)
else:
    print("Cluster " + cluster_name + " contains 0 nodes, Since it does not exist")
