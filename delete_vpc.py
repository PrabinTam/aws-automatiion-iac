#!/usr/bin/env python

from get_info import get_resource_info

class delete_lab():
    def __init__(self):
        self.ec2Client = get_resource_info().ec2Client
        self.ec2Resource = get_resource_info().ec2Resource

    def natgateway_delete(self, *args):
        """

        :param args: This will take string as its argument, example delete_nat_gateway("natgateway_name1", "natgateway_nam2" ,...)
        :return:  this will not return anything, it will raise an error if it cannot delete the natgateway.
        """
        if len(args) < 1:
            raise Exception("Please provide atleast one NatGateway Name")
        for natgateway_name in args:
            if type(natgateway_name) != str:
                raise Exception("Please provide atleast one NatGateway Name")
            try:
                natgateway_id = get_resource_info().get_natgateway_id(natgateway_name)[natgateway_name]           # get that natgateway ID from get_resource module
            except KeyError as e:
                print(f"No Nat Gateway with the name [{str(e)}] exists")
            else:
                delete_natgateway = self.ec2Client.delete_nat_gateway(NatGatewayId=natgateway_id)       # delete the natgateway using its id
                natgateway_delete_waiter = self.ec2Client.get_waiter('nat_gateway_deleted')
                # wait unitl it has fully deleted
                natgateway_delete_waiter.wait(NatGatewayIds=[natgateway_id], WaiterConfig={'Delay': 5, 'MaxAttempts': 20})
                print("finished deleting natgateway")

    def elastic_ip_release(self, *args):
        """

        :param args: This will take string as its argument, example delete_elastic_ip("elastic_ip_name1", "elastic_ip_name2" ,...)
        :return: This will not return anything, it will raise an error if it cannot release elastic ip.
        """
        if len(args) < 1:
            raise Exception("Please provide atleast one NatGateway Name")
        for elastic_ip_name in args:
            if type(elastic_ip_name) != str:
                raise Exception("Please provide atleast one NatGateway Name")
            try:
                elastic_ip_id =get_resource_info().get_elastic_ip_id(elastic_ip_name)[elastic_ip_name]
            except KeyError as e:
                print(f"No Elastic Ip with the name [{str(e)}] exists ")
            else:
                delete_elastic_ip =  self.ec2Client.release_address(AllocationId=elastic_ip_id)
                print("finished releasing the elastic ip")

    def subnet_delete(self, *args):
        """
        :param args: This method will take strings as an argument, example subnet_delete(subnet_name1, subnet_name2, ..)
        :return: This method will not return anything, it will raise an error if it cannot delete subnet
        """

        if len(args) < 1:
            raise Exception("Please provide atleast one Subnet Name")
        for subnet_name in args:
            if type(subnet_name) != str:
                raise Exception("Please provide atleast one Subnet Name")
            try:
                subnet_id = get_resource_info().get_subnet_id(subnet_name)[subnet_name]
            except KeyError as e:
                print(f"No Subnet with the name [{str(e)}] exists ")
            else:
                delete_subnet = self.ec2Client.delete_subnet(SubnetId=subnet_id)
                print("finished deleting subnets")


    def route_table_delete(self, *args):
        """
        :param args: This method will take strings as an argument, example route_table_delete(routetablename1, route-table-name2, ..)
           :return: This method will not return anything, it will raise an error if it cannot delete route table
        """
        if len(args) < 1:
            raise Exception("Please provide atleast one Subnet Name")
        for route_table_name in args:
            if type(route_table_name) != str:
                raise Exception("Please provide atleast one Subnet Name")
            try:
                route_table_id = get_resource_info().get_route_table_id(route_table_name)[route_table_name]
            except KeyError as e:
                print(f"No Route Table with the name [{str(e)}] exists ")
            else:
                self.ec2Client.delete_route_table(RouteTableId=route_table_id)
                print("Finished deleting Route tables")

    def internet_gateway_detach_from_vpc(self, vpc_id=None, internet_gateway_id=None):
        """
        :param args: This method must only have two arguments, 1st argument, VpcId and 2nd argument must be InternetGatewayID
         example delete_vpc(vpc_id, internet_gateway_id).
        :return: This method will not return anything, it will raise an error if it cannot deatach the internet gateway from VPC
        """
        if type(internet_gateway_id) != str or type(vpc_id) != str:
            raise Exception("Please only provide string values")
        try:
            self.ec2Client.detach_internet_gateway(VpcId=vpc_id, InternetGatewayId=internet_gateway_id)
        except:
            print("Vpc_id  or internet gateway ID does not exist")
        else:
            print("finished deattaching the IGW from the VPC")

    def internet_gateway_delete(self, *args):
        """
        :param args: This method take list as its argument, and each list can only be length of two:
         example delete_vpc(["", ""], ["", ""] ,...). first index of the list must be Internet Gateway Name and second index must be vpc_name
        :return: This method will not return anything, it will raise an error if it cannot delete the internet gateway.
        """
        if len(args) < 1:
            raise Exception("Please provide atleast one entry ")
        for lists in args:
            if len(lists) != 2:
                raise Exception("Please provide Subnet name and VPC name in the proper formart")
            internet_gateway_name = lists[0]
            vpc_name = lists[1]
            if type(internet_gateway_name) != str or type(vpc_name) != str:
                raise Exception("Please only provide string values")
            try:
                vpc_id = get_resource_info().get_vpc_id(vpc_name)[vpc_name]
                internet_gateway_id = get_resource_info().get_internet_gateway_id(internet_gateway_name)[internet_gateway_name]
                self.internet_gateway_detach_from_vpc(vpc_id, internet_gateway_id)
            except KeyError as e:
                print(f"No Subnet or VPC with the name [{str(e)}] exists ")
            else:
                self.ec2Client.delete_internet_gateway(InternetGatewayId=internet_gateway_id)
                print("Finished deleting Internet Gateway")

    def delete_vpc(self, *args):
        """
        :param args: This method take string as its argument, example delete_vpc("test1", "test1" ,...)
        :return: This method will not return anything, it will raise an error if it cannot delete the VPC
        """
        if len(args) < 1:
            raise Exception("Please provide atleast one NatGateway Name")
        for vpc_name in args:
            if type(vpc_name) != str:
                raise Exception("Please provide atleast one NatGateway Name")
            try:
                vpc_id = get_resource_info().get_vpc_id(vpc_name)[vpc_name]
            except KeyError as e:
                print(f"No VPC with the name [{str(e)}] exists ")
            else:
                delete_vpc = self.ec2Client.delete_vpc(VpcId=vpc_id)
                print("Finished deleting VPC")

if __name__ == '__main__':
    delete_all = delete_lab()
    delete_all.natgateway_delete("Private_Nat")
    delete_all.elastic_ip_release("Private_Nat_elastic_IP")
    delete_all.subnet_delete("Private-1a", "Private-1b", "Public-1a", "Public-1b")
    delete_all.route_table_delete("Private_RT")
    delete_all.internet_gateway_delete(["My_Igw","MY_VPC"])
    delete_all.delete_vpc("MY_VPC")

