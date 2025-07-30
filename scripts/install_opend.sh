#!/bin/bash

# OpenD Installation Helper Script

echo "======================================"
echo "OpenD Installation Guide"
echo "======================================"
echo ""
echo "OpenD is moomoo's API gateway that must be running for the bot to work."
echo ""

# Detect OS
OS="Unknown"
if [[ "$OSTYPE" == "darwin"* ]]; then
    OS="macOS"
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    OS="Linux"
elif [[ "$OSTYPE" == "msys" || "$OSTYPE" == "cygwin" ]]; then
    OS="Windows"
fi

echo "Detected OS: $OS"
echo ""

case $OS in
    "macOS")
        echo "Installation steps for macOS:"
        echo "1. Visit: https://www.moomoo.com/download/OpenAPI"
        echo "2. Download 'moomoo OpenD macOS' version"
        echo "3. Open the downloaded DMG file"
        echo "4. Drag OpenD.app to your Applications folder"
        echo "5. Launch OpenD.app from Applications"
        echo "6. You should see 'API Ready' status when it's running"
        echo ""
        echo "To run OpenD:"
        echo "- Open Applications folder and double-click OpenD.app"
        echo "- Or from terminal: open -a OpenD"
        ;;
        
    "Linux")
        echo "Installation steps for Linux:"
        echo "1. Visit: https://www.moomoo.com/download/OpenAPI"
        echo "2. Download 'moomoo OpenD Linux' version"
        echo "3. Extract the tar.gz file:"
        echo "   tar -xzf moomoo_OpenD_xxx.tar.gz"
        echo "4. Navigate to the extracted directory"
        echo "5. Run: ./OpenD"
        echo ""
        echo "Make sure to install required dependencies:"
        echo "   sudo apt-get install libssl-dev  # For Ubuntu/Debian"
        echo "   sudo yum install openssl-devel   # For CentOS/RHEL"
        ;;
        
    "Windows")
        echo "Installation steps for Windows:"
        echo "1. Visit: https://www.moomoo.com/download/OpenAPI"
        echo "2. Download 'moomoo OpenD Windows' version"
        echo "3. Extract the ZIP file to a folder (e.g., C:\\OpenD)"
        echo "4. Run OpenD.exe from the extracted folder"
        echo "5. You should see 'API Ready' status when it's running"
        echo ""
        echo "Note: You may need to allow OpenD through Windows Firewall"
        ;;
        
    *)
        echo "Unable to detect OS. Please visit:"
        echo "https://www.moomoo.com/download/OpenAPI"
        echo "And download the appropriate version for your system."
        ;;
esac

echo ""
echo "======================================"
echo "Important Notes:"
echo "======================================"
echo "- OpenD must be running before starting the trading bot"
echo "- Default connection is localhost:11111"
echo "- You should see 'API Ready' in OpenD when it's running correctly"
echo "- If you have connection issues, check your firewall settings"
echo ""

# Open download page if possible
if command -v open &> /dev/null; then
    echo "Press Enter to open the download page in your browser..."
    read
    open "https://www.moomoo.com/download/OpenAPI"
elif command -v xdg-open &> /dev/null; then
    echo "Press Enter to open the download page in your browser..."
    read
    xdg-open "https://www.moomoo.com/download/OpenAPI"
fi