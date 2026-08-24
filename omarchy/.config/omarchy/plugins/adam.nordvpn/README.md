# NordVPN dependencies

- Python 3
- NetworkManager and `nmcli`
- `secret-tool` from libsecret
- Zenity
- At least one NordVPN OpenVPN profile imported into NetworkManager

The plugin stores no credentials or credential environment variables. It keeps
the VPN password in the desktop secret service. It automatically uses the only
NordVPN profile, prefers an active profile, or presents a selector when multiple
inactive profiles are available. `connectionUuid` remains available as an
optional widget setting to select a fixed profile.
