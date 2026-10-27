# Mor icons

[Papirus](https://github.com/PapirusDevelopmentTeam/papirus-icon-theme) recoloured to the
[Mor](https://github.com/HIMURAw/mor-theme) violet: every app, folder and file icon keeps
its lightness and shape and takes the theme's hue, with a little of its own colour left so
icons stay easy to tell apart. Symbolic (single colour) panel icons are left alone. Apps
that Papirus does not cover (Flatpaks and so on) get their own icon tinted and added.

It follows `tema-rengi`: switch the desktop to turquoise, green, blue or grey and the icons
are rebuilt in that colour.

Part of [himura-desktop](https://github.com/HIMURAw/himura-desktop).

## Build

```bash
git clone https://github.com/HIMURAw/mor-theme ~/.local/src/mor-theme
git clone https://github.com/HIMURAw/mor-icons ~/.local/src/mor-icons
git clone --depth 1 https://github.com/PapirusDevelopmentTeam/papirus-icon-theme ~/.local/src/papirus-icon-theme
python3 ~/.local/src/mor-icons/build.py      # ~34k icons, 2-3 minutes
gsettings set org.gnome.desktop.interface icon-theme Mor
```

Needs Python 3 with Pillow. A distro `papirus-icon-theme` package works instead of the clone.
The result goes to `~/.local/share/icons/Mor` (and `Mor-Base`).

## License

GPL-3.0, like Papirus.
