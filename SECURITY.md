# Security Policy

## Supported versions
| Version | Supported |
|---|---|
| 3.x | ✅ |
| < 3.0 | ❌ |

## Reporting a vulnerability
The toolkit runs local scripts and invokes external tools: KiCad, Java/Freerouting and ImageMagick.

If you find an issue such as unsafe handling of untrusted design files, command injection through file names, or an unsafe download, **do not open a public issue**. Use GitHub's private vulnerability reporting instead (Security tab → *Report a vulnerability*).

Expect an acknowledgement within 7 days.

## Safety note on hardware
This skill gives engineering guidance and generates draft CAD. It is **not** a substitute for review by a qualified engineer. For mains, high-voltage, high-energy, battery, medical, automotive or aerospace designs, follow the governing standards and get the design independently reviewed and certified.
