from aws_cdk import Stack, aws_ec2 as ec2, aws_rds as rds, Duration, CfnOutput
from constructs import Construct


class TemperatureMonitorStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # VPC
        vpc = ec2.Vpc(
            self,
            "TempMonitorVPC",
            max_azs=2,
            nat_gateways=0,  # Save costs by using VPC endpoints instead
            subnet_configuration=[
                ec2.SubnetConfiguration(
                    name="public", subnet_type=ec2.SubnetType.PUBLIC, cidr_mask=24
                ),
                ec2.SubnetConfiguration(
                    name="isolated",
                    subnet_type=ec2.SubnetType.PRIVATE_ISOLATED,
                    cidr_mask=24,
                ),
            ],
        )

        # Security Group for RDS
        db_security_group = ec2.SecurityGroup(
            self,
            "DatabaseSecurityGroup",
            vpc=vpc,
            description="Security group for RDS instance",
            allow_all_outbound=True,
        )

        db_security_group.add_ingress_rule(
            peer=ec2.Peer.ipv4(vpc.vpc_cidr_block),
            connection=ec2.Port.tcp(5432),
            description="Allow PostgreSQL access from within VPC",
        )

        # RDS Instance
        database = rds.DatabaseInstance(
            self,
            "Database",
            engine=rds.DatabaseInstanceEngine.postgres(
                version=rds.PostgresEngineVersion.VER_13
            ),
            instance_type=ec2.InstanceType.of(
                ec2.InstanceClass.BURSTABLE3, ec2.InstanceSize.MICRO
            ),
            vpc=vpc,
            vpc_subnets=ec2.SubnetSelection(
                subnet_type=ec2.SubnetType.PRIVATE_ISOLATED
            ),
            allocated_storage=20,
            max_allocated_storage=20,  # Prevent autoscaling beyond free tier
            security_groups=[db_security_group],
            removal_policy=RemovalPolicy.DESTROY,  # For development only
            deletion_protection=False,  # For development only
            backup_retention=Duration.days(7),
        )

        # Outputs
        CfnOutput(self, "DatabaseEndpoint", value=database.instance_endpoint.hostname)
        CfnOutput(self, "DatabaseName", value=database.instance_identifier)
