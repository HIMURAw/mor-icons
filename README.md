# Mor icons

[Papirus](https://github.com/PapirusDevelopmentTeam/papirus-icon-theme) recoloured to match the
[Mor theme](https://github.com/HIMURAw/mor-theme). Every app, folder and file icon keeps its
lightness and shape and takes the theme's hue, with a little of its own colour left so icons
stay easy to tell apart. Symbolic (single colour) panel icons are left alone. Installed apps
that Papirus does not cover (Flatpaks and so on) get their own icon tinted and added.

It follows `tema-rengi`: switch the desktop to turquoise, green, blue or grey and the icons
are rebuilt in that colour.

<!-- screenshot: the GNOME app grid or a Nautilus window in the Mor violet icon theme, folders and app icons clearly visible, a few windows of the same colour theme behind it -->

## Easiest install

Through [himura-desktop](https://github.com/HIMURAw/himura-desktop), which sets up the icons
together with the theme:

```bash
curl -fsSL https://raw.githubusercontent.com/HIMURAw/himura-desktop/main/install.sh | bash -s -- theme
```

## Install by hand

```bash
git clone https://github.com/HIMURAw/mor-theme ~/.local/src/mor-theme
git clone https://github.com/HIMURAw/mor-icons ~/.local/src/mor-icons
git clone --depth 1 https://github.com/PapirusDevelopmentTeam/papirus-icon-theme ~/.local/src/papirus-icon-theme
python3 ~/.local/src/mor-icons/build.py      # about 34,000 icons, 2-3 minutes
gsettings set org.gnome.desktop.interface icon-theme Mor
```

Requirements:

- Python 3 with Pillow
- Papirus. `build.py` looks for a folder holding both `Papirus` and `Papirus-Dark` in this
  order: `$PAPIRUS_SRC` (default `~/.local/src/papirus-icon-theme`), `~/.local/share/icons`,
  `/usr/share/icons`. So a distro `papirus-icon-theme` package works instead of the clone.
- [mor-theme](https://github.com/HIMURAw/mor-theme) cloned next to this folder
  (`~/.local/src/mor-theme`). The build imports its `tema.py` to learn the chosen colour.

## What the build does

The build takes 2-3 minutes. It:

1. Copies Papirus into `Mor-Base` and Papirus-Dark into `Mor`, in a staging folder
   (`~/.local/share/icons/.tema-build`).
2. Recolours the SVGs in the apps, places, mimetypes, devices and categories folders. It
   reads the colour theme from `~/.config/tema/current.json` (violet if there is none).
3. Tints and adds icons of installed apps (read from the `.desktop` files, including Snap
   and Flatpak ones) that Papirus lacks.
4. Gives the small 16 px folder icons the coloured 22 px look, so file lists are not
   single-coloured.
5. Swaps the finished theme in, so icons are not broken while it builds, and updates the
   icon cache.
6. For launchers that point to an icon by file path (some Snap and third-party apps), makes a
   copy in `~/.local/share/applications/` that uses the recoloured icon name. Those copies
   carry the line `X-Mor-Icon-Override=true`. If you already have your own launcher with a
   file-path icon in that folder, its `Icon=` line is changed in place.

It writes to `~/.local/share/icons/Mor` and `~/.local/share/icons/Mor-Base`. It does not
select the theme itself; the `gsettings` command above does that.

## Following `tema-rengi`

`tema-rengi` (from the Mor theme) runs this build in the background after a colour change,
then switches the icon theme to Adwaita and back to Mor so the new colours show, and sends a
notification. To skip it, use `tema-rengi <theme> --no-icons`. To rebuild by hand after
changing the colour, just run `python3 ~/.local/src/mor-icons/build.py` again.

## Undo

```bash
gsettings reset org.gnome.desktop.interface icon-theme
rm -rf ~/.local/share/icons/Mor ~/.local/share/icons/Mor-Base
```

Launcher copies made in step 6 stay in `~/.local/share/applications/`. To list them:
`grep -l X-Mor-Icon-Override=true ~/.local/share/applications/*.desktop`, and delete those
files. If you installed through himura-desktop, `./uninstall.sh theme` takes the icons out
with the theme.

## License

GPL-3.0, like Papirus. See [LICENSE](LICENSE).
