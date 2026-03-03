# =====================
# VARIABLES GENERALES
# =====================
AWS_REGION=us-east-1
ACCOUNT_ID=387050840675

# Credenciales fijas para la base de datos
DB_USER=proyectogrupo4
DB_PASSWORD=proyectogrupo4

# Microservicios
SERVICES=busquedas-app inventarios-app reservas-app
FOLDERS=busquedas_app inventario_app reserva_app
IMAGE_TAG=v1.0.0

# Nueva version imagen
SERVICES_NEW=busquedas-app inventarios-app reservas-app
FOLDERS_NEW=busquedas_app inventario_app reserva_app
IMAGE_TAG_NEW=v2.0.0

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

docker-push-all-local:
	@i=0; \
	for service in $(SERVICES); do \
		folder=$$(echo $(FOLDERS) | cut -d' ' -f$$((i+1))); \
		echo ">>> Construyendo y subiendo $$service desde $$folder"; \
		docker build --rm -t $$service:$(IMAGE_TAG) -f $$folder/Dockerfile $$folder/.; \
		docker tag $$service:$(IMAGE_TAG) $(ACCOUNT_ID).dkr.ecr.$(AWS_REGION).amazonaws.com/$$service:$(IMAGE_TAG); \
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

# =====================
# WORKFLOWS COMPLETOS
# =====================

infra: ecr rds eks
images: ecr-login docker-push-all
deploy: infra images ingress
destroy: destroy-ingress destroy-eks destroy-rds destroy-ecr
