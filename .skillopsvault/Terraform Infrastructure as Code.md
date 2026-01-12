# Terraform Infrastructure as Code

#terraform #iac #infrastructure #cloud #aws

## Introduction

**Terraform** est un outil d'Infrastructure as Code (IaC) qui permet de définir et provisionner l'infrastructure via des fichiers de configuration.

## Concepts fondamentaux

### Providers
Plugins qui permettent d'interagir avec des APIs (AWS, Azure, GCP, etc.)

```hcl
terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = "eu-west-1"
}
```

### Resources
Composants d'infrastructure (EC2, VPC, S3, etc.)

```hcl
resource "aws_instance" "web" {
  ami           = "ami-0c55b159cbfafe1f0"
  instance_type = "t2.micro"

  tags = {
    Name = "WebServer"
    Environment = "dev"
  }
}
```

### Variables
```hcl
variable "instance_type" {
  description = "EC2 instance type"
  type        = string
  default     = "t2.micro"
}

variable "environment" {
  type = string
}
```

### Outputs
```hcl
output "instance_ip" {
  value = aws_instance.web.public_ip
  description = "Public IP of web server"
}
```

### Data Sources
Récupérer des informations existantes

```hcl
data "aws_ami" "ubuntu" {
  most_recent = true
  owners      = ["099720109477"]

  filter {
    name   = "name"
    values = ["ubuntu/images/hvm-ssd/ubuntu-focal-20.04-amd64-server-*"]
  }
}
```

## Workflow Terraform

```bash
# 1. Initialiser le projet
terraform init

# 2. Formater le code
terraform fmt

# 3. Valider la syntaxe
terraform validate

# 4. Planifier les changements
terraform plan
terraform plan -out=tfplan

# 5. Appliquer les changements
terraform apply
terraform apply tfplan

# 6. Détruire l'infrastructure
terraform destroy

# Autres commandes utiles
terraform show
terraform state list
terraform state show aws_instance.web
terraform output
```

## Structure de projet

```
terraform-project/
├── main.tf          # Ressources principales
├── variables.tf     # Déclaration des variables
├── outputs.tf       # Outputs
├── terraform.tfvars # Valeurs des variables
├── providers.tf     # Configuration providers
├── versions.tf      # Contraintes de version
└── modules/
    ├── vpc/
    ├── ec2/
    └── rds/
```

## Modules

### Créer un module
```hcl
# modules/vpc/main.tf
resource "aws_vpc" "main" {
  cidr_block = var.vpc_cidr

  tags = {
    Name = var.vpc_name
  }
}

# modules/vpc/variables.tf
variable "vpc_cidr" {
  type = string
}

variable "vpc_name" {
  type = string
}

# modules/vpc/outputs.tf
output "vpc_id" {
  value = aws_vpc.main.id
}
```

### Utiliser un module
```hcl
module "vpc" {
  source   = "./modules/vpc"
  vpc_cidr = "10.0.0.0/16"
  vpc_name = "production-vpc"
}

resource "aws_subnet" "public" {
  vpc_id     = module.vpc.vpc_id
  cidr_block = "10.0.1.0/24"
}
```

## State Management

### Backend distant (S3 + DynamoDB)
```hcl
terraform {
  backend "s3" {
    bucket         = "my-terraform-state"
    key            = "prod/terraform.tfstate"
    region         = "eu-west-1"
    dynamodb_table = "terraform-locks"
    encrypt        = true
  }
}
```

### Commandes state
```bash
terraform state list
terraform state show <resource>
terraform state mv <source> <destination>
terraform state rm <resource>
terraform import <resource> <id>
```

## Best Practices

- ✅ Utiliser des modules réutilisables
- ✅ Versionner le state dans un backend distant
- ✅ Activer le locking (DynamoDB)
- ✅ Ne jamais commiter terraform.tfvars avec des secrets
- ✅ Utiliser des workspaces pour les environnements
- ✅ Documenter les variables et outputs
- ✅ Utiliser terraform fmt et validate
- ✅ Faire des plans avant apply

## Workspaces

```bash
terraform workspace list
terraform workspace new dev
terraform workspace select prod
terraform workspace show
```

## Exemples pratiques

### VPC complet
```hcl
resource "aws_vpc" "main" {
  cidr_block           = "10.0.0.0/16"
  enable_dns_hostnames = true

  tags = {
    Name = "main-vpc"
  }
}

resource "aws_subnet" "public" {
  vpc_id            = aws_vpc.main.id
  cidr_block        = "10.0.1.0/24"
  availability_zone = "eu-west-1a"

  map_public_ip_on_launch = true
}

resource "aws_internet_gateway" "gw" {
  vpc_id = aws_vpc.main.id
}

resource "aws_route_table" "public" {
  vpc_id = aws_vpc.main.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.gw.id
  }
}
```

## Liens

- [[AWS Basics]]
- [[Terraform Modules]]
- [[CI/CD with Terraform]]
- [[Cloud Security]]

## Notes perso

Date: 2026-01-12
- Déployé une infrastructure 3-tiers sur AWS
- Utilisé remote state sur S3 avec locking
- Prochaine étape: Créer des modules réutilisables
