#!/usr/bin/env bash
# Run the real Terraform code against moto (a local AWS API emulator) with dummy credentials.
#   scripts/terraform-mock.sh plan|apply|destroy|down
set -euo pipefail
cd "$(dirname "$0")/../terraform"
ACTION="${1:-plan}"

if [[ "$ACTION" == "down" ]]; then
  rm -f provider_override.tf terraform.tfstate*
  docker rm -f careslot-moto >/dev/null 2>&1 || true
  echo "mock AWS stopped and override removed"; exit 0
fi

if ! docker ps --format '{{.Names}}' | grep -q '^careslot-moto$'; then
  docker run -d --rm --name careslot-moto -e MOTO_IAM_LOAD_MANAGED_POLICIES=true -p 5055:5000 motoserver/moto:5.1.14 >/dev/null
  until curl -s localhost:5055 >/dev/null; do sleep 1; done
  echo "moto AWS emulator listening on :5055 (macOS AirPlay owns :5000)"
fi

cp mock/provider_override.tf provider_override.tf
export AWS_ACCESS_KEY_ID=mock-access-key AWS_SECRET_ACCESS_KEY=mock-secret-key AWS_REGION=ap-south-1
terraform init -input=false >/dev/null
case "$ACTION" in
  plan)    terraform plan -input=false ;;
  apply)   terraform apply -input=false -auto-approve ;;
  destroy) terraform destroy -input=false -auto-approve ;;
  *) echo "usage: $0 plan|apply|destroy|down"; exit 1 ;;
esac
