#!/bin/bash

# Persistent Skull Animation System - All-in-One
# Auto-starts on boot, respawns when closed, shows on SSH
# Only stops with secret phrase: "unknone hart"

SCRIPT_PATH="$(readlink -f "$0")"
SCRIPT_DIR="$HOME/.skull_animation"
STOP_FLAG="$SCRIPT_DIR/.stop"
ENABLED_FLAG="$SCRIPT_DIR/.enabled"
PID_FILE="$SCRIPT_DIR/.manager.pid"
MODE="${1:-auto}"

# ============================================================================
# INSTALLATION FUNCTION
# ============================================================================
install_system() {
    echo "╔════════════════════════════════════════════════════╗"
    echo "║                                                    ║"
    echo "║     Persistent Skull Animation System Setup        ║"
    echo "║                                                    ║"
    echo "╚════════════════════════════════════════════════════╝"
    echo ""
    
    # Create directory
    mkdir -p "$SCRIPT_DIR"
    
    # Copy this script to the installation directory
    INSTALLED_SCRIPT="$SCRIPT_DIR/skull_animation.sh"
    cp "$SCRIPT_PATH" "$INSTALLED_SCRIPT"
    chmod +x "$INSTALLED_SCRIPT"
    
    # Add to bashrc
    if ! grep -q "skull_animation.sh" "$HOME/.bashrc" 2>/dev/null; then
        echo "" >> "$HOME/.bashrc"
        echo "# Persistent Skull Animation System" >> "$HOME/.bashrc"
        echo "if [ -f \"$INSTALLED_SCRIPT\" ]; then" >> "$HOME/.bashrc"
        echo "    \"$INSTALLED_SCRIPT\" startup &" >> "$HOME/.bashrc"
        echo "fi" >> "$HOME/.bashrc"
    fi
    
    # Add to .profile for graphical logins
    if ! grep -q "skull_animation.sh" "$HOME/.profile" 2>/dev/null; then
        echo "" >> "$HOME/.profile"
        echo "# Persistent Skull Animation System" >> "$HOME/.profile"
        echo "if [ -f \"$INSTALLED_SCRIPT\" ]; then" >> "$HOME/.profile"
        echo "    \"$INSTALLED_SCRIPT\" startup &" >> "$HOME/.profile"
        echo "fi" >> "$HOME/.profile"
    fi
    
    # Create convenience commands
    mkdir -p "$HOME/.local/bin"
    echo "#!/bin/bash" > "$HOME/.local/bin/stop-skull"
    echo "$INSTALLED_SCRIPT stop" >> "$HOME/.local/bin/stop-skull"
    chmod +x "$HOME/.local/bin/stop-skull"
    
    # Enable and start
    touch "$ENABLED_FLAG"
    rm -f "$STOP_FLAG"
    
    echo "✓ Installation complete!"
    echo ""
    echo "Starting animation system..."
    "$INSTALLED_SCRIPT" startup &
    
    echo ""
    echo "The skull animation will now:"
    echo "  • Start automatically on system boot"
    echo "  • Reopen when you close the terminal"
    echo "  • Show on SSH connections"
    echo ""
    echo "To stop permanently, run: stop-skull"
    echo "(You'll need to type 'unknone hart' to confirm)"
    echo ""
}

# ============================================================================
# SKULL ANIMATION FUNCTION
# ============================================================================
show_skull_animation() {
    # Hide cursor
    tput civis
    
    # Cleanup function
    cleanup() {
        tput cnorm
        clear
        exit 0
    }
    
    trap cleanup INT TERM
    
    # Skull laughing frames
    SKULL_LAUGH_1='
          ___________
         /           \\
        /   O     O   \\
       |               |
       |    \\_____/    |
       |   HAHAHAHA!   |
        \\             /
         \\___________/
            |     |
            |     |
    '
    
    SKULL_LAUGH_2='
          ___________
         /           \\
        /   ^     ^   \\
       |               |
       |    \\_____/    |
       |   HAHAHA!!    |
        \\             /
         \\___________/
            |     |
            |     |
    '
    
    # Skull crying frames
    SKULL_CRY_1='
          ___________
         /           \\
        /   T     T   \\
       |      ...      |
       |    _______    |
       |   BOO HOO!    |
        \\             /
         \\___________/
            |     |
            |     |
    '
    
    SKULL_CRY_2='
          ___________
         /           \\
        /   ;     ;   \\
       |      ...      |
       |    _______    |
       |   *sob sob*   |
        \\             /
         \\___________/
            |     |
            |     |
    '
    
    # Colors
    RED='\033[1;31m'
    BLUE='\033[1;34m'
    CYAN='\033[1;36m'
    YELLOW='\033[1;33m'
    MAGENTA='\033[1;35m'
    WHITE='\033[1;37m'
    RESET='\033[0m'
    
    counter=0
    
    while true; do
        # Check if stop flag exists
        if [ -f "$STOP_FLAG" ]; then
            cleanup
        fi
        
        # Get terminal size
        ROWS=$(tput lines)
        COLS=$(tput cols)
        
        # Clear screen
        clear
        
        # Determine which animation to show (laugh for 3 seconds, cry for 3 seconds)
        cycle=$((counter / 15))
        is_laughing=$((cycle % 2))
        
        # Select frame
        frame_num=$((counter % 10))
        
        if [ $is_laughing -eq 0 ]; then
            # Laughing animation
            if [ $((frame_num % 2)) -eq 0 ]; then
                skull="$SKULL_LAUGH_1"
                color="$RED"
            else
                skull="$SKULL_LAUGH_2"
                color="$YELLOW"
            fi
        else
            # Crying animation
            if [ $((frame_num % 2)) -eq 0 ]; then
                skull="$SKULL_CRY_1"
                color="$BLUE"
            else
                skull="$SKULL_CRY_2"
                color="$CYAN"
            fi
        fi
        
        # Calculate starting row to center vertically
        skull_height=11
        start_row=$(( (ROWS - skull_height) / 2 ))
        
        # Print skull centered
        row=$start_row
        while IFS= read -r line; do
            # Calculate column to center line
            line_length=${#line}
            start_col=$(( (COLS - line_length) / 2 ))
            
            tput cup $row $start_col
            echo -e "${color}${line}${RESET}"
            ((row++))
        done <<< "$skull"
        
        # Add hint at bottom
        tput cup $((ROWS - 2)) 0
        echo -e "${WHITE}╔════════════════════════════════════════════════════════════════╗${RESET}"
        tput cup $((ROWS - 1)) 0
        echo -e "${WHITE}║  To stop permanently, run: stop-skull (type 'unknone hart')   ║${RESET}"
        
        # Increment counter
        ((counter++))
        
        # Animation speed
        sleep 0.2
    done
}

# ============================================================================
# MANAGER FUNCTION (Keeps respawning terminals)
# ============================================================================
run_manager() {
    # Store PID
    echo $$ > "$PID_FILE"
    
    # Function to launch terminal
    launch_terminal() {
        local script="$SCRIPT_DIR/skull_animation.sh"
        
        # Try different terminal emulators
        if command -v gnome-terminal &> /dev/null; then
            gnome-terminal -- bash -c "$script animate; exec bash" &
        elif command -v xterm &> /dev/null; then
            xterm -e "bash -c '$script animate; exec bash'" &
        elif command -v konsole &> /dev/null; then
            konsole -e bash -c "$script animate; exec bash" &
        elif command -v xfce4-terminal &> /dev/null; then
            xfce4-terminal -e "bash -c '$script animate; exec bash'" &
        elif command -v mate-terminal &> /dev/null; then
            mate-terminal -e "bash -c '$script animate; exec bash'" &
        elif command -v terminator &> /dev/null; then
            terminator -e "bash -c '$script animate; exec bash'" &
        elif command -v alacritty &> /dev/null; then
            alacritty -e bash -c "$script animate; exec bash" &
        fi
    }
    
    # Main loop
    while true; do
        # Check if stop flag exists
        if [ -f "$STOP_FLAG" ]; then
            rm -f "$PID_FILE"
            rm -f "$ENABLED_FLAG"
            exit 0
        fi
        
        # Check if enabled
        if [ ! -f "$ENABLED_FLAG" ]; then
            sleep 1
            continue
        fi
        
        # Count running animations
        animation_count=$(pgrep -f "skull_animation.sh animate" | wc -l)
        
        # If no animation running, launch new terminal
        if [ "$animation_count" -eq 0 ]; then
            launch_terminal
        fi
        
        # Check every 2 seconds
        sleep 2
    done
}

# ============================================================================
# STOP FUNCTION (with dialog requiring "unknone hart")
# ============================================================================
stop_animation() {
    clear
    echo "╔════════════════════════════════════════════════════╗"
    echo "║                                                    ║"
    echo "║          STOP SKULL ANIMATION PERMANENTLY          ║"
    echo "║                                                    ║"
    echo "║  To stop the animation system permanently,         ║"
    echo "║  type the secret phrase below:                     ║"
    echo "║                                                    ║"
    echo "╚════════════════════════════════════════════════════╝"
    echo ""
    echo -n "Enter secret phrase: "
    read -r input
    
    if [ "$input" = "unknone hart" ]; then
        # Create stop flag
        touch "$STOP_FLAG"
        
        # Kill all processes
        pkill -f "skull_animation.sh animate"
        pkill -f "skull_animation.sh manager"
        
        # Remove enabled flag
        rm -f "$ENABLED_FLAG"
        
        echo ""
        echo "✓ Skull animation system stopped permanently!"
        echo "✓ It will not run on startup anymore."
        echo ""
        echo "To re-enable, run: $SCRIPT_DIR/skull_animation.sh start"
        echo ""
    else
        echo ""
        echo "✗ Incorrect phrase. Animation continues."
        echo ""
        exit 1
    fi
}

# ============================================================================
# START FUNCTION (re-enable)
# ============================================================================
start_animation() {
    rm -f "$STOP_FLAG"
    touch "$ENABLED_FLAG"
    
    # Start manager if not running
    if ! pgrep -f "skull_animation.sh manager" > /dev/null; then
        nohup "$SCRIPT_DIR/skull_animation.sh" manager > /dev/null 2>&1 &
    fi
    
    echo "✓ Skull animation system enabled!"
    echo "✓ Animation will run on startup and reopen when closed."
    echo ""
}

# ============================================================================
# STARTUP FUNCTION (runs on login)
# ============================================================================
startup_animation() {
    # Check if stop flag exists
    if [ -f "$STOP_FLAG" ]; then
        return
    fi
    
    # Create enabled flag
    touch "$ENABLED_FLAG"
    
    # Start manager if not running
    if ! pgrep -f "skull_animation.sh manager" > /dev/null; then
        nohup "$SCRIPT_DIR/skull_animation.sh" manager > /dev/null 2>&1 &
    fi
    
    # If SSH connection, show animation in current terminal
    if [ -n "$SSH_CONNECTION" ] || [ -n "$SSH_CLIENT" ]; then
        "$SCRIPT_DIR/skull_animation.sh" animate
    fi
}

# ============================================================================
# MAIN DISPATCHER
# ============================================================================

case "$MODE" in
    install)
        install_system
        ;;
    animate)
        show_skull_animation
        ;;
    manager)
        run_manager
        ;;
    stop)
        stop_animation
        ;;
    start)
        start_animation
        ;;
    startup)
        startup_animation
        ;;
    *)
        # If run without arguments, show menu
        echo "Persistent Skull Animation System"
        echo ""
        echo "Usage: $0 [command]"
        echo ""
        echo "Commands:"
        echo "  install  - Install the animation system"
        echo "  animate  - Show the skull animation"
        echo "  manager  - Run the background manager"
        echo "  stop     - Stop the animation (requires 'unknone hart')"
        echo "  start    - Re-enable the animation"
        echo "  startup  - Initialize on login (auto-called)"
        echo ""
        echo "Quick start:"
        echo "  $0 install"
        echo ""
        ;;
esac
