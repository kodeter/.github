# .github

Community health files and the public profile for the Kodeter organization.

| Path | Purpose |
|---|---|
| `profile/README.md` | Renders on [github.com/kodeter](https://github.com/kodeter) |
| `images/banner.png` | Header image for the organization profile page |
| `images/profile.png` | Organization avatar, uploaded through the org settings page |
| `tools/brand/generate.py` | Regenerates the two images above |

The banner is 2000x1000 (2:1) and the avatar is 512x512. Regenerate them with:

```bash
cd tools/brand
python3 generate.py
```

Palette, typography, and layout notes live in `docs/design/brand-assets.md` in the working copy of this project.
