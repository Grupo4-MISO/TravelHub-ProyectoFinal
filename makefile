# =====================
# VARIABLES GENERALES
# =====================
AWS_REGION=us-east-1
ACCOUNT_ID=387050840675

# Credenciales fijas para la base de datos
DB_USER=proyectogrupo4
DB_PASSWORD=proyectogrupo4

# Microservicios
SERVICES=busquedas-app inventarios-app reservas-app comentarios-app auth-app transacciones-app clientes-app proveedores-app
SERVICES_LAMBDA=webhook-pagos-app email-app
FOLDERS_LAMBDA=webhook_pagos email
FOLDERS=busquedas_app inventario_app reserva_app comentariosapp autenticadorapp transaccionesapp clientesapp proveedoresapp
IMAGE_TAG=v1.0.0

# Nueva version imagen
SERVICES_NEW=reservas-app transacciones-app
FOLDERS_NEW=reserva_app transaccionesapp
IMAGE_TAG_NEW=v7.0.0

# Nueva version imagen lambda
SERVICES_LAMBDA_NEW=email-app
FOLDERS_LAMBDA_NEW=email
IMAGE_TAG_LAMBDA_NEW=v5.0.0

export AWS_REGION

# =====================
# STACKS INDIVIDUALES
# =====================

ecr:
	cd terraform/stacks/ecr && \
	terraform init -backend-config="../../environments/ecr/backend.tfvars" && \
	terraform plan -var-file="../../environments/ecr/terraform.tfvars" -out .tfplan && \
	terraform apply ".tfplan"

rds:
	cd terraform/stacks/rds && \
	terraform init -backend-config="../../environments/rds/backend.tfvars" && \
	terraform plan -var-file="../../environments/rds/terraform.tfvars" -out .tfplan && \
	terraform apply ".tfplan"

eks:
	cd terraform/stacks/eks && \
	terraform init -backend-config="../../environments/eks/backend.tfvars" && \
	terraform plan -var-file="../../environments/eks/terraform.tfvars" -out .tfplan && \
	terraform apply ".tfplan" && \
	aws eks update-kubeconfig --region $(AWS_REGION) --name proyecto-final-grupo-4

elasticache:
	cd terraform/stacks/elasticache && \
	terraform init -backend-config="../../environments/elasticache/backend.tfvars" && \
	terraform plan -var-file="../../environments/elasticache/terraform.tfvars" -out .tfplan && \
	terraform apply ".tfplan"

sqs:
	cd terraform/stacks/sqs && \
	terraform init -backend-config="../../environments/sqs/backend.tfvars" && \
	terraform plan -var-file="../../environments/sqs/terraform.tfvars" -out .tfplan && \
	terraform apply ".tfplan"

lambda:
	cd terraform/stacks/lambda && \
	terraform init -backend-config="../../environments/lambda/backend.tfvars" && \
	terraform plan -var-file="../../environments/lambda/terraform.tfvars" -out .tfplan && \
	terraform apply ".tfplan"

lambda-queue:
	cd terraform/stacks/lambda-queue && \
	terraform init -backend-config="../../environments/lambda-queue/backend.tfvars" && \
	terraform plan -var-file="../../environments/lambda-queue/terraform.tfvars" -out .tfplan && \
	terraform apply ".tfplan"

ingress:
	helm repo add ingress-nginx https://kubernetes.github.io/ingress-nginx && \
	helm repo update && \
	helm install ingress-nginx ingress-nginx/ingress-nginx \
		--namespace ingress-nginx \
		--create-namespace \
		--set controller.service.type=LoadBalancer

# =====================
# DESTROY
# =====================

destroy-ecr:
	cd terraform/stacks/ecr && \
	terraform destroy -var-file="../../environments/ecr/terraform.tfvars"

destroy-rds:
	cd terraform/stacks/rds && \
	terraform destroy -var-file="../../environments/rds/terraform.tfvars"

destroy-eks:
	cd terraform/stacks/eks && \
	terraform destroy -var-file="../../environments/eks/terraform.tfvars"

destroy-elasticache:
	cd terraform/stacks/elasticache && \
	terraform destroy -var-file="../../environments/elasticache/terraform.tfvars"

destroy-sqs:
	cd terraform/stacks/sqs && \
	terraform destroy -var-file="../../environments/sqs/terraform.tfvars"

destroy-lambda:
	cd terraform/stacks/lambda && \
	terraform destroy -var-file="../../environments/lambda/terraform.tfvars"

destroy-lambda-queue:
	cd terraform/stacks/lambda-queue && \
	terraform destroy -var-file="../../environments/lambda-queue/terraform.tfvars"

destroy-ingress:
	kubectl delete service ingress-nginx-controller -n ingress-nginx || true
	helm uninstall ingress-nginx -n ingress-nginx || true
	kubectl delete ns ingress-nginx || true

# =====================
# DOCKER + ECR
# =====================

ecr-login:
	aws ecr get-login-password --region $(AWS_REGION) | \
	docker login --username AWS --password-stdin $(ACCOUNT_ID).dkr.ecr.$(AWS_REGION).amazonaws.com

docker-push-all:
	@i=0; \
	for service in $(SERVICES); do \
		folder=$$(echo $(FOLDERS) | cut -d' ' -f$$((i+1))); \
		echo ">>> Construyendo y subiendo $$service desde $$folder"; \
		docker build --rm -t $$service:$(IMAGE_TAG) -f $$folder/Dockerfile $$folder/.; \
		docker tag $$service:$(IMAGE_TAG) $(ACCOUNT_ID).dkr.ecr.$(AWS_REGION).amazonaws.com/$$service:$(IMAGE_TAG); \
		docker push $(ACCOUNT_ID).dkr.ecr.$(AWS_REGION).amazonaws.com/$$service:$(IMAGE_TAG); \
		i=$$((i+1)); \
	done

docker-push-lambda:
	@i=0; \
	for service in $(SERVICES_LAMBDA); do \
		folder=$$(echo $(FOLDERS_LAMBDA) | cut -d' ' -f$$((i+1))); \
		echo ">>> Construyendo y subiendo $$service desde $$folder"; \
		docker buildx build \
			--platform linux/amd64 \
			--provenance=false \
			-t $(ACCOUNT_ID).dkr.ecr.$(AWS_REGION).amazonaws.com/$$service:$(IMAGE_TAG) \
			-f $$folder/Dockerfile $$folder/. \
			--push; \
		i=$$((i+1)); \
	done

docker-push-new:
	@i=0; \
	for service in $(SERVICES_NEW); do \
		folder=$$(echo $(FOLDERS_NEW) | cut -d' ' -f$$((i+1))); \
		echo ">>> Construyendo y subiendo $$service desde $$folder"; \
		docker build --rm -t $$service:$(IMAGE_TAG_NEW) -f $$folder/Dockerfile $$folder/.; \
		docker tag $$service:$(IMAGE_TAG_NEW) $(ACCOUNT_ID).dkr.ecr.$(AWS_REGION).amazonaws.com/$$service:$(IMAGE_TAG_NEW); \
		docker push $(ACCOUNT_ID).dkr.ecr.$(AWS_REGION).amazonaws.com/$$service:$(IMAGE_TAG_NEW); \
		i=$$((i+1)); \
	done

docker-push-lambda-new:
	docker buildx build \
		--platform linux/amd64 \
		--provenance=false \
		-t $(ACCOUNT_ID).dkr.ecr.$(AWS_REGION).amazonaws.com/$(SERVICES_LAMBDA_NEW):$(IMAGE_TAG_LAMBDA_NEW) \
		-f $(FOLDERS_LAMBDA_NEW)/Dockerfile $(FOLDERS_LAMBDA_NEW)/. \
		--push

# =====================
# WORKFLOWS COMPLETOS
# =====================

infra: ecr rds eks elasticache sqs lambda
images: ecr-login docker-push-all docker-push-lambda
deploy: infra images ingress
deploy-lambda-queue: lambda-queue
destroy: destroy-ingress destroy-elasticache destroy-eks destroy-rds destroy-ecr destroy-sqs destroy-lambda-queue destroy-lambda