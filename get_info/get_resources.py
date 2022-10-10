#!/usr/bin/env python

import boto3
import botocore

class get_resource_info():
    def __init__(self):
        self.ec2Resource = boto3.resource('ec2')
        self.ec2Client = boto3.client('ec2')

    def get_natgateway_id(self, *args):
        """
        :param kwargs: you must pass argument in this formart var=value"
        :return: it will return Nat Gateway ID of the gateway name, and if nothing was specified it will return an empty string
        """
        get_natgateway_id=""
        natgateway_id_dict = {}
        if len(args) < 1:
            raise Exception("Please provide atleast one NatGateway Name")
        for natgateway_name in args:
            if type(natgateway_name) != str:
                raise TypeError(f"Only Strings are allowed. {natgateway_name} is not a string")
            describe_natgateway_id = self.ec2Client.describe_nat_gateways(
                Filters=[{'Name': 'tag:Name', 'Values': [natgateway_name]}])
            if describe_natgateway_id['ResponseMetadata']['HTTPStatusCode'] == 200 and len(describe_natgateway_id['NatGateways']) > 0:
                for attributes in describe_natgateway_id['NatGateways']:
                    for keys in attributes:
                        if attributes['State'] != "deleted":
                            if keys == "NatGatewayId":
                                ID = attributes[keys]
                                natgateway_id_dict[natgateway_name] = ID
        return natgateway_id_dict

    def get_elastic_ip_id(self, *args):
        elastic_ip_id_dict = {}
        if len(args) < 1:
            raise Exception("Please provide atleast one Elastic IP Name")
        for elastic_ip_name in args:
            if type(elastic_ip_name) != str:
                raise TypeError(f"only Strings are allowed. {elastic_ip_name} is not a string")
            describe_elastic_ip = self.ec2Client.describe_addresses(
                Filters=[{'Name': 'tag:Name', 'Values': [elastic_ip_name]}])
            if describe_elastic_ip['ResponseMetadata']['HTTPStatusCode'] == 200 and len(describe_elastic_ip['Addresses']) > 0:
                for attributes in describe_elastic_ip['Addresses']:
                    for keys in attributes:
                        if keys == "AllocationId":
                            ID = attributes[keys]
                            elastic_ip_id_dict[elastic_ip_name] = ID
        return elastic_ip_id_dict

    def get_vpc_id(self, *args):
        """
        :param kwargs: You must pass in your VPC name
        :return: It will return you with the VpcId
        """
        vpc_id_dict = {}
        if len(args) < 1:
            raise Exception("Please provide atleast one NatGateway Name")
        for vpc_name in args:
            if type(vpc_name) != str:
                raise TypeError(f"Only Strings are allowed. {vpc_name} is not a string")
            describe_vpc_id = self.ec2Client.describe_vpcs(Filters=[{'Name': 'tag:Name', 'Values': [vpc_name]}])
            if describe_vpc_id['ResponseMetadata']['HTTPStatusCode'] == 200 and len(describe_vpc_id['Vpcs']) > 0:
                for attributes in describe_vpc_id['Vpcs']:
                    for keys in attributes:
                        if keys == "VpcId":
                            ID = attributes[keys]
                            vpc_id_dict[vpc_name] = ID
        return vpc_id_dict

    def get_subnet_id(self, *args):
        """
        :param args: This module will take string as your argument. Argumnet has to be the subnet name
        :return: it will return  you with a dictionay {subnet_name: subnet_id}
        """
        subnet_id_dict = {}
        if len(args) < 1:
            raise Exception("Please provide atleast one Subnet Name")
        for subnet_name in args:
            if type(subnet_name) != str:
                raise TypeError(f"Only Strings are allowed. {subnet_name} is not a string")
            subnet_id = self.ec2Client.describe_subnets(Filters=[{'Name': 'tag:Name', 'Values': [subnet_name]}])
            if subnet_id['ResponseMetadata']['HTTPStatusCode'] == 200 and len(subnet_id['Subnets']) > 0:
                for attributes in subnet_id['Subnets']:
                    for keys in attributes:
                        if keys == "SubnetId":
                            ID = attributes[keys]
                            subnet_id_dict[subnet_name] = ID
        return subnet_id_dict

    def get_route_table_id(self, *args):
        """
        :param args: This module will take string as your argument. Argumnet has to be the route_table_name name
        :return: it will return  you with a dictionay {route_table1: route_table1_id, route_table2: route-table2_id, ...}
        :example: get_route_table_id("route_table_name1", "route_table_name2", ...)
        """
        route_table_id_dict = {}
        if len(args) < 1:
            raise Exception("Please provide atleast one subnet Name")
        for route_table_name in args:
            if type(route_table_name) != str:
                raise TypeError(f"Only Strings are allowed. {route_table_name} is not a string")
            route_table_id = self.ec2Client.describe_route_tables(
                Filters=[{'Name': 'tag:Name', 'Values': [route_table_name]}])
            if route_table_id['ResponseMetadata']['HTTPStatusCode'] == 200 and len(route_table_id['RouteTables']) > 0:
                for attributes in route_table_id['RouteTables']:
                    for keys in attributes:
                        if keys == "RouteTableId":
                            ID = attributes[keys]
                            route_table_id_dict[route_table_name] = ID
        return route_table_id_dict

    def get_internet_gateway_id(self, *args):
        """

        :param args: This module will take string as your argument. Argument has to be the internet_gateway's name
        :return: it will return  you with a dictionay {internet_gw1: internet_gw1_id, internet_gw2: internet_gw2_id, ...}
        :example: get_route_table_id("internet_gateway_name1", "internet_gateway_name2", ...)
        """
        internet_gateway_id_dict = {}
        if len(args) < 1:
            raise Exception("Please provide atleast one subnet Name")
        for internet_gateway_name in args:
            if type(internet_gateway_name) != str:
                raise TypeError(f"Only Strings are allowed. {internet_gateway_name} is not a string")
            internet_gateway_id = self.ec2Client.describe_internet_gateways(
                Filters=[{'Name': 'tag:Name', 'Values': [internet_gateway_name]}])
            if internet_gateway_id['ResponseMetadata']['HTTPStatusCode'] == 200 and len(
                    internet_gateway_id['InternetGateways']) > 0:
                for attributes in internet_gateway_id['InternetGateways']:
                    for keys in attributes:
                        if keys == "InternetGatewayId":
                            ID = attributes[keys]
                            internet_gateway_id_dict[internet_gateway_name] = ID
        return internet_gateway_id_dict

#if __name__ == '__main__':
#    s = get_resource_info()
#    print(s.ec2Client)
