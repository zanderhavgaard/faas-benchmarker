#!/bin/bash

# create db server and orchestrator servers

# load utils
source $fbrd/fb_cli/utils.sh

function createOrchestrator {
  cd "$fbrd/infrastructure/orchestrator"

  pmsg "Creating Orchstrator server ..."

  pmsg "Initializing teraform ..."

  bash init.sh

  pmsg "Validating terraform configuration ..."

  terraform validate

  pmsg "Creating the Orchestrator server ..."

  terraform apply -auto-approve

  smsg "Done creating Orchestrator server."

  cd "$fbrd"
}

function createDatabaseServer {
  cd "$fbrd/infrastructure/db_server"

  pmsg "Creating Database server ..."

  pmsg "Initializing teraform ..."

  bash init.sh

  pmsg "Validating terraform configuration ..."

  terraform validate

  pmsg "Creating the server ..."

  terraform apply -auto-approve

  smsg "Done creating Database server."

  cd "$fbrd"
}

msg "This will provision the Orchestrator and database server, would you like to proceed? [yes/no]"
read -n 3 -r ; echo
if [[ $REPLY =~ ^yes$ ]]; then
  createOrchestrator
  echo
  createDatabaseServer
  echo
  smsg "Done creating infrastructure."
fi
