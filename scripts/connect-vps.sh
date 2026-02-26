#!/bin/bash

# ============================================
# VPS Connection — master script
# ============================================
# Usage: ./scripts/connect-vps.sh [command]
#
# CUSTOMIZE: Update VPS_HOST, PROJECT_PATH, CONTAINER_NAME

set -e

# Configuration
VPS_HOST="{your-vps-host}"         # From ~/.ssh/config
PROJECT_PATH="/home/{user}/{project}"
CONTAINER_NAME="{project}-app"
CONTAINER_PG="{project}-postgres"
CONTAINER_REDIS="{project}-redis"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

show_help() {
    echo -e "${BLUE}=========================================="
    echo " VPS Connection — Master Script"
    echo -e "==========================================${NC}"
    echo ""
    echo "Usage: ./scripts/connect-vps.sh [command]"
    echo ""
    echo "Commands:"
    echo ""
    echo -e "  ${GREEN}shell${NC}           - Shell into app container"
    echo -e "  ${GREEN}logs${NC}            - Follow app logs"
    echo -e "  ${GREEN}logs-all${NC}        - Follow all service logs"
    echo -e "  ${GREEN}status${NC}          - Show container status"
    echo -e "  ${GREEN}stats${NC}           - Show resource usage"
    echo -e "  ${GREEN}restart${NC}         - Restart app container"
    echo -e "  ${GREEN}restart-all${NC}     - Restart all services"
    echo -e "  ${GREEN}python${NC}          - Python REPL in container"
    echo -e "  ${GREEN}postgres${NC}        - Connect to PostgreSQL"
    echo -e "  ${GREEN}redis${NC}           - Connect to Redis CLI"
    echo -e "  ${GREEN}ssh${NC}             - SSH to VPS server"
    echo -e "  ${GREEN}exec <cmd>${NC}      - Run command in app container"
    echo ""
}

run_on_vps() {
    local cmd="$1"
    ssh "$VPS_HOST" "cd $PROJECT_PATH && $cmd"
}

check_ssh_config() {
    if ! ssh -o ConnectTimeout=5 "$VPS_HOST" "echo 'ok'" > /dev/null 2>&1; then
        echo -e "${RED}Cannot connect to VPS ($VPS_HOST)${NC}"
        echo "Check ~/.ssh/config and ensure the host is configured."
        exit 1
    fi
}

main() {
    local command="${1:-help}"

    case "$command" in
        shell)
            check_ssh_config
            echo -e "${BLUE}Connecting to app container shell...${NC}"
            ssh -t "$VPS_HOST" "cd $PROJECT_PATH && docker exec -it $CONTAINER_NAME /bin/sh"
            ;;

        logs)
            check_ssh_config
            echo -e "${BLUE}Following app logs (Ctrl+C to exit)...${NC}"
            ssh -t "$VPS_HOST" "cd $PROJECT_PATH && docker logs -f --tail=100 $CONTAINER_NAME"
            ;;

        logs-all)
            check_ssh_config
            echo -e "${BLUE}Following all service logs (Ctrl+C to exit)...${NC}"
            ssh -t "$VPS_HOST" "cd $PROJECT_PATH && docker compose logs -f"
            ;;

        status)
            check_ssh_config
            echo -e "${BLUE}Container status:${NC}"
            run_on_vps "docker compose ps"
            ;;

        stats)
            check_ssh_config
            echo -e "${BLUE}Resource usage (Ctrl+C to exit):${NC}"
            ssh -t "$VPS_HOST" "docker stats"
            ;;

        restart)
            check_ssh_config
            echo -e "${YELLOW}Restarting app container...${NC}"
            run_on_vps "docker compose restart $CONTAINER_NAME"
            echo -e "${GREEN}App restarted${NC}"
            ;;

        restart-all)
            check_ssh_config
            echo -e "${YELLOW}Restarting all services...${NC}"
            run_on_vps "docker compose restart"
            echo -e "${GREEN}All services restarted${NC}"
            ;;

        python)
            check_ssh_config
            echo -e "${BLUE}Starting Python REPL in container...${NC}"
            ssh -t "$VPS_HOST" "cd $PROJECT_PATH && docker exec -it $CONTAINER_NAME python"
            ;;

        postgres)
            check_ssh_config
            echo -e "${BLUE}Connecting to PostgreSQL...${NC}"
            ssh -t "$VPS_HOST" "cd $PROJECT_PATH && docker exec -it $CONTAINER_PG psql -U postgres"
            ;;

        redis)
            check_ssh_config
            echo -e "${BLUE}Connecting to Redis CLI...${NC}"
            echo -e "${YELLOW}Use AUTH command with password from .env${NC}"
            ssh -t "$VPS_HOST" "cd $PROJECT_PATH && docker exec -it $CONTAINER_REDIS redis-cli"
            ;;

        ssh)
            check_ssh_config
            echo -e "${BLUE}SSH to VPS server...${NC}"
            ssh -t "$VPS_HOST" "cd $PROJECT_PATH && exec \$SHELL"
            ;;

        exec)
            if [ -z "$2" ]; then
                echo -e "${RED}Specify a command to execute${NC}"
                echo "Example: ./scripts/connect-vps.sh exec 'ls -la /app'"
                exit 1
            fi
            check_ssh_config
            echo -e "${BLUE}Executing command in container...${NC}"
            ssh -t "$VPS_HOST" "cd $PROJECT_PATH && docker exec $CONTAINER_NAME $2"
            ;;

        help|--help|-h)
            show_help
            ;;

        *)
            echo -e "${RED}Unknown command: $command${NC}"
            echo ""
            show_help
            exit 1
            ;;
    esac
}

main "$@"
