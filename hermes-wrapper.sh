#!/bin/bash
ln -sf /opt/hermes/.venv/bin/hermes /usr/local/bin/hermes
exec /opt/hermes/.venv/bin/hermes dashboard --host 0.0.0.0 --insecure &
exec /opt/hermes/.venv/bin/hermes "$@"
