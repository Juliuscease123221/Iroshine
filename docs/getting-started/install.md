# Install

iroshine needs Python 3.10 or newer, [Manim](https://docs.manim.community/en/stable/installation.html)
(installed for you), and two system tools that Manim relies on: **FFmpeg** and the **Cairo / Pango**
drawing libraries.

## 1. System tools

=== "macOS"

    ```bash
    brew install cairo pango ffmpeg pkg-config
    ```

=== "Windows"

    Install [FFmpeg](https://ffmpeg.org/download.html) and make sure `ffmpeg` runs in a terminal.
    Manim's Windows wheels bundle Cairo and Pango, so nothing else is needed. If Manim fails to
    install, follow the [Manim installation guide](https://docs.manim.community/en/stable/installation.html).

=== "Linux (Debian / Ubuntu)"

    ```bash
    sudo apt install build-essential python3-dev libcairo2-dev libpango1.0-dev ffmpeg
    ```

## 2. iroshine

```bash
git clone https://github.com/Juliuscease123221/Iroshine.git
cd Iroshine
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -e .
```

`pip install -e .` installs Manim and NumPy and makes `import iroshine` work from any folder.

## 3. Fonts (optional)

The defaults use **Inter** and **IBM Plex Mono**, both free from
[Google Fonts](https://fonts.google.com/). If they are missing, text falls back to a system font and
everything still renders.

## 4. Check it works

```bash
cd examples
python 00_start_here.py low
```

That writes `00_start_here.mp4`, a small draft, in well under a minute. Next:
[your first video](first-video.md).
