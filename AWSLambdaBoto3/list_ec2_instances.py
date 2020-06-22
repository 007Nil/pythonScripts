import boto3

# using resource
'''
ec2_resource = boto3.resource(service_name="ec2",region_name="ap-south-1")

for each_instance in ec2_resource.instances.all():
    print(each_instance.id, each_instance.state['Name'])
'''
# Declare variables for search instances

instance_name = "test"
count = 0
terminated = "terminated"

ec2_client = boto3.client(service_name="ec2", region_name="ap-south-1")
ec2_instance_details = ec2_client.describe_instances()
# print(ec2_instance_details)
for each_instance in ec2_instance_details['Reservations']:
    # print(each_instance)
    for each_instance_requried_details in each_instance['Instances']:
        print(each_instance_requried_details)
        if instance_name == each_instance_requried_details["KeyName"] and each_instance_requried_details["State"]["Name"] != terminated:
            count += 1

print(count)
