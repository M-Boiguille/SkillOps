#!/bin/bash
#
# SkillOps Cron Setup Script
#
# This script helps you set up SkillOps to run automatically via cron.
# Run this script to interactively configure a daily SkillOps execution.
#
# Usage: bash setup/cron/install.sh
#

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Helper functions
print_header() {
    echo -e "\n${BLUE}=== $1 ===${NC}\n"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

# Check prerequisites
check_requirements() {
    print_header "Checking Prerequisites"
    
    # Check if skillops is installed
    if ! command -v skillops &> /dev/null; then
        print_error "SkillOps not found in PATH"
        echo "Please install SkillOps first: pip install skillops"
        exit 1
    fi
    
    print_success "SkillOps found: $(which skillops)"
    
    # Check if crontab is available
    if ! command -v crontab &> /dev/null; then
        print_error "crontab not found"
        echo "Your system may not support cron jobs (e.g., WSL1, Docker containers)"
        exit 1
    fi
    
    print_success "Crontab is available"
}

# Get user input
get_user_input() {
    print_header "Configuration"
    
    # Get home directory
    HOME_DIR="$HOME"
    print_success "Home directory: $HOME_DIR"
    
    # Get SkillOps installation path
    SKILLOPS_PATH=$(which skillops)
    print_success "SkillOps path: $SKILLOPS_PATH"
    
    # Ask for schedule time
    echo -e "${YELLOW}What time should SkillOps run daily?${NC}"
    echo "Examples: 8:00, 09:30, 20:00 (24-hour format)"
    read -p "Enter time [08:00]: " SCHEDULE_TIME
    SCHEDULE_TIME="${SCHEDULE_TIME:-08:00}"
    
    # Parse hours and minutes
    HOUR=$(echo $SCHEDULE_TIME | cut -d: -f1)
    MINUTE=$(echo $SCHEDULE_TIME | cut -d: -f2)
    
    # Validate time
    if ! [[ $HOUR =~ ^[0-9]{1,2}$ ]] || ! [[ $MINUTE =~ ^[0-9]{1,2}$ ]]; then
        print_error "Invalid time format. Please use HH:MM"
        exit 1
    fi
    
    if [ $HOUR -gt 23 ] || [ $MINUTE -gt 59 ]; then
        print_error "Invalid time values"
        exit 1
    fi
    
    print_success "Scheduled time: $HOUR:$(printf "%02d" $MINUTE)"
    
    # Ask for email notifications
    echo -e "\n${YELLOW}Enable email notifications on failure?${NC}"
    read -p "Enter email (or 'no' to skip) [no]: " EMAIL_ADDR
    
    # Ask for environment file
    echo -e "\n${YELLOW}Where are your SkillOps environment variables?${NC}"
    read -p "Enter path [$HOME_DIR/.config/skillops/skillops.env]: " ENV_FILE
    ENV_FILE="${ENV_FILE:-$HOME_DIR/.config/skillops/skillops.env}"
    
    # Ask for log location
    echo -e "\n${YELLOW}Where should cron logs be saved?${NC}"
    read -p "Enter log file path [$HOME_DIR/.local/share/skillops/cron.log]: " LOG_FILE
    LOG_FILE="${LOG_FILE:-$HOME_DIR/.local/share/skillops/cron.log}"
    
    print_success "Configuration saved"
}

# Create cron command
create_cron_command() {
    print_header "Creating Cron Entry"
    
    # Create log directory if needed
    LOG_DIR=$(dirname "$LOG_FILE")
    mkdir -p "$LOG_DIR"
    print_success "Log directory created: $LOG_DIR"
    
    # Build cron command
    if [ -f "$ENV_FILE" ]; then
        # Use environment file if it exists
        CRON_CMD="source $ENV_FILE && $SKILLOPS_PATH start"
    else
        CRON_CMD="$SKILLOPS_PATH start"
    fi
    
    # Add logging
    CRON_CMD="$CRON_CMD >> $LOG_FILE 2>&1"
    
    # Add email if specified
    if [ "$EMAIL_ADDR" != "no" ] && [ -n "$EMAIL_ADDR" ]; then
        CRON_CMD="($CRON_CMD) || echo 'SkillOps failed on $(date)' | mail -s 'SkillOps Cron Error' $EMAIL_ADDR"
    fi
    
    # Create cron schedule (minute hour * * *)
    CRON_SCHEDULE="$MINUTE $HOUR * * * $CRON_CMD"
    
    print_success "Cron command created"
    echo -e "\n${BLUE}Cron Entry:${NC}"
    echo "$CRON_SCHEDULE"
}

# Add to crontab
add_to_crontab() {
    print_header "Installing Cron Job"
    
    # Get current crontab
    CURRENT_CRONTAB=$(crontab -l 2>/dev/null || echo "")
    
    # Check if already installed
    if echo "$CURRENT_CRONTAB" | grep -q "skillops"; then
        print_warning "SkillOps cron job already exists"
        read -p "Replace existing entry? (y/n) [n]: " REPLACE
        
        if [ "$REPLACE" != "y" ]; then
            print_error "Installation cancelled"
            exit 1
        fi
        
        # Remove old entry
        echo "$CURRENT_CRONTAB" | grep -v "skillops" | crontab -
        print_success "Removed existing SkillOps cron job"
    fi
    
    # Add new entry
    (echo "$CURRENT_CRONTAB"; echo "$CRON_SCHEDULE") | crontab -
    
    print_success "SkillOps cron job installed"
}

# Verify installation
verify_installation() {
    print_header "Verifying Installation"
    
    # Check if installed
    if crontab -l 2>/dev/null | grep -q "skillops"; then
        print_success "Cron job is installed"
        
        # Show next runs
        echo -e "\n${BLUE}Your SkillOps cron job:${NC}"
        crontab -l | grep skillops
        
        # Show log file location
        echo -e "\n${BLUE}Logs will be saved to:${NC}"
        echo "$LOG_FILE"
        
        # Show how to view logs
        echo -e "\n${BLUE}To view logs:${NC}"
        echo "  tail -f $LOG_FILE"
        
        return 0
    else
        print_error "Cron job not found"
        return 1
    fi
}

# Remove installation
uninstall() {
    print_header "Uninstalling Cron Job"
    
    if crontab -l 2>/dev/null | grep -q "skillops"; then
        crontab -l | grep -v "skillops" | crontab -
        print_success "SkillOps cron job removed"
    else
        print_warning "No SkillOps cron job found"
    fi
}

# Manual configuration
show_manual_config() {
    print_header "Manual Cron Configuration"
    
    echo "If you prefer to edit your crontab manually:"
    echo ""
    echo "1. Open your crontab editor:"
    echo "   crontab -e"
    echo ""
    echo "2. Add one of these lines:"
    echo ""
    echo "   # Basic (no env file):"
    echo "   0 8 * * * /usr/local/bin/skillops start >> ~/.local/share/skillops/cron.log 2>&1"
    echo ""
    echo "   # With environment file:"
    echo "   0 8 * * * source ~/.config/skillops/skillops.env && /usr/local/bin/skillops start >> ~/.local/share/skillops/cron.log 2>&1"
    echo ""
    echo "   # With error notifications (email):"
    echo "   0 8 * * * source ~/.config/skillops/skillops.env && /usr/local/bin/skillops start >> ~/.local/share/skillops/cron.log 2>&1 || echo 'Failed' | mail -s 'SkillOps Error' user@example.com"
    echo ""
    echo "3. Save and exit"
    echo ""
    echo "Cron Schedule Format:"
    echo "  ┌───────────── minute (0 - 59)"
    echo "  │ ┌───────────── hour (0 - 23)"
    echo "  │ │ ┌───────────── day of month (1 - 31)"
    echo "  │ │ │ ┌───────────── month (1 - 12)"
    echo "  │ │ │ │ ┌───────────── day of week (0 - 6, 0=Sunday)"
    echo "  │ │ │ │ │"
    echo "  │ │ │ │ │"
    echo "  0 8 * * * command"
    echo ""
    echo "Common examples:"
    echo "  0 8 * * * — Every day at 8:00 AM"
    echo "  0 20 * * * — Every day at 8:00 PM"
    echo "  0 9 * * 1 — Every Monday at 9:00 AM"
    echo "  */15 * * * * — Every 15 minutes"
    echo ""
}

# Main menu
show_menu() {
    print_header "SkillOps Cron Setup"
    
    echo "1. Install SkillOps cron job (interactive)"
    echo "2. Manual cron configuration"
    echo "3. Show current cron jobs"
    echo "4. Remove SkillOps cron job"
    echo "5. Exit"
    echo ""
    read -p "Select option [1]: " CHOICE
    CHOICE="${CHOICE:-1}"
    
    case $CHOICE in
        1)
            check_requirements
            get_user_input
            create_cron_command
            add_to_crontab
            verify_installation
            ;;
        2)
            show_manual_config
            ;;
        3)
            print_header "Current Cron Jobs"
            crontab -l || echo "No cron jobs found"
            ;;
        4)
            uninstall
            ;;
        5)
            echo "Goodbye!"
            exit 0
            ;;
        *)
            print_error "Invalid option"
            exit 1
            ;;
    esac
}

# Run menu
show_menu
