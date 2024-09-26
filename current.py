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

with Diagram("NSP Current Architecture", show=True, direction="LR", graph_attr=graph_attrs):
    
    # API Connections from Third-Party Microsites to WAF (LHS)
    third_party_microsites = Internet("Third Party Microsites")
    
    # Web Access (LHS)
    client = Client("User Traffic")
    
    ec2_instance = EC2("EC2 Instance")
    third_party_microsites >> Edge(label="API Traffic") >> ec2_instance
    client >> Edge(label="HTTPS") >> ec2_instance
    
    # RDS Cluster
    with Cluster("RDS Cluster"):
        main_rds = RDS("Main Database (R/W)")
        read_replica_rds = RDS("Read Replica (R/O)")

    ec2_instance >> Edge(label="DB Access") >> main_rds
    
    # Reporting Environment
    reporting_app = EC2("Reporting Environment")
    reporting_app >> read_replica_rds

    # External connections to SendGrid and Dotdigital via Internet Gateway and Route Table (bottom)
    sendgrid_api = Custom("SendGrid API", "./sendgrid_logo.png")  # Custom node for SendGrid
    dotdigital_api = Custom("Dotdigital API", "./dotdigital_logo.png")  # Custom node for Dotdigital
    
    ec2_instance >> Edge(label="Send Email") >> sendgrid_api
    ec2_instance >> Edge(label="Marketing Automation") >> dotdigital_api

    # External connections
    power_bi = PowerBI("PowerBI Dashboard")
    read_replica_rds >> Edge(label="Remote Data Connection") >> power_bi
