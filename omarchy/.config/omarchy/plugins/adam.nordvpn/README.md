# NordVPN dependencies

- Python 3
- NetworkManager and `nmcli`
- `secret-tool` from libsecret
- Zenity
- A NetworkManager VPN profile whose UUID is configured as `connectionUuid`
  in `~/.config/omarchy/shell.json`

The plugin stores no credentials or credential environment variables. It keeps
the VPN password in the desktop secret service.
