#!/bin/bash
###############################################################################
# LTE 4G Configuration
# Controls EC25 modem internet backup behavior
###############################################################################

# Master switch - Set to OFF to completely disable 4G (power saving, modem issues)
# ON: 4G interface available for backup
# OFF: 4G completely disabled, no routes
LTE_4G_ENABLED=ON

# Failover mode - Controls how failover works
# OFF: Passive mode - 4G route always present (metric 999), Linux chooses automatically
# ON: Active mode - Script actively manages routes, adds/removes based on WiFi/LAN status
LTE_4G_FAILOVER=OFF

###############################################################################
# Do not modify below this line
###############################################################################
export LTE_4G_ENABLED
export LTE_4G_FAILOVER
