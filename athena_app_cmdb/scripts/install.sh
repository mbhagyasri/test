#!/bin/bash
set -e

# Section TOOLS

# Checking if all needed tools are present in runtime 

if ! [ -x "$(command -v helm)" ]; then
    echo "Err: helm is not installed!" >&2
    exit 1
fi

if ! [ -x "$(command -v aws)" ]; then
    echo "Err: aws is not installed!"
    exit 1
fi

if ! [ -x "$(command -v kubectl)" ]; then
    echo "Err: kubectl is not installed!" >&2
    exit 1
fi

# End of section
# Section VARIABLES

echo "Checking necessary environment variables"

if [ -z "$AWS_ACCESS_KEY_ID" ] || [ -z "$AWS_SECRET_ACCESS_KEY" ]; then
	echo "Err: AWS_ACCESS_KEY_ID or AWS_SECRET_ACCESS_KEY is not set!"
	echo "ex. export AWS_ACCESS_KEY_ID=\"1234567890\""
	echo "ex. export AWS_SECRET_ACCESS_KEY=\"1234567890\""
	exit 1
else
    echo "OK: AWS_ACCESS_KEY_ID"
    echo "OK: AWS_SECRET_ACCESS_KEY"
fi

if [ -z "$AWS_DEFAULT_REGION" ]; then
	echo "Warn: AWS_DEFAULT_REGION is not set, using default us-west-2"
	echo "ex. export AWS_DEFAULT_REGION=\"us-west-2\""
	export AWS_DEFAULT_REGION="us-west-2"
else
    echo "OK: AWS_DEFAULT_REGION"
fi

if [ -z "$EKS_CLUSTER_NAME" ]; then
	echo "Err: EKS_CLUSTER_NAME is not set!"
	echo "ex. export EKS_CLUSTER_NAME=\"athena-fancy-owl\""
	exit 1
fi

if [ -z "$IQR_ENVIRONMENT" ]; then
	echo "Err: IQR_ENVIRONMENT is not set!"
	echo "ex. export IQR_ENVIRONMENT=\"sandbox\""
	exit 1
fi

if [ -z "$BAMBOO_BUILD_ID" ]; then
	echo "Err: BAMBOO_BUILD_ID is not set!"
	echo "ex. export BAMBOO_BUILD_ID=\"1\""
	exit 1
fi

# End of section

# Generate kubeconfig for specified EKS cluster and test connection

if ! [ "$(aws eks update-kubeconfig --name "$EKS_CLUSTER_NAME" --kubeconfig ./kube_config)" ]; then
	echo "Err: could not get kube config for specified EKS cluster \"$EKS_CLUSTER_NAME\"!"
	exit 1
fi

if ! [ -f "./kube_config" ]; then
	echo "Err: kubeconfig file not found - ./kube_config!"
	exit 1
else
	export KUBECONFIG=./kube_config
fi

if ! [ "$(kubectl cluster-info)" ]; then
    echo "Err: Could not connect to Kubernetes cluster, please check env variable KUBECONFIG!"
    exit 1
fi

# End of section

# Section CUSTOM VARS

region="$(echo $AWS_DEFAULT_REGION | cut -d- -f1)"

# End of section

# Section RESOURCES CHECK

if ! [ -f "./helm/charts/deployment/Values.yaml" ]; then
    echo "Err: custom values file not found - ./helm/charts/deployment/Values.yaml"
    exit 1
fi

if ! [ -f "./helm/values/deployment/Values.${region}-${IQR_ENVIRONMENT}.yaml" ]; then
    echo "Err: custom values file not found - ./helm/values/deployment/Values.${region}-${IQR_ENVIRONMENT}.yaml"
    exit 1
fi

# End of section

# Section INSTALL

echo "Creating namespace cdk-athena-app-cmdb"
if ! [ "$(
	kubectl create namespace cdk-athena-app-cmdb \
	--dry-run=client -o yaml \
	| kubectl apply -f - && \
  kubectl label namespace cdk-athena-app-cmdb \
  istio-injection=enabled --overwrite)" ]; then
    echo "Err: could not create namespace, please check env variable KUBECONFIG!"
    exit 1
fi

echo "Creating external secret for RDS"
# get secret ARN
secretArn="$(aws secretsmanager get-secret-value --secret-id "${region}"-"${IQR_ENVIRONMENT}"-svc-app-registry_db_password | jq -r .ARN)"
# get role ARN
roleArn="$(aws ssm get-parameters --name /platform/cluster/"${region}"-"${IQR_ENVIRONMENT}"_athena-platform/secretRole | jq -r '.Parameters[].Value')"

# Skip secret creation
if [ -n "${secretArn}" ] || [ -n "${roleArn}" ]; then
  if ! [ "$(helm upgrade --install athena-app-cmdb-db-secret ./helm/charts/ext-secret \
    -n cdk-athena-app-registry -f ./helm/charts/ext-secret/values.yaml \
    --set roleArn="${roleArn}"  \
    --set sourceSecretKey="${secretArn}" )" ]; then
  	echo "Err: unable to create external secret for RDS into cluster - $EKS_CLUSTER_NAME"
  	exit 1
  fi
fi

# Choose correct domain for app-registry
case "$IQR_ENVIRONMENT" in
  prod)
    APP_DOMAIN="athena.connectcdk.com"
    ;;
  *)
    APP_DOMAIN="athena-${IQR_ENVIRONMENT}.connectcdk.com"
    ;;
esac

echo "Installing athena-app-cmdb to cluster - $EKS_CLUSTER_NAME"
if ! [ "$(helm upgrade --install athena-app-registry ./helm/charts/deployment \
  -n cdk-athena-app-cmdb -f ./helm/charts/deployment/Values.yaml -f ./helm/values/deployment/Values."${region}-${IQR_ENVIRONMENT}".yaml \
  --set domain="${APP_DOMAIN}" --set location_id="location-${region}-${IQR_ENVIRONMENT}" \
  --set image=artifactory.cobalt.com/athena/athena-platform/athena-app-cmdb:"$BAMBOO_BUILD_ID"  )" ]; then
	echo "Err: unable to install athena-app-cmdb into cluster - $EKS_CLUSTER_NAME"
	exit 1
fi

# End of section
# Section TRAPS

function onExit {
    rm -f ./kube_config
}

trap onExit EXIT ERR

# End of section
