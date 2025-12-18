# Notes for third party software

## `mitmproxy` for proxying API's

[mitmproxy.org](https://mitmproxy.org/)

- `sudo apt install mitmproxy`
- open http://mitm.it/ which should list options to install certs. If not, try routing all network traffic through a proxy on your system:
  - turn proxy on and select manual
  - enter `localhost` for both http and https
- turn off the proxy
- use this command to listen create a proxy for any URL:
  - `mitmproxy --mode reverse:https://your-app-url.com`
