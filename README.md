<div align="center">
    <img src="data/icons/hicolor/scalable/apps/org.vanillaos.ControlCenter.svg" height="64">
    <h1>Vanilla OS Control Center</h1>
    <p>This utility is meant to be used in <a href="https://github.com/vanilla-os">Vanilla OS</a> 
    to manage its components (ABroot, VSO, Apx) and drivers via ubuntu-drivers-common.</p><br>
    <p><b>This project is deprecated, see <a href="https://vanillaos.org/2023/07/05/vanilla-os-orchid-devlog.html">this post</a> for more information.</b></p>
    <hr />
</a>
    <br />
    <img src="data/screenshot.png">
</div>


## Build
### Dependencies
- build-essential
- meson
- libadwaita-1-dev
- gettext
- desktop-file-utils
- vte4

### Build
```bash
meson build
ninja -C build
```

### Install
```bash
sudo ninja -C build install
```

## Run
```bash
vanilla-control-center
```

## Use of Generative AI

Maintainers may use generative AI tools as assistants while working on vanilla-control-center. Non-trivial assisted commits disclose the tool, model, and scope of the work.

AI tools may assist with code comments, documentation, repetitive code, and issue triage. Maintainers make project decisions and review every assisted change before it is merged.

Use these trailers for non-trivial assisted commits:

```plain
Assisted-by: <tool>:<model-version>
AI-Scope: <what the tool generated and the prompt or a short prompt summary>
```

Single-line completions, renames, and formatting changes do not need trailers.

Coding agents must also follow [AGENTS.md](AGENTS.md) before changing files,
creating commits, or opening pull requests.
