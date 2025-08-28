# Home Assistant Configuration

This repository contains my Home Assistant configuration files, automations, and custom components.

## 🏠 Overview

My Home Assistant setup includes:
- **Configuration**: Main configuration files and packages
- **Automations**: Time-based and device-triggered automations
- **Custom Components**: MQTT Media Player integration
- **Themes**: Custom frontend themes
- **Scripts & Scenes**: Automation scripts and scene configurations

## 📁 File Structure

```
├── configuration.yaml          # Main configuration file
├── automations.yaml           # Automation definitions
├── hue_scene_selector.yaml    # Hue scene selector package
├── custom_components/         # Custom integrations
│   └── mqtt_media_player/    # MQTT Media Player component
├── themes/                    # Frontend themes
├── scripts.yaml              # Script definitions
├── scenes.yaml               # Scene definitions
├── groups.yaml               # Group definitions
└── README.md                 # This file
```

## 🔧 Configuration Details

### Core Features
- **Packages**: Modular configuration using packages
- **Frontend**: Custom themes and JavaScript modules
- **Panel iframe**: Webtop integration
- **HTTP**: Reverse proxy configuration for external access
- **Sensors**: Time and date sensors

### Integrations
- **Hue**: Scene selector and lighting control
- **MQTT**: Custom media player component
- **FFmpeg**: Media processing
- **Time/Date**: Time-based automations

## 🚀 Getting Started

1. Clone this repository to your Home Assistant configuration directory
2. Ensure all required integrations are installed
3. Restart Home Assistant
4. Check the logs for any configuration errors

## ⚠️ Security Notes

- This configuration includes external access configurations
- Review and adjust trusted proxies for your network
- Consider using environment variables for sensitive information

## 🤝 Contributing

Feel free to submit issues or pull requests if you find any problems or have suggestions for improvements.

## 📝 License

This configuration is shared for educational purposes. Use at your own risk and always backup your existing configuration before making changes.

---

*Last updated: August 2025*