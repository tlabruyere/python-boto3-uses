import boto3
import json


def load_env(var_file):
    with open(var_file, 'r') as f:
        env = json.load(f)
    return env


def sort_images_by_creation_date(images):
    newlist = sorted(images['Images'], key=lambda k: k['CreationDate'],reverse=True) 
    print(newlist[0])


class AWS_Interaction(object):
    '''
    Handles interactions for AWS
    '''
    # Vars
    cl = None
    ev = None
    region = None
    regions = None

    # functions
    def __init__(self, keyfile):
        '''
        Constructor: takes a path to a json key file of format:
        {
          "aws_access_key":"XXXXXXXXXXXXX",
          "aws_secret_key":"XXXXXXXXXXXXX",
          "region":"XXXXXXXXXXXXX"
        }
        '''
        self.ev = load_env(keyfile)
        self.region = self.ev['region'] 
        self.client(self.region)

    def client(self):
        '''
        getter for client
        '''
        return self.cl

    def client(self, region_name='us-west-1'):
        '''
        setter for the client. Defaults to the region us-west-1. If the region_name is different 
        the the current, it will set it to the new region

        '''
        if self.cl is None or self.cl.meta.region_name is not region_name:
            print(region_name)
            self.cl = boto3.client('ec2',
                    region_name=region_name, 
                    aws_access_key_id=self.ev['aws_access_key'], 
                    aws_secret_access_key=self.ev['aws_secret_key'])
        return self.cl 

    def get_cur_connect_region(self):
        '''
        return the current region
        '''
        return self.client().meta.region_name

    def get_regions(self, force_update=False):
        '''
        returns a list of all potential regions
        '''
        if self.regions is None or force_update:
            self.regions = self.client().describe_regions()
        return [x['RegionName'] for x in self.regions['Regions'] if 'RegionName' in x]

    def my_describe_images(self, kwargs):
        '''
        describe images call boto3 cimages
        '''
        print('printing some stuff',kwargs)
#        images = self.client().describe_images(**kwargs)
#        images = self.client().describe_images(Filters=kwargs,DryRun=True)
        images = self.client().describe_images(Filters=kwargs)
        return images
    
    def find_image(self, name):
        '''
        Find images by name
        Ex:
        aws.find_image('ubuntu/images/hvm-instance/ubuntu-bionic-18.04*')
        '''
        #d = {'Filters': list({'Name':'name', 'Values': list(name)})}
#        filters = [{'Name':'tag:Name', 'Values':['webapp01']}]
        print(name)
        d = [{'Name':'name', 'Values': [name]}]
        return self.my_describe_images(d)

    def get_amis_by_owner(self, owner_id, key=None):
        images = self.describe_images(Owners=owner_id)
        if key is None:
            return images['Images']
        if 0 < len(images['Images'][0]) and key not in images['Images'][0].keys():
            raise KeyError(key + ' was not returned in describe_images') 	
        return  [x['ImageId'] for x in images['Images']]

    def deregister_ami(self, li_o_ami_id):
        for ami in li_o_ami_id:
            self.client().deregister_image(ImageId=ami)
