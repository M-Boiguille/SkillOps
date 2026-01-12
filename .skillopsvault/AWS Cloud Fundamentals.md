# AWS Cloud Fundamentals

#aws #cloud #devops #infrastructure

## Services principaux

### EC2 (Elastic Compute Cloud)

Machines virtuelles dans le cloud.

```bash
# AWS CLI - Lister instances
aws ec2 describe-instances

# Lancer instance
aws ec2 run-instances \
  --image-id ami-0c55b159cbfafe1f0 \
  --instance-type t2.micro \
  --key-name MyKeyPair \
  --security-group-ids sg-12345678

# Arrêter/Démarrer
aws ec2 stop-instances --instance-ids i-1234567890abcdef0
aws ec2 start-instances --instance-ids i-1234567890abcdef0

# Terminer (supprimer)
aws ec2 terminate-instances --instance-ids i-1234567890abcdef0
```

**Types d'instances** :
- **t2/t3** : Burstable, général (web apps)
- **m5** : Balanced, général
- **c5** : Compute optimized (calcul)
- **r5** : Memory optimized (databases)
- **p3** : GPU (ML/AI)

### S3 (Simple Storage Service)

Stockage objet scalable et durable.

```bash
# Lister buckets
aws s3 ls

# Créer bucket
aws s3 mb s3://my-bucket-name

# Upload fichier
aws s3 cp file.txt s3://my-bucket/file.txt

# Sync dossier
aws s3 sync ./local-dir s3://my-bucket/remote-dir

# Supprimer
aws s3 rm s3://my-bucket/file.txt
aws s3 rb s3://my-bucket --force  # Supprimer bucket

# Public read (attention sécurité!)
aws s3api put-object-acl \
  --bucket my-bucket \
  --key file.txt \
  --acl public-read
```

**Classes de stockage** :
- **S3 Standard** : Accès fréquent
- **S3 IA (Infrequent Access)** : Accès occasionnel (moins cher)
- **S3 Glacier** : Archive long terme (très peu cher)
- **S3 One Zone-IA** : Une seule AZ (moins cher mais moins résilient)

### RDS (Relational Database Service)

Bases de données managées.

```bash
# Créer instance MySQL
aws rds create-db-instance \
  --db-instance-identifier mydb \
  --db-instance-class db.t3.micro \
  --engine mysql \
  --master-username admin \
  --master-user-password mypassword123 \
  --allocated-storage 20

# Lister instances
aws rds describe-db-instances

# Créer snapshot
aws rds create-db-snapshot \
  --db-instance-identifier mydb \
  --db-snapshot-identifier mydb-snapshot-2026-01-12
```

**Engines supportés** : MySQL, PostgreSQL, MariaDB, Oracle, SQL Server, Aurora

### VPC (Virtual Private Cloud)

Réseau privé virtuel isolé.

```bash
# Créer VPC
aws ec2 create-vpc --cidr-block 10.0.0.0/16

# Créer subnet
aws ec2 create-subnet \
  --vpc-id vpc-12345678 \
  --cidr-block 10.0.1.0/24 \
  --availability-zone us-east-1a

# Créer Internet Gateway
aws ec2 create-internet-gateway
aws ec2 attach-internet-gateway \
  --vpc-id vpc-12345678 \
  --internet-gateway-id igw-12345678
```

**Composants VPC** :
- **Subnets** : Segmentation réseau
- **Route Tables** : Routage du trafic
- **Internet Gateway** : Accès Internet
- **NAT Gateway** : Sortie Internet pour private subnets
- **Security Groups** : Firewall stateful
- **NACLs** : Network ACLs (firewall stateless)

### IAM (Identity and Access Management)

Gestion des accès et permissions.

```bash
# Lister users
aws iam list-users

# Créer user
aws iam create-user --user-name john

# Créer access key
aws iam create-access-key --user-name john

# Attacher policy
aws iam attach-user-policy \
  --user-name john \
  --policy-arn arn:aws:iam::aws:policy/ReadOnlyAccess

# Créer role
aws iam create-role \
  --role-name MyEC2Role \
  --assume-role-policy-document file://trust-policy.json
```

**Exemple de policy JSON** :
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "s3:GetObject",
        "s3:ListBucket"
      ],
      "Resource": [
        "arn:aws:s3:::my-bucket",
        "arn:aws:s3:::my-bucket/*"
      ]
    }
  ]
}
```

### Lambda

Serverless compute - exécuter du code sans gérer de serveurs.

```python
# Exemple Lambda Python
def lambda_handler(event, context):
    """
    Event: Input data (API Gateway, S3 event, etc.)
    Context: Runtime info
    """
    name = event.get('name', 'World')
    return {
        'statusCode': 200,
        'body': f'Hello {name}!'
    }
```

```bash
# Créer fonction Lambda
aws lambda create-function \
  --function-name MyFunction \
  --runtime python3.11 \
  --role arn:aws:iam::123456789012:role/lambda-role \
  --handler lambda_function.lambda_handler \
  --zip-file fileb://function.zip

# Invoquer
aws lambda invoke \
  --function-name MyFunction \
  --payload '{"name": "Alice"}' \
  response.json
```

### CloudWatch

Monitoring et logs.

```bash
# Voir logs
aws logs describe-log-groups
aws logs tail /aws/lambda/MyFunction --follow

# Créer alarm
aws cloudwatch put-metric-alarm \
  --alarm-name cpu-mon \
  --alarm-description "CPU > 80%" \
  --metric-name CPUUtilization \
  --namespace AWS/EC2 \
  --statistic Average \
  --period 300 \
  --threshold 80 \
  --comparison-operator GreaterThanThreshold
```

## CLI et SDK

### Configuration AWS CLI

```bash
# Configurer credentials
aws configure
# AWS Access Key ID: YOUR_KEY
# AWS Secret Access Key: YOUR_SECRET
# Default region: us-east-1
# Default output: json

# Profils multiples
aws configure --profile production
aws s3 ls --profile production

# Variables d'environnement
export AWS_ACCESS_KEY_ID=YOUR_KEY
export AWS_SECRET_ACCESS_KEY=YOUR_SECRET
export AWS_DEFAULT_REGION=us-east-1
```

### Boto3 (Python SDK)

```python
import boto3

# S3 client
s3 = boto3.client('s3')
s3.upload_file('file.txt', 'my-bucket', 'file.txt')

# EC2 resource
ec2 = boto3.resource('ec2')
instances = ec2.instances.filter(
    Filters=[{'Name': 'instance-state-name', 'Values': ['running']}]
)
for instance in instances:
    print(f"{instance.id}: {instance.instance_type}")

# DynamoDB
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('MyTable')
table.put_item(Item={'id': '123', 'name': 'John'})
```

## Infrastructure as Code

### CloudFormation Template (YAML)

```yaml
AWSTemplateFormatVersion: '2010-09-09'
Description: Simple EC2 instance with Security Group

Parameters:
  KeyName:
    Type: AWS::EC2::KeyPair::KeyName
    Description: EC2 Key Pair

Resources:
  MySecurityGroup:
    Type: AWS::EC2::SecurityGroup
    Properties:
      GroupDescription: Allow SSH and HTTP
      SecurityGroupIngress:
        - IpProtocol: tcp
          FromPort: 22
          ToPort: 22
          CidrIp: 0.0.0.0/0
        - IpProtocol: tcp
          FromPort: 80
          ToPort: 80
          CidrIp: 0.0.0.0/0

  MyEC2Instance:
    Type: AWS::EC2::Instance
    Properties:
      ImageId: ami-0c55b159cbfafe1f0
      InstanceType: t2.micro
      KeyName: !Ref KeyName
      SecurityGroups:
        - !Ref MySecurityGroup
      Tags:
        - Key: Name
          Value: MyWebServer

Outputs:
  InstanceId:
    Description: Instance ID
    Value: !Ref MyEC2Instance
  PublicIP:
    Description: Public IP
    Value: !GetAtt MyEC2Instance.PublicIp
```

```bash
# Déployer stack
aws cloudformation create-stack \
  --stack-name my-stack \
  --template-body file://template.yaml \
  --parameters ParameterKey=KeyName,ParameterValue=my-key

# Lister stacks
aws cloudformation list-stacks

# Supprimer stack
aws cloudformation delete-stack --stack-name my-stack
```

## Régions et Zones de disponibilité

```
Région (ex: us-east-1)
├── AZ A (us-east-1a) - Datacenter isolé
├── AZ B (us-east-1b) - Datacenter isolé
└── AZ C (us-east-1c) - Datacenter isolé
```

**Principales régions** :
- **us-east-1** : Virginie (US)
- **us-west-2** : Oregon (US)
- **eu-west-1** : Irlande
- **eu-central-1** : Francfort
- **ap-southeast-1** : Singapour
- **ap-northeast-1** : Tokyo

## Modèle de coûts

**Facteurs de coût** :
- **Compute** : EC2 instances (à l'heure/seconde)
- **Storage** : S3, EBS (par GB/mois)
- **Data transfer** : Sortie Internet (entrée gratuite)
- **Requests** : API calls (S3 GET/PUT, Lambda invocations)

**Optimisation** :
- ✅ Reserved Instances (1-3 ans = -75%)
- ✅ Spot Instances (surplus capacity = -90%)
- ✅ Auto Scaling (payer que ce qu'on utilise)
- ✅ S3 Lifecycle policies (archivage Glacier)
- ✅ CloudWatch billing alarms

```bash
# Voir coûts du mois
aws ce get-cost-and-usage \
  --time-period Start=2026-01-01,End=2026-01-31 \
  --granularity MONTHLY \
  --metrics "BlendedCost"
```

## Best Practices

- ✅ **Sécurité** : Principe du moindre privilège (IAM)
- ✅ **High Availability** : Multi-AZ pour production
- ✅ **Backups** : Snapshots automatisés (EBS, RDS)
- ✅ **Monitoring** : CloudWatch alarms sur métriques critiques
- ✅ **Tags** : Organiser ressources (Environment, Project, Owner)
- ✅ **Cost management** : Budgets et alertes
- ✅ **Infrastructure as Code** : CloudFormation ou Terraform
- ✅ **Encryption** : At rest (EBS, S3) et in transit (HTTPS, TLS)

## Services avancés

- **ECS/EKS** : Container orchestration (Docker/Kubernetes)
- **API Gateway** : Créer et gérer APIs
- **SNS/SQS** : Messaging (pub/sub et queues)
- **DynamoDB** : NoSQL database managée
- **ElastiCache** : Redis/Memcached managé
- **Route 53** : DNS managé
- **CloudFront** : CDN (Content Delivery Network)
- **Elastic Beanstalk** : PaaS (déploiement simplifié)

## Liens

- [[Terraform AWS]]
- [[Docker on AWS]]
- [[Kubernetes EKS]]
- [[AWS Security Best Practices]]

## Notes perso

Date: 2026-01-12
- Configuration multi-comptes avec AWS Organizations
- Utilisation de CloudFormation pour IaC
- TODO: Approfondir networking (VPC peering, Transit Gateway)
- TODO: Certifications AWS (Solutions Architect Associate)
