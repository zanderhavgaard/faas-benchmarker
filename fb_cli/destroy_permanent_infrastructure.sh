#!/bin/bash

# load utils
source $fbrd/fb_cli/utils.sh

function destroyOrchestrator {
  cd "$fbrd/infrastructure/orchestrator"

  pmsg "Destroying Orchestrator server ..."

  terraform destroy

  smsg "Done destroying Orchestrator server."

  cd "$fbrd"
}

function destroyDatabaseServer {
  cd "$fbrd/infrastructure/db_server"

  pmsg "Destroying database server ..."

  terraform destroy

  smsg "Done destroying database server."

  cd "$fbrd"
}

msg "This will destroy the Orchestrator and database server, would you like to proceed? [yes/no]"
read -n 3 -r ; echo
if [[ $REPLY =~ ^yes$ ]]; then
  msg "\n\tYou must anwser yes when prompted.\n"
  destroyOrchestrator
  echo
  destroyDatabaseServer
  echo
  smsg "Done destroying infrastructure."
fi
