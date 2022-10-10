#!/usr/bin/env python

import boto3
import botocore
import time

class vpc():
    def __init__(self):
        self.ec2resource = boto3.resource('ec2')
        self.ec2Client = boto3.client('ec2')
        self.vpc = self.create_vpc()

    def create_vpc(self):
        vpc =  self.ec2resource.create_vpc(CidrBlock='10.0.0.0/16', InstanceTenancy='default',
                                           TagSpecifications=[{'ResourceType': 'vpc', 'Tags': [{'Key': 'Name', 'Value': 'MY_VPC'}]}])
#        vpc.create_tags(Tags=[{'Key': 'Name', 'Value': 'my_vpc'}])
        vpc_waiter = self.ec2Client.get_waiter('vpc_available')
        vpc_waiter.wait(VpcIds=[vpc.id])
        self.ec2Client.modify_vpc_attribute(EnableDnsSupport={'Value': True}, VpcId=vpc.id)
        self.ec2Client.modify_vpc_attribute(EnableDnsHostnames={'Value': True}, VpcId=vpc.id)
        print("Finished createing VPC")
        return vpc

    def create_lab(self):
        # this method will call the other methods to complete the build of the VPC and other resources.
        if self.vpc.id:
            My_Igw_Id = self.create_igw()
            Main_RT_Id = self.delete_existing_table(My_Igw_Id)
            Private_RT_Id = self.create_private_route_table()
            Public_1a_Subnet_id = self.create_subnets(Main_RT_Id, Private_RT_Id)
            self.Create_nat_gateway(Public_1a_Subnet_id, Private_RT_Id)

    def create_igw(self):
        # create internet gateway and attach to the VPC that was created
        # return gateway ID
        My_Igw = self.ec2resource.create_internet_gateway(TagSpecifications=[{'ResourceType': 'internet-gateway', 'Tags': [{'Key': 'Name', 'Value': 'My_Igw'}]}])
        time.sleep(2)
        Igw_waiter = self.ec2Client.get_waiter('internet_gateway_exists')
        Igw_waiter.wait(InternetGatewayIds=[My_Igw.id])

        My_Igw.attach_to_vpc(VpcId=self.vpc.id)
        print("Finished creating Internet gateway and attaching to the VPC")
        return My_Igw.id

    def get_all_route_tables(self):
        all_route_tables = self.ec2Client.describe_route_tables()
        return all_route_tables

    def delete_existing_table(self, My_Igw_Id):
        # delete any table that exists except the main table and rename the main table "Main_RT"
        # return main route table ID
        Main_RT_Id = ""
        all_route_tables = self.get_all_route_tables()
        for route_table in all_route_tables['RouteTables']:
            if len(route_table['Associations'])> 0:
                if (route_table['Associations'][0]['Main']):
                    Main_RT_Id = route_table['RouteTableId']
                    self.ec2Client.create_tags(Resources=[Main_RT_Id], Tags=[{'Key': 'Name', 'Value': 'Main_RT'}])
                    self.ec2Client.create_route(DestinationCidrBlock='0.0.0.0/0', GatewayId=My_Igw_Id, RouteTableId=Main_RT_Id)
            else:
                self.ec2Client.delete_route_table(RouteTableId=route_table['RouteTableId'])
        print("Finished deleting all RT beside the main one and renmaed it to Main_RT, also routed its route to everywhere")
        return Main_RT_Id

    def create_private_route_table(self):
        # create a route table for private subnet and return its ID
        # cannot create the route yet because I need NAT gateway for this as this is how that is designed.
        Private_RT = self.ec2Client.create_route_table(VpcId=self.vpc.id)
        time.sleep(2)
        Private_RT_Id = Private_RT['RouteTable']['RouteTableId']
        self.ec2Client.create_tags(Resources=[Private_RT_Id], Tags=[{'Key': 'Name', 'Value': 'Private_RT'}])
        print("Finished creating Private route table")
        return Private_RT_Id

    def create_subnets(self, Main_RT_Id, Private_RT_Id):
    # createV subnets
        subnet_creation_list = [{
            'Public-1a':{'CidrBlock': '10.0.1.0/24', 'VpcId':self.vpc.id, 'AvailabilityZone': 'us-east-1a'},
            'Public-1b':{'CidrBlock': '10.0.2.0/24', 'VpcId':self.vpc.id, 'AvailabilityZone': 'us-east-1b'},
            'Private-1a':{'CidrBlock': '10.0.3.0/24', 'VpcId':self.vpc.id, 'AvailabilityZone': 'us-east-1a'},
            'Private-1b':{'CidrBlock': '10.0.4.0/24', 'VpcId':self.vpc.id, 'AvailabilityZone': 'us-east-1b'},
                                }]
        # loop throguh the above list and create 4 subnets
        for subnets in subnet_creation_list:
            Public_1a_Subnet_id = ""
            for subnet,values in subnets.items():
                try:
                    subnet_create = self.ec2resource.create_subnet(CidrBlock=subnets[subnet]['CidrBlock'], AvailabilityZone=subnets[subnet]['AvailabilityZone'], VpcId=subnets[subnet]['VpcId'])
                    subnet_waiter = self.ec2Client.get_waiter('subnet_available')
                    subnet_waiter.wait(SubnetIds=[subnet_create.id])
                    # set the name of the subnet
                    subnet_create.create_tags(Tags=[{'Key': 'Name', 'Value': subnet}])
                except botocore.exceptions.ClientError as e:
                    print(e.response['Error']['Message'])
                else:
                    # assign puplic ipv4 ip address tp the instance in the public subnet and associate public with main route table
                    if "Public" in subnet:
                        self.ec2Client.modify_subnet_attribute(MapPublicIpOnLaunch={'Value': True}, SubnetId=subnet_create.id)
                        self.ec2Client.associate_route_table(RouteTableId=Main_RT_Id, SubnetId=subnet_create.id)
                    # associate the private route table with private subnets
                    if "Private" in subnet:
                        self.ec2Client.associate_route_table(RouteTableId=Private_RT_Id, SubnetId=subnet_create.id)
                    if "Public-1a" in subnet:
                        Public_1a_Subnet_id = subnet_create.id
            # reutn public subnet 1-a ID becuase this is where NAT Gateway will live
            print("Finished creating subnets and attaching to the proper route table")
            return Public_1a_Subnet_id

    def Create_nat_gateway(self, Public_1a_Subnet_id, Private_RT_Id):
        # get elastic IP
        Elastic_Ip = self.ec2Client.allocate_address(TagSpecifications=[{'ResourceType': 'elastic-ip', 'Tags': [{'Key':'Name', 'Value': 'Private_Nat_elastic_IP'}]}])
        # create nat gateway
        Nat_Gateway = self.ec2Client.create_nat_gateway(AllocationId=Elastic_Ip['AllocationId'], SubnetId=Public_1a_Subnet_id, ConnectivityType='public',
                                                        TagSpecifications=[{'ResourceType': 'natgateway', 'Tags': [{'Key': 'Name', 'Value': 'Private_Nat'}]}])
        nat_waiter = self.ec2Client.get_waiter('nat_gateway_available')
        try:
            nat_waiter.wait(NatGatewayIds=[Nat_Gateway['NatGateway']['NatGatewayId']], WaiterConfig={'Delay': 5, 'MaxAttempts': 20})
        except botocore.exceptions.WaiterError as e:
            print(e)
        # route private route table to the Nat Gateway
        self.ec2Client.create_route(DestinationCidrBlock='0.0.0.0/0', NatGatewayId=Nat_Gateway['NatGateway']['NatGatewayId'], RouteTableId=Private_RT_Id)
        print("Finished creating nat gateways")



if __name__ == '__main__':
    create_vpc = vpc()
    create_vpc.create_lab()