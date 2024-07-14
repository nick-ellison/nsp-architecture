from diagrams import Diagram, Cluster, Edge
from diagrams.aws.compute import EC2
from diagrams.aws.database import RDS
from diagrams.onprem.client import User
from diagrams.onprem.network import Internet

# Create a new diagram
with Diagram("National Schools Partnership AWS Architecture", show=True):
    
    # Define the EC2 instance
    ec2_instance = EC2("EC2 Instance")

    # Define the RDS instances (main and read-only mirror)
    with Cluster("RDS Cluster"):
        main_rds = RDS("Main Database (Read/Write)")
        read_only_rds = RDS("Read-Only Mirror")
    
    # Define application versions
    with Cluster("Applications"):
        production_app = EC2("Production Environment")
        reporting_app = EC2("Reporting Environment")
    
    # Connect EC2 instance to application versions
    ec2_instance >> production_app
    ec2_instance >> reporting_app

    # Connect the production version to the main RDS database
    production_app >> main_rds
    
    # Connect the reporting version to the read-only RDS mirror
    reporting_app >> read_only_rds

    # Define external connections
    with Cluster("External Connectivity"):
        nsp_website = User("NSP Website")
        third_party = Internet("Third Party Microsites")
    
    # Connect production environment to external services
    production_app >> Edge(label="API") >> nsp_website
    production_app >> Edge(label="API") >> third_party
