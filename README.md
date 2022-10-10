# aws-automatiion-iac
i started this project to help me understand the Iac in the AWS cloud. 

I currently have three files files. 
1. vpc.py -- This will create VPC, subnets, routetable, Internet gateway, NAT, elastic IP.
2. get_info/get_resources.py -- This will essentially take the name of the resouce and return that resource's ID. 
3. delete_vpc.py -- this will import the get_resources.py and get the ID for resources such as Internet Gateway, vpc subnets and so on and use that ID to delete the resource. 
