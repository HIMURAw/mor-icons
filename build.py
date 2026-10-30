"""Mor simge teması: Papirus'tan (macOS tarzı değil), bütün uygulama/klasör/dosya simgeleri mor tonlarda.

    python3 build.py        # ~/.local/share/icons/Mor (+ Mor-Base) üretir
    gsettings set org.gnome.desktop.interface icon-theme Mor

Her rengin açıklığı korunur, tonu mora çekilir (biraz çeşitlilik kalır), griler hafif morlaşır; böylece
simge biçimleri tanınır kalır. Tek renkli (symbolic) panel/araç simgelerine dokunulmaz. Papirus'ta olmayan
kurulu uygulamaların (Flatpak vb.) kendi simgeleri de boyanıp temaya eklenir.
2026-10-13, Umut: "tüm uygulamaların iconlarını mor yap, macOS iconlarını kullanma".
"""
import colorsys
import configparser
import glob
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

from PIL import Image

HOME = Path.home()
# Papirus: a git clone (has Papirus/ and Papirus-Dark/ inside) or the distro package.
SRC = next((d for d in (Path(os.environ.get("PAPIRUS_SRC", HOME / ".local/src/papirus-icon-theme")),
                        HOME / ".local/share/icons", Path("/usr/share/icons"))
            if (d / "Papirus").is_dir() and (d / "Papirus-Dark").is_dir()), None)
if SRC is None:
    sys.exit("Papirus not found: git clone https://github.com/PapirusDevelopmentTeam/papirus-icon-theme "
             "~/.local/src/papirus-icon-theme (or install the papirus-icon-theme package)")
FINAL = HOME / ".local/share/icons"
# Built aside and swapped in at the end: rebuilding in place left every icon broken for minutes.
# Symlinks inside are relative (../Mor-Base/...), so both themes move together.
OUT = FINAL / ".tema-build"
BASE, THEME = "Mor-Base", "Mor"
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "mor-theme"))  # cloned side by side
from tema import current  # noqa: E402  the chosen colour theme (tema-rengi)

PALETTE = current()
GREY = PALETTE["sat"] == 0
HUE = PALETTE["icon_hue"] / 360
ICON_LUM = PALETTE["icon_lum"]    # mid tones darker: a light hue at violet's lightness looks washed out
ICON_SAT = PALETTE["icon_sat"]
SPREAD = 0.12            # asıl tonun ne kadarı kalsın (çeşitlilik)
TINT = {"apps", "places", "mimetypes", "devices", "categories"}

HEX = re.compile(r"#([0-9a-fA-F]{6}|[0-9a-fA-F]{3})\b")


def recolor_rgb(r, g, b):
    h, l, s = colorsys.rgb_to_hls(r, g, b)
    if GREY:                                    # black / white / grey theme: no colour at all
        return colorsys.hls_to_rgb(h, l, 0.0)
    if s < 0.12 or l > 0.97 or l < 0.03:      # gri, beyaz, siyah: hafif morluk
        s2 = 0.18 if 0.03 <= l <= 0.97 else s
        h2 = HUE
    else:
        d = ((h - HUE + 0.5) % 1.0) - 0.5
        h2 = (HUE + d * SPREAD) % 1.0
        s2 = min(1.0, s * 0.85 + 0.12 + ICON_SAT)
        if 0.25 < l < 0.92:
            l *= ICON_LUM
    return colorsys.hls_to_rgb(h2, l, s2)


def recolor_hex(m):
    v = m.group(1)
    if len(v) == 3:
        v = "".join(c * 2 for c in v)
    r, g, b = (int(v[i:i + 2], 16) / 255 for i in (0, 2, 4))
    r, g, b = recolor_rgb(r, g, b)
    return "#%02x%02x%02x" % (round(r * 255), round(g * 255), round(b * 255))


def tint_svg(src, dst):
    text = Path(src).read_text(errors="ignore")
    Path(dst).write_text(HEX.sub(recolor_hex, text))


def tint_png(src, dst):
    im = Image.open(src).convert("RGBA")
    px = im.load()
    cache = {}
    for y in range(im.height):
        for x in range(im.width):
            r, g, b, a = px[x, y]
            if a == 0:
                continue
            key = (r >> 2, g >> 2, b >> 2)
            if key not in cache:
                cache[key] = tuple(round(c * 255) for c in recolor_rgb(r / 255, g / 255, b / 255))
            px[x, y] = (*cache[key], a)
    im.save(dst)


def category(path):
    parts = Path(path).parts
    return parts[-2] if len(parts) >= 2 else ""


def tint_tree(root):
    n = 0
    for dirpath, dirnames, files in os.walk(root):
        if "symbolic" in dirpath or category(os.path.join(dirpath, "x")) not in TINT:
            continue
        for f in files:
            p = os.path.join(dirpath, f)
            if os.path.islink(p) or not f.endswith(".svg") or "symbolic" in f:
                continue
            tint_svg(p, p)
            n += 1
    return n


def copy_themes():
    for name in (BASE, THEME):
        shutil.rmtree(OUT / name, ignore_errors=True)
    shutil.copytree(SRC / "Papirus", OUT / BASE, symlinks=True)
    shutil.copytree(SRC / "Papirus-Dark", OUT / THEME, symlinks=True)
    # Papirus-Dark büyük boyutlarda ../Papirus'a bağlı: yeni tabana çevir.
    for dirpath, dirnames, files in os.walk(OUT / THEME):
        for f in dirnames + files:
            p = os.path.join(dirpath, f)
            if os.path.islink(p):
                t = os.readlink(p)
                if "Papirus/" in t and "Papirus-" not in t:
                    os.unlink(p)
                    os.symlink(t.replace("Papirus/", BASE + "/"), p)
    for name, title in ((BASE, "Mor (taban)"), (THEME, "Mor")):
        idx = OUT / name / "index.theme"
        s = idx.read_text()
        s = re.sub(r"^Name=.*$", f"Name={title}", s, count=1, flags=re.M)
        s = re.sub(r"^Comment=.*$", "Comment=Papirus, mor tonlarda", s, count=1, flags=re.M)
        idx.write_text(s)


# ---------- Papirus'ta olmayan uygulamalar ----------

APP_DIRS = ["/usr/share/applications", str(HOME / ".local/share/applications"), "/var/lib/snapd/desktop/applications",
            "/var/lib/flatpak/exports/share/applications", str(HOME / ".local/share/flatpak/exports/share/applications")]
ICON_ROOTS = [str(HOME / ".local/share/icons/hicolor"), "/usr/share/icons/hicolor",
              "/var/lib/flatpak/exports/share/icons/hicolor", str(HOME / ".local/share/flatpak/exports/share/icons/hicolor")]


def app_icons():
    names = set()
    for d in APP_DIRS:
        for f in glob.glob(d + "/*.desktop"):
            for line in open(f, errors="ignore"):
                if line.startswith("Icon="):
                    names.add(line[5:].strip())
                    break
    return names


def themed(name):
    return any(glob.glob(str(OUT / BASE / f"*/apps/{name}.svg")))


def find_source(name):
    if os.path.isabs(name):
        return name if os.path.exists(name) else None
    for root in ICON_ROOTS:
        p = f"{root}/scalable/apps/{name}.svg"
        if os.path.exists(p):
            return p
    best = None
    for root in ICON_ROOTS:
        for p in glob.glob(f"{root}/*x*/apps/{name}.png"):
            size = int(Path(p).parts[-3].split("x")[0])
            if not best or size > best[0]:
                best = (size, p)
    if best:
        return best[1]
    for ext in (".svg", ".png"):
        p = f"/usr/share/pixmaps/{name}{ext}"
        if os.path.exists(p):
            return p
    return None


def add_fallbacks():
    sc = OUT / THEME / "fallback/scalable/apps"
    bm = OUT / THEME / "fallback/256/apps"
    sc.mkdir(parents=True, exist_ok=True)
    bm.mkdir(parents=True, exist_ok=True)
    done = []
    for name in sorted(app_icons()):
        if themed(name) or name.endswith("-symbolic"):
            continue
        src = find_source(name)
        if not src:
            continue
        base = Path(name).stem if os.path.isabs(name) else name
        try:
            if src.endswith(".svg"):
                tint_svg(src, sc / f"{base}.svg")
            else:
                tint_png(src, bm / f"{base}.png")
            done.append(base)
        except Exception as e:  # bozuk simge: atla
            print("atlandı", name, e, file=sys.stderr)
    idx = OUT / THEME / "index.theme"
    s = idx.read_text()
    s = re.sub(r"^Directories=(.*)$", r"Directories=\1,fallback/scalable/apps,fallback/256/apps", s, count=1, flags=re.M)
    s += ("\n[fallback/scalable/apps]\nContext=Applications\nSize=256\nMinSize=8\nMaxSize=512\nType=Scalable\n"
          "\n[fallback/256/apps]\nContext=Applications\nSize=256\nMinSize=8\nMaxSize=512\nType=Scalable\n")
    idx.write_text(s)
    return done


MARK = "X-Mor-Icon-Override=true"


def override_absolute():
    """Simgeyi dosya yoluyla veren kısayollar (Snap'ler, Resolve...) temayı atlar: kullanıcı kopyası
    (~/.local/share/applications, aynı ad) simgeyi temadaki boyalı adla verir."""
    user = HOME / ".local/share/applications"
    out = []
    for d in APP_DIRS:
        for f in glob.glob(d + "/*.desktop"):
            lines = open(f, errors="ignore").read().splitlines()
            icon = next((l[5:].strip() for l in lines if l.startswith("Icon=")), "")
            if not icon.startswith("/"):
                continue
            stem = Path(f).stem
            candidates = [stem.split("_")[0], stem, Path(icon).stem]
            name = next((c for c in candidates if themed(c)), None)
            if not name:
                name = Path(icon).stem
                if not (glob.glob(str(OUT / THEME / f"fallback/*/apps/{name}.*"))):
                    continue
            new = [f"Icon={name}" if l.startswith("Icon=") else l for l in lines]
            target = user / Path(f).name
            if Path(f).parent == user:
                Path(f).write_text("\n".join(new) + "\n")          # kullanıcının kendi kısayolu: yerinde
            elif not target.exists() or MARK in target.read_text(errors="ignore"):
                if MARK not in new:
                    i = next(i for i, l in enumerate(new) if l.strip() == "[Desktop Entry]")
                    new.insert(i + 1, MARK)
                target.write_text("\n".join(new) + "\n")
            else:
                continue
            out.append(f"{Path(f).name}->{name}")
    subprocess.run(["update-desktop-database", "-q", str(user)])
    return out


def colored_small_places(root):
    """Papirus'ta 16px klasörler panel gibi tek renkli; dosya yöneticisinin küçük listesinde
    Windows Gezgini gibi renkli görünsün diye 22px'in renkli klasörleri 16px'e konuyor."""
    n = 0
    for size in ("16x16", "16x16@2x"):
        src = root / size.replace("16x16", "22x22") / "places"
        dst = root / size / "places"
        if not src.is_dir() or not dst.is_dir():
            continue
        for f in dst.glob("*.svg"):
            if f.name.endswith("-symbolic.svg") or not (src / f.name).exists():
                continue
            s = src / f.name
            if f.is_symlink() or f.exists():
                f.unlink()
            f.write_bytes(s.resolve().read_bytes())
            n += 1
    return n


def swap_in():
    for name in (BASE, THEME):
        old = FINAL / f".tema-old-{name}"
        shutil.rmtree(old, ignore_errors=True)
        if (FINAL / name).exists():
            (FINAL / name).rename(old)
        (OUT / name).rename(FINAL / name)
        shutil.rmtree(old, ignore_errors=True)
        subprocess.run(["gtk-update-icon-cache", "-q", "-f", str(FINAL / name)])


if __name__ == "__main__":
    shutil.rmtree(OUT, ignore_errors=True)
    OUT.mkdir(parents=True)
    copy_themes()
    n = tint_tree(OUT / BASE) + tint_tree(OUT / THEME)
    extra = add_fallbacks()
    print("renkli 16px klasör:", colored_small_places(OUT / THEME))
    swap_in()
    OUT = FINAL  # the functions below look at the installed theme now
    print("yol yerine ad:", ", ".join(override_absolute()))
    print(f"boyanan svg: {n}, Papirus'ta olmayan uygulama: {len(extra)} -> {', '.join(extra[:40])}")
