# various utils

## //util/bin/with

  execute a command with an extended/modified environment

### usage

    with ENV COMMAND

  where `ENV` is the name of the environment and
  `COMMAND` your to-be-executed command (-line).

### environment

  `env_dir` defines the directory where environment files are searched
  (default: `$HOME/.env.d`).

### example

    cat > ~/.env.d/frh-ire <<EOF
    export api_url=...
    export api_key=...
    export api_hash=...
    EOF

    with frh-ire //ext/solus/bin/client info
