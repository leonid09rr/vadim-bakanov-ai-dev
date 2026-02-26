#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(dirname "$SCRIPT_DIR")"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

log_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[OK]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

# Get project directory from config path
get_project_dir() {
    local config="$1"
    dirname "$(realpath "$config")"
}

# Ensure .env.local exists with all required keys (in project dir)
ensure_env_file() {
    local project_dir="$1"
    local env_file="$project_dir/.env.local"
    local missing_keys=""

    # Create file if doesn't exist
    if [ ! -f "$env_file" ]; then
        cat > "$env_file" << 'EOF'
# SEO Research API Keys
# Fill in your credentials below

# DataForSEO - keyword data API
# Get your credentials: https://dataforseo.com/apis/getting-started
DATAFORSEO_LOGIN=your-dataforseo-login
DATAFORSEO_PASSWORD=your-dataforseo-password

# OpenRouter - embeddings API
# Get your API key: https://openrouter.ai/keys
OPENROUTER_API_KEY=your-openrouter-api-key
EOF
        log_info "Created $env_file with placeholder values"
    fi

    # Source the env file (disable nounset temporarily)
    set +u
    set -a
    . "$env_file"
    set +a
    set -u

    # Check DATAFORSEO_LOGIN
    if [ -z "${DATAFORSEO_LOGIN:-}" ] || [ "$DATAFORSEO_LOGIN" = "your-dataforseo-login" ]; then
        missing_keys="$missing_keys DATAFORSEO_LOGIN"
    fi

    # Check DATAFORSEO_PASSWORD
    if [ -z "${DATAFORSEO_PASSWORD:-}" ] || [ "$DATAFORSEO_PASSWORD" = "your-dataforseo-password" ]; then
        missing_keys="$missing_keys DATAFORSEO_PASSWORD"
    fi

    # Check OPENROUTER_API_KEY
    if [ -z "${OPENROUTER_API_KEY:-}" ] || [ "$OPENROUTER_API_KEY" = "your-openrouter-api-key" ]; then
        missing_keys="$missing_keys OPENROUTER_API_KEY"
    fi

    # If any keys are missing/placeholder, show error and exit
    if [ -n "$missing_keys" ]; then
        echo ""
        log_error "API keys not configured in $env_file"
        echo ""
        echo "Missing or placeholder values for:"
        for key in $missing_keys; do
            echo "  - $key"
        done
        echo ""
        echo "Please edit $env_file and fill in your credentials:"
        echo ""
        echo "  DataForSEO (keyword data):"
        echo "    - Sign up: https://dataforseo.com"
        echo "    - Getting started: https://dataforseo.com/apis/getting-started"
        echo "    - Your login is your email, password is in API settings"
        echo ""
        echo "  OpenRouter (embeddings):"
        echo "    - Sign up: https://openrouter.ai"
        echo "    - Create API key: https://openrouter.ai/keys"
        echo ""
        echo "After filling in the credentials, run the command again."
        exit 2
    fi

    log_success "API keys loaded from $env_file"
}

# Check and install UV if needed
ensure_uv() {
    if command -v uv &> /dev/null; then
        return 0
    fi

    log_warn "UV not found. Installing..."
    curl -LsSf https://astral.sh/uv/install.sh | sh

    # Add to PATH for current session
    export PATH="$HOME/.local/bin:$PATH"

    if command -v uv &> /dev/null; then
        log_success "UV installed successfully"
    else
        log_error "Failed to install UV. Please install manually: https://docs.astral.sh/uv/"
        exit 1
    fi
}

# Validate config file exists
validate_config() {
    local config="$1"
    if [[ ! -f "$config" ]]; then
        log_error "Config file not found: $config"
        exit 1
    fi
    log_info "Using config: $config"
}

# Setup cache directories and gitignore in project dir
setup_project_dirs() {
    local project_dir="$1"
    local cache_dir="$project_dir/.cache"
    local gitignore="$project_dir/.gitignore"

    mkdir -p "$cache_dir/raw"
    mkdir -p "$cache_dir/processed"
    mkdir -p "$cache_dir/embeddings"
    mkdir -p "$cache_dir/clusters"

    # Create/update .gitignore
    if [ ! -f "$gitignore" ]; then
        cat > "$gitignore" << 'EOF'
# SEO Research - auto-generated
.env.local
.cache/
EOF
    else
        # Ensure entries exist
        grep -q "^\.env\.local$" "$gitignore" || echo ".env.local" >> "$gitignore"
        grep -q "^\.cache/$" "$gitignore" || echo ".cache/" >> "$gitignore"
    fi
}

# Commands
cmd_fetch() {
    local config="${1:-config.json}"
    shift || true
    validate_config "$config"

    local project_dir=$(get_project_dir "$config")
    ensure_env_file "$project_dir"
    ensure_uv
    setup_project_dirs "$project_dir"

    log_info "Fetching keywords from DataForSEO..."
    uv run "$SCRIPT_DIR/fetch_keywords.py" "$config" "$@"
}

cmd_preprocess() {
    local config="${1:-config.json}"
    validate_config "$config"
    ensure_uv

    log_info "Preprocessing data..."
    uv run "$SCRIPT_DIR/preprocess.py" "$config"
}

cmd_embed() {
    local config="${1:-config.json}"
    validate_config "$config"

    local project_dir=$(get_project_dir "$config")
    ensure_env_file "$project_dir"
    ensure_uv

    log_info "Generating embeddings..."
    uv run "$SCRIPT_DIR/embed.py" "$config"
}

cmd_cluster() {
    local config="${1:-config.json}"
    shift || true
    validate_config "$config"
    ensure_uv

    log_info "Running clustering..."
    uv run "$SCRIPT_DIR/cluster.py" "$config" "$@"
}

cmd_pages() {
    local config="${1:-config.json}"
    shift || true
    validate_config "$config"
    ensure_uv

    uv run "$SCRIPT_DIR/export_pages.py" "$config" "$@"
}

cmd_url_clusters() {
    local config="${1:-config.json}"
    shift || true
    validate_config "$config"
    ensure_uv

    uv run "$SCRIPT_DIR/url_clusters.py" "$config" "$@"
}

cmd_cluster_review() {
    local cluster_file="$1"
    shift || true
    ensure_uv

    if [[ -z "$cluster_file" ]] || [[ "$cluster_file" == "config.json" ]]; then
        echo "Usage: ./cli.sh cluster-review <cluster.json> [--top N]"
        echo ""
        echo "View cluster keywords for quick review."
        echo ""
        echo "Example:"
        echo "  ./cli.sh cluster-review /path/to/project/.cache/clusters/0-example.json"
        echo "  ./cli.sh cluster-review /path/to/project/.cache/clusters/5-dictation.json --top 30"
        exit 1
    fi

    if [[ ! -f "$cluster_file" ]]; then
        log_error "File not found: $cluster_file"
        exit 1
    fi

    uv run "$SCRIPT_DIR/cluster_review.py" "$cluster_file" "$@"
}

cmd_cluster_report() {
    local extra_args="$1"
    shift || true
    local cluster_files=("$@")
    ensure_uv

    if [[ ${#cluster_files[@]} -eq 0 ]]; then
        echo "Usage: ./cli.sh cluster-report --config <config.json> <cluster1.json> [cluster2.json ...]"
        echo ""
        echo "View multiple clusters in one report."
        echo ""
        echo "Example:"
        echo "  ./cli.sh cluster-report --config /path/to/config.json 4-dictation.json 5-whisper.json"
        echo "  ./cli.sh cluster-report --config config.json --top 10 0-*.json 1-*.json"
        exit 1
    fi

    uv run "$SCRIPT_DIR/cluster_report.py" $extra_args "${cluster_files[@]}"
}

cmd_strategy_scores() {
    local config="${1:-config.json}"
    validate_config "$config"
    ensure_uv

    log_info "Calculating strategy opportunity scores..."
    uv run "$SCRIPT_DIR/strategy_scores.py" "$config"
}

cmd_run() {
    local config="${1:-config.json}"
    validate_config "$config"

    local project_dir=$(get_project_dir "$config")
    ensure_env_file "$project_dir"

    log_info "Running full pipeline..."
    echo ""

    cmd_fetch "$config"
    echo ""

    cmd_preprocess "$config"
    echo ""

    cmd_embed "$config"
    echo ""

    cmd_cluster "$config"
    echo ""

    log_success "Pipeline complete!"
}

cmd_setup() {
    local config="${1:-config.json}"

    if [[ ! -f "$config" ]]; then
        log_error "Config file not found: $config"
        echo ""
        echo "Create a config.json first, then run setup."
        exit 1
    fi

    local project_dir=$(get_project_dir "$config")
    log_info "Setting up API credentials in $project_dir/.env.local..."

    # This will create/update the file and show instructions
    ensure_env_file "$project_dir" || true

    echo ""
    log_info "Edit $project_dir/.env.local with your credentials, then run your command."
}

cmd_help() {
    cat << EOF
SEO Research CLI

Usage: ./cli.sh <command> [options]

Commands:
    setup       Create/check .env.local with API credentials
    fetch       Fetch keywords from DataForSEO API (--force to re-fetch)
    preprocess  Merge, filter, and calculate scores
    embed       Generate embeddings via OpenRouter
    cluster     Run K-means clustering (--k N to set cluster count)
    cluster-review  View single cluster keywords
    cluster-report  View multiple clusters in one report
    pages       Export competitor pages with keywords for strategy analysis
    url-clusters Show which clusters each URL ranks in
    strategy-scores Calculate opportunity scores for each SEO strategy
    run         Run full pipeline (fetch → preprocess → embed → cluster)
    help        Show this help message

Options:
    --config, -c    Path to config.json (default: config.json)
    --force, -f     Force re-fetch even if cached (for fetch)
    --k N           Set number of clusters (for cluster)
    --domain X      Filter by domain (for pages)
    --top N         Limit keywords per cluster (for cluster-report)

Examples:
    ./cli.sh setup
    ./cli.sh fetch --force
    ./cli.sh cluster --k 100
    ./cli.sh cluster-review /path/to/.cache/clusters/0-example.json
    ./cli.sh cluster-report --config config.json 4-dictation.json 5-whisper.json
    ./cli.sh pages --domain competitor.com
    ./cli.sh strategy-scores --config config.json

API Credentials:
    Stored in .env.local (git-ignored). Run 'setup' to create the file.

    Required keys:
    - DATAFORSEO_LOGIN      DataForSEO email
    - DATAFORSEO_PASSWORD   DataForSEO API password
    - OPENROUTER_API_KEY    OpenRouter API key
EOF
}

# Parse arguments
main() {
    local command="${1:-help}"
    shift || true

    local config="config.json"
    local extra_args=""
    local force_flag=""
    local cluster_files=()

    # Parse options
    while [[ $# -gt 0 ]]; do
        case "$1" in
            --config|-c)
                config="$2"
                shift 2
                ;;
            --k)
                extra_args="$extra_args --k $2"
                shift 2
                ;;
            --force|-f)
                force_flag="--force"
                shift
                ;;
            --domain)
                extra_args="$extra_args --domain $2"
                shift 2
                ;;
            --top)
                extra_args="$extra_args --top $2"
                shift 2
                ;;
            --url)
                extra_args="$extra_args --url $2"
                shift 2
                ;;
            *)
                # Collect .json files for cluster-report, otherwise treat as config
                if [[ "$1" == *.json ]]; then
                    if [[ "$command" == "cluster-report" ]]; then
                        cluster_files+=("$1")
                    else
                        config="$1"
                    fi
                fi
                shift
                ;;
        esac
    done

    case "$command" in
        setup)
            cmd_setup "$config"
            ;;
        fetch)
            cmd_fetch "$config" $force_flag
            ;;
        preprocess)
            cmd_preprocess "$config"
            ;;
        embed)
            cmd_embed "$config"
            ;;
        cluster)
            cmd_cluster "$config" $extra_args
            ;;
        pages)
            cmd_pages "$config" $extra_args
            ;;
        url-clusters)
            cmd_url_clusters "$config" $extra_args
            ;;
        cluster-review)
            cmd_cluster_review "$config" $extra_args
            ;;
        cluster-report)
            cmd_cluster_report "$extra_args" "${cluster_files[@]}"
            ;;
        strategy-scores)
            cmd_strategy_scores "$config"
            ;;
        run)
            cmd_run "$config"
            ;;
        help|--help|-h)
            cmd_help
            ;;
        *)
            log_error "Unknown command: $command"
            echo ""
            cmd_help
            exit 1
            ;;
    esac
}

main "$@"
