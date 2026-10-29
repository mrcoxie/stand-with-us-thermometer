# Stand With Us — live goal thermometer

Stream overlay for the "Stand With Nolan Wells' Targeted Friends" GiveSendGo campaign.

- `index.html` — the thermometer. Add it to OBS, Streamlabs, StreamYard or Restream as a Browser Source / overlay URL at 400 x 1000. Transparent background.
- `data.json` — the current total. A GitHub Action (`.github/workflows/update.yml`) re-reads the GiveSendGo page every 5 minutes and updates this file; the overlay re-reads it every 20 seconds.
- Options on the URL: `?interval=30`, `?bg=navy`, `?status=0`, `?demo=1`, `?raised=…&goal=…&donors=…` to pin figures by hand.
