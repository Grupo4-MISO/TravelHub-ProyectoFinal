1. Creación del clúster en EKS
2. Conexión con kubectl
    - `aws configure`
    - `aws sts get-caller-identity --region us-east-1`
    - `aws eks update-kubeconfig --name travel-hub-project --region us-east-1`
    - `aws eks create-access-entry --cluster-name travel-hub-project --principal-arn arn:aws:iam::050451362222:user/nei-aws-cli --region us-east-1`
    - `aws eks associate-access-policy --cluster-name travel-hub-project --principal-arn arn:aws:iam::050451362222:user/nei-aws-cli --policy-arn arn:aws:eks::aws:cluster-access-policy/AmazonEKSClusterAdminPolicy --access-scope type=cluster --region us-east-1`
    - `kubectl get node`
3. Instalar Prometheus y Alertmanager:
    - helm repo add prometheus-community https://prometheus-community.github.io
    - helm repo update
    - kubectl create namespace monitoring
    - helm install my-prometheus prometheus-community/kube-prometheus-stack -f values-eks.yaml -n monitoring
**Nota:** Debes apuntar al archivo values-eks.yaml

4. Crear los recursos en el clúster
    - kubectl apply -f deployment.yaml
    - kubectl apply -f alert-eks.yaml

5. Eliminar el clúster
    - eksctl delete cluster --name travel-hub-project

