import boto3
import json


def load_env(var_file):
    with open(var_file, 'r') as f:
        env = json.load(f)
    return env

class AWS_Interaction(object):
    # Vars
    cl = None
    ev = None
    region = None
    regions = None

    # functions
    def __init__(self, keyfile):
        self.ev = load_env(keyfile)
        self.region = self.ev['region'] 
        self.client(self.region)

    def client(self):
        return self.cl

    def client(self, region_name='us-west-1'):
        if self.cl is None or self.cl.meta.region_name is not region_name:
            print(region_name)
            self.cl = boto3.client('ec2',
                    region_name=region_name, 
                    aws_access_key_id=self.ev['aws_access_key'], 
                    aws_secret_access_key=self.ev['aws_secret_key'])
        return self.cl 

    def get_cur_connect_region(self):
        return self.client().meta.region_name

    def get_regions(self, force_update=False):
        if self.regions is None or force_update:
            self.regions = self.client().describe_regions()
        return [x['RegionName'] for x in self.regions['Regions'] if 'RegionName' in x]

    def get_amis(self,owner_id, key=None):
#        images = self.client().describe_images(Owners=owner_id)
        images =  {'Images': [{'Architecture': 'x86_64',
                'CreationDate': '2018-07-24T03:39:09.000Z',
                'ImageId': 'ami-01628f22f4c4941c1',
                'ImageLocation': '823307771695/packer-example 1532403465',
                'ImageType': 'machine',
                'Public': False,
                'OwnerId': '823307771695',
                'State': 'available',
                'BlockDeviceMappings': [{'DeviceName': '/dev/sda1',
                'Ebs': {'Encrypted': False,
                'DeleteOnTermination': True,
                'SnapshotId': 'snap-011584176c08aad96',
                'VolumeSize': 8,
                'VolumeType': 'gp2'}},
                {'DeviceName': '/dev/sdb', 'VirtualName': 'ephemeral0'},
                {'DeviceName': '/dev/sdc', 'VirtualName': 'ephemeral1'}],
                'EnaSupport': True,
                'Hypervisor': 'xen',
                'Name': 'packer-example 1532403465',
                'RootDeviceName': '/dev/sda1',
                'RootDeviceType': 'ebs',
                'SriovNetSupport': 'simple',
                'VirtualizationType': 'hvm'}],
                'ResponseMetadata': {'RequestId': '3eadc2d9-2d3c-4661-830e-b7cb2f82be56',
                'HTTPStatusCode': 200,
                'HTTPHeaders': {'content-type': 'text/xml;charset=UTF-8',
                'content-length': '1888',
                'date': 'Tue, 24 Jul 2018 03:41:01 GMT',
                'server': 'AmazonEC2'},
                'RetryAttempts': 0}}
        if key is None:
            return images['Images']
        if 0 < len(images['Images'][0]) and key not in images['Images'][0].keys():
            raise KeyError(key + ' was not returned in describe_images') 	
        return  [x['ImageId'] for x in images['Images']]

    def deregister_ami(self, li_o_ami_id):
        for ami in li_o_ami_id:
            self.client().deregister_image(ImageId=ami)

print('this')

#    connection = boto3.ec2.connect_to_region('eu-west-1', 
#            aws_access_key_id=env['aws_access_key'], \
#            aws_secret_access_key=env['aws_secret_key'])
#            proxy=yourProxy, \
#            proxy_port=yourProxyPort)
#    return connection.get_all_images()
