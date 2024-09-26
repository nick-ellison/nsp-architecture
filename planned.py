from diagrams import Diagram, Cluster, Edge
from diagrams.aws.compute import EC2, AutoScaling
from diagrams.aws.network import ALB, InternetGateway, RouteTable, VPC
from diagrams.aws.database import RDS
from diagrams.aws.storage import EFS
from diagrams.aws.management import Cloudwatch
from diagrams.aws.security import WAF
from diagrams.onprem.vcs import Github
from diagrams.onprem.analytics import PowerBI
from diagrams.aws.general import Client
from diagrams.aws.devtools import Codebuild, Codecommit, Codedeploy
from diagrams.aws.database import ElasticacheForRedis
from diagrams.onprem.client import Client
from diagrams.custom import Custom  # Import Custom class
from diagrams.onprem.network import Internet

# Create a new diagram with left-to-right flow and increased spacing
graph_attrs = {
    "splines": "ortho",
    "nodesep": "1.5",
    "ranksep": "1.5",
}

with Diagram("NSP Architecture", show=True, direction="LR", graph_attr=graph_attrs):
    
    # Internet Gateway and Route Table at the bottom
    igw = InternetGateway("Internet Gateway")
    route_table = RouteTable("Route Table")
    
    # API Connections from Third-Party Microsites to WAF (LHS)
    third_party_microsites = Internet("Third Party Microsites")
    
    # Web Access (LHS)
    client = Client("User Traffic")

    # VPC
    with Cluster("VPC"):

        # Shared Storage (EFS)
        efs = EFS("EFS - Shared Storage")
        
        # Load Balancer and WAF inside VPC
        alb = ALB("ALB")
        waf = WAF("WAF")
        
        # Web and API traffic from the LHS to WAF
        third_party_microsites >> Edge(label="API Traffic") >> waf
        client >> Edge(label="HTTPS") >> waf
        waf >> alb

        # Auto Scaling Group Cluster
        with Cluster("Auto Scaling Group"):
            ec2_instances = [EC2("EC2 Instance 1"),
                             EC2("EC2 Instance 2")]
            alb >> ec2_instances
            ec2_instances[0] >> efs
            ec2_instances[1] >> efs
        
        # RDS Cluster
        with Cluster("RDS Cluster"):
            main_rds = RDS("Main Database (R/W)")
            read_replica_rds = RDS("Read Replica (R/O)")
            ec2_instances[0] >> Edge(label="DB Access") >> main_rds
            ec2_instances[1] >> main_rds
        
        # Monitoring and Logging
        cloudwatch = Cloudwatch("CloudWatch")
        ec2_instances[0] >> cloudwatch
        ec2_instances[1] >> cloudwatch

        # ElastiCache Integration for Queue Management
        elasticache = ElasticacheForRedis("ElastiCache for Redis")
        ec2_instances[0] >> elasticache

        # Reporting Environment
        reporting_app = EC2("Reporting Environment")
        reporting_app >> read_replica_rds

        # Internet Gateway and Route Table Connections at the bottom
        ec2_instances >> route_table >> igw

    # External connections to SendGrid and Dotdigital via Internet Gateway and Route Table (bottom)
    sendgrid_api = Custom("SendGrid API", "./sendgrid_logo.png")  # Custom node for SendGrid
    dotdigital_api = Custom("Dotdigital API", "./dotdigital_logo.png")  # Custom node for Dotdigital
    
    route_table >> Edge(label="Send Email") >> igw >> sendgrid_api
    route_table >> Edge(label="Marketing Automation") >> igw >> dotdigital_api

    # External connections
    power_bi = PowerBI("PowerBI Dashboard")
    read_replica_rds >> Edge(label="Remote Data Connection") >> power_bi
