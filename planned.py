from diagrams import Diagram, Cluster, Edge
from diagrams.aws.compute import EC2, AutoScaling
from diagrams.aws.network import ELB
from diagrams.aws.security import WAF
from diagrams.aws.database import RDS
from diagrams.aws.storage import EFS
from diagrams.aws.management import Cloudwatch
from diagrams.onprem.network import Internet
from diagrams.onprem.vcs import Github
from diagrams.onprem.analytics import PowerBI

# Create a new diagram with left-to-right flow and increased spacing
graph_attrs = {
    "splines": "ortho",
    "nodesep": "1.5",
    "ranksep": "1.5",
}

with Diagram("Resilient National Schools Partnership AWS Architecture", show=True, direction="LR", graph_attr=graph_attrs):
    
    # Shared Storage (EFS)
    efs = EFS("Shared Storage")
    
    # Deployment Cluster
    with Cluster("Deployment"):
        github = Github("GitHub")
        deployment_ec2 = EC2("Deployment EC2 Instance")
        github >> Edge(label="Deploy Code") >> deployment_ec2
        deployment_ec2 >> efs
    
    # Load Balancer Cluster
    with Cluster("Load Balancer"):
        data_site = Internet("data.nationalschoolspartnership.com")
        waf = WAF("Web Application Firewall")
        elb = ELB("ELB")
        data_site >> Edge(label="HTTPS") >> waf >> elb
    
    # Auto Scaling Group Cluster
    with Cluster("Auto Scaling Group"):
        ec2_instances = [EC2("EC2 Instance 1"),
                         EC2("EC2 Instance 2")]
        elb >> ec2_instances
        ec2_instances[0] >> efs
        ec2_instances[1] >> efs
    
    # Reporting Environment
    reporting_app = EC2("Reporting Environment")
    reporting_app >> efs
    
    # RDS Cluster
    with Cluster("RDS Cluster"):
        main_rds = RDS("Main Database (Read/Write)")
        read_only_rds = RDS("Read-Only Mirror")
        ec2_instances[0] >> main_rds
        ec2_instances[1] >> main_rds
        reporting_app >> read_only_rds
    
    # Websites Cluster
    with Cluster("Websites"):
        third_party = Internet("Third Party Microsites")
        nsp_website = Internet("NSP Website")
        third_party >> Edge(label="API") >> data_site
        nsp_website >> Edge(label="API") >> data_site
    
    # Monitoring and Logging
    cloudwatch = Cloudwatch("CloudWatch")
    ec2_instances[0] >> cloudwatch
    ec2_instances[1] >> cloudwatch
    deployment_ec2 >> cloudwatch
    reporting_app >> cloudwatch
    
    # External connections
    power_bi = PowerBI("PowerBI Dashboard")
    read_only_rds >> Edge(label="Remote Connection") >> power_bi
