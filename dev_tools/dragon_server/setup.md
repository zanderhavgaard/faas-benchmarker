# ufw

ufw default deny incoming
ufw default allow outgoing
ufw allow ssh
ufw allow in on cni0
ufw allow out on cni0
ufw default allow routed

## allow specified ips to access the gateway
ufw allow from <ip> to any port 31112

# deploy microk8s

## microk8s
snap install microk8s --classic

## setup aliases
snap alias microk8s.kubectl kubectl
snap alias microk8s.helm helm

## setup user permissions
usermod -a -G microk8s $USER
chown -f -R $USER ~/.kube

## configure cluster
microk8s start
microk8s status --wait-ready
microk8s enable dns storage registry

### (optional) setup aliases for microk8s internal tools (we will assume commands are aliased)
snap alias microk8s.kubectl kubectl
snap alias microk8s.helm helm

# openfaas

## clone faas-netes repo
git clone https://github.com/openfaas/faas-netes

## create openfaas and openfaas-fn namespaces
kubectl apply -f https://raw.githubusercontent.com/openfaas/faas-netes/master/namespaces.yml

============================

microk8s enable helm
helm init

## deploy the openfaas stack
helm upgrade \
    --install \
    --namespace openfaas \
    --set functionNamespace=openfaas-fn \
    --set generateBasicAuth=true \
    --set faasIdler.dryRun=false \
    --set faasIdler.inactivityDuration=30m \
    --set faasIdler.reconcileInterval=5m \
    openfaas \
    faas-netes/chart/openfaas

## get the generated password
PASSWORD=$(kubectl -n openfaas get secret basic-auth -o jsonpath="{.data.basic-auth-password}" | base64 --decode) \
    && echo "OpenFaaS admin password: $PASSWORD"


============================

### first generate openfaas password for basic auth
PASSWORD=$(head -c 12 /dev/urandom | shasum| cut -d' ' -f1)

### then create kubernetes secret
kubectl -n openfaas create secret generic basic-auth \
--from-literal=basic-auth-user=admin \
--from-literal=basic-auth-password="$PASSWORD"

### deploy the openfaas stack
kubectl apply -f faas-netes/yaml

============================

microk8s enable helm
helm init

## add openfaas helm repo
helm repo add openfaas https://openfaas.github.io/faas-netes/
helm repo update

## deploy the openfaas stack
helm repo update && helm upgrade openfaas --install openfaas/openfaas \
    --namespace openfaas  \
    --set functionNamespace=openfaas-fn \
    --set generateBasicAuth=true \
    --set faasIdler.dryRun=false \
    --set faasIdler.inactivityDuration=30m \
    --set faasIdler.reconcileInterval=5m

## get the generated password
PASSWORD=$(kubectl -n openfaas get secret basic-auth -o jsonpath="{.data.basic-auth-password}" | base64 --decode) \
    && echo "OpenFaaS admin password: $PASSWORD"

============================

# configure faas-cli
kubectl port-forward svc/gateway -n openfaas 31112:8080 &
export OPENFAAS_URL=http://127.0.0.1:31112
echo -n $PASSWORD | faas-cli login --password-stdin

# get password from cluster
kubectl get secret -n openfaas basic-auth -o jsonpath="{.data.basic-auth-password}" | base64 --decode ; echo

## troubleshooting

### reset cluster
microk8s reset

### uninstall openfaas
kubectl delete namespace openfaas openfaas-fn
kubectl delete clusterrole openfaas-prometheus
