"""HTML autónomo y comprobaciones de layout, movimiento y bucle."""

import base64
import copy
import json
import logging

from .settings import ROOT

LOGGER = logging.getLogger(__name__)


def write_preview(script, output, settings, audio_path=None):
    try:
        payload = copy.deepcopy(script)
        payload["layout"] = settings.layout()
        if audio_path:
            payload["audio"] = "data:audio/wav;base64," + base64.b64encode(
                audio_path.read_bytes()).decode("ascii")
        html = (ROOT / "content/reels/phishing-myth-v3.html").read_text(encoding="utf-8")
        html = html.replace("__REEL_DATA__", json.dumps(payload, ensure_ascii=False)
                            .replace("<", "\\u003c"))
        for token, name in (("SPACE", "space-grotesk-latin.woff2"),
                            ("OSWALD", "oswald-latin.woff2")):
            font = ROOT / "content/reels/fonts" / name
            if not font.is_file():
                # Checkout anterior a la copia de fuentes; no depende de Vite ni de red.
                font = ROOT.parent / "cyberpulse-templates/public/fonts" / name
            html = html.replace(f"__{token}_FONT__", "data:font/woff2;base64," +
                                base64.b64encode(font.read_bytes()).decode("ascii"))
        target = output / "preview.html"
        target.write_text(html, encoding="utf-8")
        caption = script["caption"]
        missing = [url for url in script["sources"] if url not in caption]
        if missing:
            caption += "\n\nFuentes:\n" + "\n".join(missing)
        hashtags = script.get("hashtags", [])
        if hashtags:
            caption += "\n\n" + " ".join(hashtags)
        (output / "caption.txt").write_text(caption, encoding="utf-8")
        return target
    except (OSError, KeyError, TypeError):
        LOGGER.error("No se pudo construir la plantilla local o su caption")
        raise


def validate_visuals(page, script, settings):
    """Comprueba todos los bloques y hojas de texto cada cuarto de segundo."""
    duration = sum(s["duration"] for s in script["scenes"])
    try:
        samples = 0
        for quarter in range(int(duration * 4) + 1):
            t = min(quarter / 4, duration)
            page.evaluate("t => window.renderAt(t)", t)
            issues = page.evaluate("""({top,bottom}) => {
                const stage=document.querySelector('#stage').getBoundingClientRect();
                const visible=el=>el.getClientRects().length &&
                    getComputedStyle(el).visibility!=='hidden';
                const checks=[...document.querySelectorAll('[data-safe]')];
                // También mide las hojas internas: un contenedor no detecta texto desbordado.
                checks.push(...[...document.querySelectorAll('#stage *')].filter(el=>
                    [...el.childNodes].some(n=>n.nodeType===3&&n.textContent.trim())));
                const problems=[];
                for(const el of new Set(checks)) if(visible(el)){
                    const r=el.getBoundingClientRect();
                    if(r.top-stage.top<top-.5||r.bottom-stage.top>bottom+.5||
                       r.left<stage.left||r.right>stage.right||
                       el.scrollWidth>el.clientWidth+1||el.scrollHeight>el.clientHeight+1)
                        problems.push(el.id||el.className||el.tagName);
                }
                const c=document.querySelector('#cursor'),link=document.querySelector('#link');
                if(visible(c)&&visible(link)){
                    const a=c.getBoundingClientRect(),b=link.getBoundingClientRect();
                    if(a.left<b.right&&a.right>b.left&&a.top<b.bottom&&a.bottom>b.top)
                        problems.push('cursor-over-link');
                }
                const text=document.querySelector('#stage').innerText;
                if(text.includes('Fuentes:')||text.includes('SIN VOZ'))problems.push('fixed-source-bar');
                return problems;
            }""", settings.layout())
            if issues:
                raise ValueError(f"Layout inseguro en {t:.2f}s: {issues}")
            samples += 1
        page.evaluate("window.renderAt(0)")
        first = page.locator("#stage").screenshot()
        page.evaluate("t => window.renderAt(t)", duration - 1 / settings.fps)
        last = page.locator("#stage").screenshot()
        if first != last:
            raise ValueError("El último fotograma no coincide con el inicial")
        # Cada ventana de 1.5s contiene un cambio de movimiento, también dentro de escenas.
        for half in range(int((duration - 1.5) * 2)):
            t = half / 2
            states = []
            for moment in (t, t + .375, t + .75, t + 1.125):
                page.evaluate("t => window.renderAt(t)", moment)
                states.append(page.evaluate("""() => ['phone','floating','icon','save'].map(id=>{
                    const el=document.getElementById(id);return [el.style.transform,
                    el.getClientRects().length?1:0];})"""))
            if all(s == states[0] for s in states[1:]):
                raise ValueError(f"Ventana estática de 1.5s en {t}s")
        return {"timeline_samples": samples, "safe_layout": settings.layout(),
                "loop_frame_equal": True, "max_static_window_seconds": 1.5}
    except Exception:
        LOGGER.error("Falló la comprobación visual del reel")
        raise
