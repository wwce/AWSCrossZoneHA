import logging
import boto3
import urllib3
from botocore.exceptions import ClientError

event = {}
context = {}

ec2 = boto3.resource('ec2')
ec2_client = boto3.client('ec2')
logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event, context):
    eniinfo = ec2.NetworkInterface(event['trustgood']).private_ip_address
    #print(eniinfo)
    logger.info("eniinfo var {}".format(eniinfo))                    
    http = urllib3.PoolManager()
    logger.info("http var {}".format(http)) 
    #print(http)
    urlvar = 'http://' + eniinfo
    try:
        r = http.request('GET', urlvar, headers={'Host': 'checkip.amazonaws.com'}, timeout=5.0, retries=1)
    except:
        logger.info("*****path check failed*****")
        return
    #print(r)
    #print(r.status)
    #print(r.headers)
    if (r.status == 200):
        logger.info("*****Path 200OK*****")
    elif (r.status == 302):
        logger.info("*****Site Redirected*****")
    else:
        logger.info("*****Site NOT 200OK*****")
        return
        
    route_table = ec2_client.describe_route_tables(
            Filters=[
            {
                'Name': 'vpc-id',
                'Values': [
                    event['vpcid']
                ]          
            },
        ]
    )
    if route_table.get('RouteTables'):
        for i in range(len(route_table['RouteTables'])):
            routes = route_table['RouteTables'][i]['Routes']
            for route in routes:
                    key = 'NetworkInterfaceId'
                    if key in route:
                        if route['NetworkInterfaceId'] == event['untrustdead']:
                            response = ec2_client.replace_route(
                                RouteTableId=(route_table['RouteTables'][i]['RouteTableId']),
                                DryRun=False,
                                NetworkInterfaceId=event['untrustgood'],
                                DestinationCidrBlock=(route['DestinationCidrBlock'])
                            )
                            logger.info("Success! Changing {} route next hop to {} in route table {} .... response {}".format(route['DestinationCidrBlock'], event['untrustgood'],route_table['RouteTables'][i]['RouteTableId'],response))
                        elif route['NetworkInterfaceId'] == event['trustdead']:

                            response = ec2_client.replace_route(
                                RouteTableId=(route_table['RouteTables'][i]['RouteTableId']),
                                DryRun=False,
                                NetworkInterfaceId=event['trustgood'],
                                DestinationCidrBlock=(route['DestinationCidrBlock'])
                            )
                            logger.info("Success! Changing {} route next hop to {} in route table {} .... response {}".format(route['DestinationCidrBlock'], event['trustgood'],route_table['RouteTables'][i]['RouteTableId'],response))                    
    else:
        logger.info('No routes to process')