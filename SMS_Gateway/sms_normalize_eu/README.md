# sms-normalize-eu

SMSTools3 **checkhandler** to normalize `To:` into **E.164** for EU/EEA/UK.

## Install

```bash
sudo cp sms-normalize-eu.sh /usr/local/bin/
sudo chmod +x /usr/local/bin/sms-normalize-eu.sh
sudo sed -i 's|^checkhandler *=.*|checkhandler = /usr/local/bin/sms-normalize-eu.sh|' /etc/smsd.conf
# or add the line if missing
```

Optional default country (fallback when a number cannot be classified):
```bash
sudo sh -c 'echo "DEFAULT_CC=+44" > /etc/default/sms-normalize-eu'
echo 'export DEFAULT_CC=+44' | sudo tee -a /etc/environment >/dev/null
```

> The script already defaults to `+44` if `DEFAULT_CC` is not provided. Change inside the script if needed.

## Behavior
- Accepts: `+CC...`, `00CC...`, `CCCC...` (bare country code), and national formats per-country (07… for UK, 8… for LT, 0… for most EU).
- Rewrites the first `To:` header in the file passed by SMSTools3.
- Heuristics prioritize correctness and avoid double-prefix issues (e.g. `4407...` → `+4407...`, not `+44407...`).

## Countries covered
UK, LT, DE, FR, IT, ES, NL, BE, IE, PT, PL, RO, CZ, SK, AT, DK, SE, NO, FI, CH, HU, LV, EE, GR, BG, SI, HR, BA, RS, ME, MK, UA, BY, CY, MT, LU, IS, AL, MD, LI.

## Disclaimer
This is a best-effort heuristic for modems. For perfect accuracy, use a full numbering library (e.g., libphonenumber) in your upstream app and pass E.164 to SMSTools3.
