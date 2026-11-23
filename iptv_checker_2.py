import concurrent.futures
import ctypes
from datetime import datetime, timedelta, timezone
import gzip
import json
import math
import os
import re
import shutil
import socket
import ssl
import subprocess
import sys
import threading
import time
import tkinter as tk
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from tkinter import filedialog, messagebox, ttk


SECA_M3U_URL = "https://raw.githubusercontent.com/secagratis/Lista-Rai-IPTV/refs/heads/main/MIX.M3U"
VASSEL81_M3U_URL = "https://raw.githubusercontent.com/Vassel81/iptv-italia-personale/refs/heads/main/italia-unificata.m3u"
PLUTO_M3U_URL = "https://raw.githubusercontent.com/secagratis/Lista-Rai-IPTV/refs/heads/main/Pluto.m3u"
PLUTO_EPG_URL = "https://i.mjh.nz/PlutoTV/it.xml"
IPTV_ORG_M3U_URL = "https://iptv-org.github.io/iptv/index.m3u"
TVITAVA_M3U_URL = "https://raw.githubusercontent.com/bbb0six/tvitava/refs/heads/main/tvv.m3u8"
RAKUTEN_M3U_URL = "https://raw.githubusercontent.com/iptv-org/iptv/refs/heads/master/streams/it_rakuten.m3u"
RAKUTEN_EPG_URL = "https://i.mjh.nz/Roku/all.xml"

DEFAULT_M3U_URL = SECA_M3U_URL

DEFAULT_EPG_URLS = [
    "https://iptv-epg.org/files/epg-it.xml.gz",
    "https://iptv-epg.org/files/epg-ch.xml.gz",
]


COUNTRY_MAP = {
    "IT": "IT - Italia",
    "ITA": "IT - Italia",
    "ITALY": "IT - Italia",
    "ITALIA": "IT - Italia",
    "UK": "UK - Regno Unito",
    "GB": "UK - Regno Unito",
    "GBR": "UK - Regno Unito",
    "ENGLAND": "UK - Regno Unito",
    "US": "US - USA",
    "USA": "US - USA",
    "UNITED STATES": "US - USA",
    "FR": "FR - Francia",
    "FRA": "FR - Francia",
    "FRANCE": "FR - Francia",
    "FRANCIA": "FR - Francia",
    "DE": "DE - Germania",
    "GER": "DE - Germania",
    "GERMANY": "DE - Germania",
    "GERMANIA": "DE - Germania",
    "ES": "ES - Spagna",
    "ESP": "ES - Spagna",
    "SPAIN": "ES - Spagna",
    "SPAGNA": "ES - Spagna",
    "CH": "CH - Svizzera",
    "SWITZERLAND": "CH - Svizzera",
    "SVIZZERA": "CH - Svizzera",
    "AT": "AT - Austria",
    "AUSTRIA": "AT - Austria",
    "PT": "PT - Portogallo",
    "PORTUGAL": "PT - Portogallo",
    "PORTOGALLO": "PT - Portogallo",
    "NL": "NL - Paesi Bassi",
    "NETHERLANDS": "NL - Paesi Bassi",
    "BE": "BE - Belgio",
    "BELGIUM": "BE - Belgio",
    "RO": "RO - Romania",
    "ROMANIA": "RO - Romania",
    "AL": "AL - Albania",
    "ALBANIA": "AL - Albania",
    "GR": "GR - Grecia",
    "GREECE": "GR - Grecia",
    "TR": "TR - Turchia",
    "TURKEY": "TR - Turchia",
    "RU": "RU - Russia",
    "RUSSIA": "RU - Russia",
    "CA": "CA - Canada",
    "CANADA": "CA - Canada",
    "BR": "BR - Brasile",
    "BRAZIL": "BR - Brasile",
    "AR": "AR - Argentina",
    "ARGENTINA": "AR - Argentina",
    "INT": "INT - Internazionale",
    "INTERNATIONAL": "INT - Internazionale",
}

THEMES = {
    "light": {
        "bg": "#f0f4f9",
        "card_bg": "#ffffff",
        "header_bg": "#1e293b",
        "header_fg": "#ffffff",
        "header_sub": "#94a3b8",
        "fg": "#1e293b",
        "muted": "#64748b",
        "border": "#cbd5e1",
        "entry_bg": "#ffffff",
        "entry_fg": "#0f172a",
        "tree_bg": "#ffffff",
        "tree_alt": "#f8fafc",
        "tree_fg": "#1e293b",
        "tree_head_bg": "#e2e8f0",
        "tree_head_fg": "#0f172a",
        "tree_sel_bg": "#2563eb",
        "tree_sel_fg": "#ffffff",
        "accent": "#2563eb",
        "accent_hover": "#1d4ed8",
        "success": "#16a34a",
        "success_hover": "#15803d",
        "danger": "#dc2626",
        "danger_hover": "#b91c1c",
        "warning": "#d97706",
        "warning_hover": "#b45309",
        "neutral_btn": "#e2e8f0",
        "neutral_btn_fg": "#1e293b",
        "neutral_btn_hover": "#cbd5e1",
        "tag_online": "#15803d",
        "tag_offline": "#dc2626",
        "tag_pending": "#64748b",
        "tag_rec": "#d97706",
        "tag_wait": "#2563eb",
    },
    "dark": {
        "bg": "#0f172a",
        "card_bg": "#1e293b",
        "header_bg": "#020617",
        "header_fg": "#f8fafc",
        "header_sub": "#94a3b8",
        "fg": "#f1f5f9",
        "muted": "#94a3b8",
        "border": "#334155",
        "entry_bg": "#0f172a",
        "entry_fg": "#f8fafc",
        "tree_bg": "#1e293b",
        "tree_alt": "#162032",
        "tree_fg": "#f1f5f9",
        "tree_head_bg": "#0f172a",
        "tree_head_fg": "#e2e8f0",
        "tree_sel_bg": "#3b82f6",
        "tree_sel_fg": "#ffffff",
        "accent": "#3b82f6",
        "accent_hover": "#2563eb",
        "success": "#22c55e",
        "success_hover": "#16a34a",
        "danger": "#ef4444",
        "danger_hover": "#dc2626",
        "warning": "#f59e0b",
        "warning_hover": "#d97706",
        "neutral_btn": "#334155",
        "neutral_btn_fg": "#f1f5f9",
        "neutral_btn_hover": "#475569",
        "tag_online": "#4ade80",
        "tag_offline": "#f87171",
        "tag_pending": "#94a3b8",
        "tag_rec": "#fbbf24",
        "tag_wait": "#60a5fa",
    },
}


def get_app_base_dir():
    if getattr(sys, "frozen", False):
        return os.path.dirname(os.path.abspath(sys.executable))
    return os.path.dirname(os.path.abspath(__file__))


def get_bundled_bin_dir():
    if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
        return sys._MEIPASS
    return get_app_base_dir()


def detect_country(extinf, group_title, name, url):
    if extinf:
        m_country = re.search(r'tvg-country\s*=\s*"([^"]+)"', extinf, re.IGNORECASE)
        if m_country:
            raw = m_country.group(1).strip()
            if raw:
                return COUNTRY_MAP.get(raw.upper(), raw.upper())

    if group_title:
        gt_clean = group_title.strip()
        gt_up = gt_clean.upper()
        if gt_up in COUNTRY_MAP:
            return COUNTRY_MAP[gt_up]
        for code, label in COUNTRY_MAP.items():
            if len(code) >= 2 and re.search(rf'(?:^|[\s\|\-:/\[\(]){re.escape(code)}(?:$|[\s\|\-:/\]\)])', gt_up):
                return label

    if name:
        m_prefix = re.match(r'^[\[\(\{]?\s*([A-Za-z]{2,3})\s*[\]\)\}]?\s*[:\|\-\s]', name.strip())
        if m_prefix:
            code = m_prefix.group(1).upper()
            if code in COUNTRY_MAP:
                return COUNTRY_MAP[code]

        m_suffix = re.search(r'[\[\(]\s*([A-Za-z]{2,3})\s*[\]\)]\s*$', name.strip())
        if m_suffix:
            code = m_suffix.group(1).upper()
            if code in COUNTRY_MAP:
                return COUNTRY_MAP[code]

        name_up = name.upper()
        for kw, label in [
            ("ITALIA", "IT - Italia"),
            ("MEDIASET", "IT - Italia"),
            ("RAI ", "IT - Italia"),
            ("SKY SPORT", "IT - Italia"),
            ("LA7", "IT - Italia"),
            ("TV8", "IT - Italia"),
            ("NOVE", "IT - Italia"),
        ]:
            if kw in name_up:
                return label

    if url:
        low_url = url.lower()
        if any(k in low_url for k in ("mediaset", "rai.it", "la7.it", "/it/", ".it/")):
            return "IT - Italia"
        m_path = re.search(r'/([a-z]{2})/', low_url)
        if m_path:
            code = m_path.group(1).upper()
            if code in COUNTRY_MAP:
                return COUNTRY_MAP[code]

    return "N/D"


def normalize_key(text):
    if not text:
        return ""
    return re.sub(r"[^a-z0-9]", "", text.lower())


def smart_channel_key(text):
    if not text:
        return ""
    s = text.lower().strip()
    s = re.sub(r'^[\[\(\{]?\s*[a-z]{2,3}\s*[\]\)\}]?\s*[:\|\-\s]+', '', s)
    s = re.sub(
        r'\b(fhd|uhd|4k|hd|sd|hq|lq|hevc|h265|h264|1080p|720p|576p|480p|50fps|25fps|backup|alt|vip|raw|ita|italia|24h|live|plus|eventi|sky)\b',
        ' ',
        s,
    )
    return re.sub(r"[^a-z0-9]", "", s)


def parse_hls_quality(manifest_text):
    if not manifest_text:
        return ""
    best_h = 0
    best_bw = 0
    for line in manifest_text.splitlines():
        if line.startswith("#EXT-X-STREAM-INF"):
            m_res = re.search(r"RESOLUTION\s*=\s*(\d+)x(\d+)", line, re.IGNORECASE)
            if m_res:
                h = int(m_res.group(2))
                if h > best_h:
                    best_h = h
            m_bw = re.search(r"BANDWIDTH\s*=\s*(\d+)", line, re.IGNORECASE)
            if m_bw:
                bw = int(m_bw.group(1))
                if bw > best_bw:
                    best_bw = bw
    if best_h > 0:
        if best_h >= 2160:
            return "4K (2160p)"
        return f"{best_h}p"
    if best_bw > 0:
        mbps = best_bw / 1_000_000.0
        return f"HLS {mbps:.1f}M"
    return ""


def sanitize_filename(name):
    cleaned = re.sub(r'[\\/*?:"<>|]', "_", name or "registrazione")
    cleaned = re.sub(r"\s+", "_", cleaned).strip("_")
    return cleaned[:65] or "registrazione"


def format_duration(seconds):
    seconds = max(0, int(seconds))
    hrs, rem = divmod(seconds, 3600)
    mins, secs = divmod(rem, 60)
    if hrs > 0:
        return f"{hrs:02d}:{mins:02d}:{secs:02d}"
    return f"{mins:02d}:{secs:02d}"


def parse_xmltv_datetime(dt_str):
    if not dt_str:
        return None
    s = dt_str.strip()
    m = re.match(r"^(\d{14})(?:\s*([+-]\d{4}))?$", s)
    if not m:
        return None
    base, offset = m.group(1), m.group(2)
    try:
        dt = datetime.strptime(base, "%Y%m%d%H%M%S")
        if offset:
            sign = 1 if offset[0] == "+" else -1
            hrs = int(offset[1:3])
            mins = int(offset[3:5])
            tz = timezone(sign * timedelta(hours=hrs, minutes=mins))
            return dt.replace(tzinfo=tz).astimezone()
        return dt.astimezone()
    except Exception:
        return None


def update_extinf_line(extinf, new_name, new_tvg_id):
    base = extinf.strip() if extinf else "#EXTINF:-1,"
    if "," in base:
        header_part, _ = base.split(",", 1)
    else:
        header_part = base

    if re.search(r'tvg-id\s*=\s*"[^"]*"', header_part, re.IGNORECASE):
        if new_tvg_id:
            header_part = re.sub(
                r'tvg-id\s*=\s*"[^"]*"',
                f'tvg-id="{new_tvg_id}"',
                header_part,
                count=1,
                flags=re.IGNORECASE,
            )
        else:
            header_part = re.sub(r'\s*tvg-id\s*=\s*"[^"]*"', "", header_part, count=1, flags=re.IGNORECASE)
    elif new_tvg_id:
        header_part = f'{header_part} tvg-id="{new_tvg_id}"'

    return f"{header_part},{new_name}"


class IPTVCheckerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("IPTV Studio Pro — Validator, Editor EPG, Player & Timer Recorder")
        self.root.geometry("1480x850")
        self.root.minsize(1200, 700)

        self.config_path = os.path.join(get_app_base_dir(), "iptv_studio_config.json")
        self.saved_cfg = self._load_config()

        self.theme_mode = self.saved_cfg.get("theme_mode", "light")
        if self.theme_mode not in THEMES:
            self.theme_mode = "light"

        self.styled_buttons = []
        self.card_frames = []
        self.themed_labels = []
        self.themed_entries = []

        self.default_ua = (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/130.0.0.0 Safari/537.36"
        )

        self.ssl_ctx = ssl.create_default_context()
        self.ssl_ctx.check_hostname = False
        self.ssl_ctx.verify_mode = ssl.CERT_NONE

        self.ffprobe_semaphore = threading.Semaphore(3)

        self.channels = []
        self.uid_counter = 0
        self.m3u_header_epg = ""
        self.epg_channels = {}
        self.epg_name_to_id = {}
        self.epg_smart_to_id = {}
        self.epg_programmes = {}

        self.is_running = False
        self.stop_requested = False
        self.check_session_id = 0

        self.ui_lock = threading.Lock()
        self.pending_updates = []
        self.completed_count = 0
        self.total_targets = 0
        self.scan_finished_flag = False

        self.active_recordings = {}
        self.rec_counter = 0
        self.rec_poll_scheduled = False
        self.rec_manager_win = None
        self.rec_manager_tree = None

        self.embed_proc = None
        self.embed_hwnd = None
        self.embed_channel_name = ""
        self.embed_muted = False
        self.embed_poll_scheduled = False

        self.style = ttk.Style(self.root)
        try:
            self.style.theme_use("clam")
        except Exception:
            pass

        self._build_ui()
        self._restore_saved_settings()
        self._auto_detect_player()
        self._refresh_ffmpeg_badge()
        self._apply_theme()
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)

        self.root.after(250, self._startup_auto_load)

    def _load_config(self):
        try:
            if os.path.isfile(self.config_path):
                with open(self.config_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    if isinstance(data, dict):
                        return data
        except Exception:
            pass
        return {}

    def _collect_pending_timers_for_save(self):
        timers = []
        now = time.time()
        for rec in self.active_recordings.values():
            if rec["state"] == "WAITING" and rec["scheduled_start"] > now:
                timers.append(
                    {
                        "channel_name": rec["channel_name"],
                        "prog_title": rec["prog_title"],
                        "file_path": rec["file_path"],
                        "scheduled_start": rec["scheduled_start"],
                        "duration_minutes": max(1, int(rec["limit_seconds"] // 60)) if rec["limit_seconds"] > 0 else 60,
                    }
                )
        return timers

    def _save_config(self):
        data = {
            "theme_mode": self.theme_mode,
            "m3u_source": self.file_path_var.get().strip(),
            "epg_source": self.epg_source_var.get().strip(),
            "rec_folder": self.rec_folder_var.get().strip(),
            "player_type": self.player_type_var.get(),
            "player_exe": self.player_exe_var.get().strip(),
            "timeout": int(self.timeout_var.get()),
            "workers": int(self.workers_var.get()),
            "deep_check": bool(self.deep_check_var.get()),
            "probe_quality": bool(self.probe_quality_var.get()),
            "volume": int(self.volume_var.get()) if hasattr(self, "volume_var") else 80,
            "scheduled_timers": self._collect_pending_timers_for_save(),
        }
        try:
            with open(self.config_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception:
            pass

    def _restore_saved_settings(self):
        saved_m3u = self.saved_cfg.get("m3u_source", "").strip()
        if saved_m3u and saved_m3u != "[Lista incollata]":
            self.file_path_var.set(saved_m3u)
        else:
            self.file_path_var.set(DEFAULT_M3U_URL)

        saved_epg = self.saved_cfg.get("epg_source", "").strip()
        if saved_epg:
            self.epg_source_var.set(saved_epg)
        else:
            self.epg_source_var.set(", ".join(DEFAULT_EPG_URLS))

        if self.saved_cfg.get("rec_folder"):
            self.rec_folder_var.set(self.saved_cfg["rec_folder"])
        if self.saved_cfg.get("player_type") in ("vlc", "ffplay"):
            self.player_type_var.set(self.saved_cfg["player_type"])
        if "timeout" in self.saved_cfg:
            self.timeout_var.set(max(2, min(30, int(self.saved_cfg["timeout"]))))
        if "workers" in self.saved_cfg:
            self.workers_var.set(max(1, min(30, int(self.saved_cfg["workers"]))))
        if "deep_check" in self.saved_cfg:
            self.deep_check_var.set(bool(self.saved_cfg["deep_check"]))
        if "probe_quality" in self.saved_cfg:
            self.probe_quality_var.set(bool(self.saved_cfg["probe_quality"]))
        if "volume" in self.saved_cfg and hasattr(self, "volume_var"):
            self.volume_var.set(max(0, min(100, int(self.saved_cfg["volume"]))))

    def _restore_saved_timers(self):
        raw_timers = self.saved_cfg.get("scheduled_timers") or []
        now = time.time()
        valid_timers = [
            t
            for t in raw_timers
            if isinstance(t, dict)
            and t.get("channel_name")
            and t.get("file_path")
            and float(t.get("scheduled_start", 0)) > now
        ]
        if not valid_timers:
            return

        if not messagebox.askyesno(
            "Ripristina Timer Salvati",
            f"Trovati {len(valid_timers)} timer futuri salvati nella sessione precedente.\n"
            "Vuoi riattivarli automaticamente?",
        ):
            return

        for t in valid_timers:
            ch = next(
                (c for c in self.channels if normalize_key(c["name"]) == normalize_key(t["channel_name"])),
                None,
            )
            if not ch:
                continue
            sched_ts = float(t["scheduled_start"])
            mins = max(1, int(t.get("duration_minutes", 60)))
            out_path = t["file_path"]
            if any(os.path.abspath(r["file_path"]) == os.path.abspath(out_path) for r in self.active_recordings.values()):
                continue

            self.rec_counter += 1
            rec_id = self.rec_counter
            rec_info = {
                "id": rec_id,
                "ch_uid": ch["uid"],
                "channel_name": ch["name"],
                "prog_title": t.get("prog_title", ""),
                "file_path": out_path,
                "state": "WAITING",
                "scheduled_start": sched_ts,
                "start_time": sched_ts,
                "limit_seconds": mins * 60,
                "stop_event": threading.Event(),
                "timer_expired": False,
                "proc": None,
            }
            self.active_recordings[rec_id] = rec_info
            threading.Thread(
                target=self._record_worker,
                args=(rec_info, dict(ch), self._find_ffmpeg()),
                daemon=True,
            ).start()
            self._update_channel_row_visual(ch)

        if self.active_recordings and not self.rec_poll_scheduled:
            self.rec_poll_scheduled = True
            self.root.after(500, self._poll_recording_status)
        self._update_rec_controls_ui()
        self._update_stats()

    def _startup_auto_load(self):
        m3u_src = self.file_path_var.get().strip()
        if m3u_src:
            if m3u_src.lower().startswith(("http://", "https://")):
                self._load_m3u_from_url(silent=True)
            elif os.path.isfile(m3u_src):
                try:
                    with open(m3u_src, "r", encoding="utf-8", errors="replace") as f:
                        self._parse_m3u_content(f.read(), preserve_epg_box=True)
                except Exception:
                    pass

        epg_src = self.epg_source_var.get().strip()
        if epg_src:
            self._start_epg_load(silent=True)

        self.root.after(600, self._restore_saved_timers)

    def _make_btn(self, parent, text, command, kind="neutral", width=None, state=tk.NORMAL, padx=11, pady=5):
        btn = tk.Button(
            parent,
            text=text,
            command=command,
            relief=tk.FLAT,
            bd=0,
            cursor="hand2",
            font=("Segoe UI", 9, "bold" if kind != "neutral" else "normal"),
            padx=padx,
            pady=pady,
            state=state,
        )
        if width:
            btn.config(width=width)
        btn._btn_kind = kind
        self.styled_buttons.append(btn)

        def on_enter(_e):
            if str(btn["state"]) != tk.DISABLED:
                t = THEMES[self.theme_mode]
                hover_map = {
                    "accent": t["accent_hover"],
                    "success": t["success_hover"],
                    "danger": t["danger_hover"],
                    "warning": t["warning_hover"],
                    "neutral": t["neutral_btn_hover"],
                }
                btn.config(bg=hover_map.get(btn._btn_kind, t["neutral_btn_hover"]))

        def on_leave(_e):
            self._style_single_button(btn)

        btn.bind("<Enter>", on_enter)
        btn.bind("<Leave>", on_leave)
        self._style_single_button(btn)
        return btn

    def _style_single_button(self, btn):
        t = THEMES[self.theme_mode]
        kind = getattr(btn, "_btn_kind", "neutral")
        if str(btn["state"]) == tk.DISABLED:
            btn.config(bg=t["neutral_btn"], fg=t["muted"])
            return
        bg_map = {
            "accent": (t["accent"], "#ffffff"),
            "success": (t["success"], "#ffffff"),
            "danger": (t["danger"], "#ffffff"),
            "warning": (t["warning"], "#ffffff"),
            "neutral": (t["neutral_btn"], t["neutral_btn_fg"]),
        }
        bg, fg = bg_map.get(kind, (t["neutral_btn"], t["neutral_btn_fg"]))
        btn.config(bg=bg, fg=fg, activebackground=bg, activeforeground=fg)

    def _toggle_theme(self):
        self.theme_mode = "dark" if self.theme_mode == "light" else "light"
        self.theme_btn.config(text="☀️ Tema Chiaro" if self.theme_mode == "dark" else "🌙 Tema Scuro")
        self._apply_theme()
        self._refresh_tree()

    def _apply_theme(self):
        t = THEMES[self.theme_mode]
        self.root.configure(bg=t["bg"])

        self.header_banner.config(bg=t["header_bg"])
        self.title_box.config(bg=t["header_bg"])
        self.header_right_box.config(bg=t["header_bg"])
        self.header_title_lbl.config(bg=t["header_bg"], fg=t["header_fg"])
        self.header_sub_lbl.config(bg=t["header_bg"], fg=t["header_sub"])

        for cf in self.card_frames:
            cf.config(bg=t["card_bg"], highlightbackground=t["border"], highlightthickness=1)

        for lbl, role in self.themed_labels:
            bg = t["card_bg"] if role != "bg" else t["bg"]
            fg = t["muted"] if role == "muted" else t["fg"]
            if isinstance(lbl, tk.Frame):
                lbl.config(bg=bg)
            else:
                lbl.config(bg=bg, fg=fg)

        for ent in self.themed_entries:
            ent.config(
                bg=t["entry_bg"],
                fg=t["entry_fg"],
                insertbackground=t["entry_fg"],
                highlightbackground=t["border"],
                highlightcolor=t["accent"],
                highlightthickness=1,
                relief=tk.FLAT,
            )

        if hasattr(self, "video_stage"):
            self.video_stage.config(bg="#050811")
        if hasattr(self, "video_placeholder_lbl"):
            self.video_placeholder_lbl.config(bg="#050811", fg="#94a3b8")
        if hasattr(self, "embed_now_lbl"):
            self.embed_now_lbl.config(bg=t["card_bg"], fg=t["fg"])
        if hasattr(self, "vol_scale"):
            self.vol_scale.config(bg=t["card_bg"], fg=t["fg"], troughcolor=t["neutral_btn"], highlightthickness=0)

        for btn in self.styled_buttons:
            self._style_single_button(btn)

        self.style.configure("TFrame", background=t["bg"])
        self.style.configure("Card.TFrame", background=t["card_bg"])
        self.style.configure("TLabel", background=t["card_bg"], foreground=t["fg"], font=("Segoe UI", 9))
        self.style.configure("Bg.TLabel", background=t["bg"], foreground=t["fg"], font=("Segoe UI", 9))
        self.style.configure("TRadiobutton", background=t["card_bg"], foreground=t["fg"], font=("Segoe UI", 9))
        self.style.map("TRadiobutton", background=[("active", t["card_bg"])])
        self.style.configure("TCheckbutton", background=t["card_bg"], foreground=t["fg"], font=("Segoe UI", 9))
        self.style.map("TCheckbutton", background=[("active", t["card_bg"])])

        self.style.configure(
            "Treeview",
            background=t["tree_bg"],
            fieldbackground=t["tree_bg"],
            foreground=t["tree_fg"],
            rowheight=26,
            borderwidth=0,
            font=("Segoe UI", 9),
        )
        self.style.configure(
            "Treeview.Heading",
            background=t["tree_head_bg"],
            foreground=t["tree_head_fg"],
            relief="flat",
            font=("Segoe UI", 9, "bold"),
            padding=(6, 6),
        )
        self.style.map(
            "Treeview",
            background=[("selected", t["tree_sel_bg"])],
            foreground=[("selected", t["tree_sel_fg"])],
        )
        self.style.map("Treeview.Heading", background=[("active", t["border"])])

        self.style.configure(
            "Modern.Horizontal.TProgressbar",
            troughcolor=t["neutral_btn"],
            background=t["accent"],
            borderwidth=0,
            thickness=10,
        )

        self.tree.tag_configure("ONLINE", foreground=t["tag_online"], background=t["tree_bg"])
        self.tree.tag_configure("ONLINE_ALT", foreground=t["tag_online"], background=t["tree_alt"])
        self.tree.tag_configure("OFFLINE", foreground=t["tag_offline"], background=t["tree_bg"])
        self.tree.tag_configure("OFFLINE_ALT", foreground=t["tag_offline"], background=t["tree_alt"])
        self.tree.tag_configure("PENDING", foreground=t["tag_pending"], background=t["tree_bg"])
        self.tree.tag_configure("PENDING_ALT", foreground=t["tag_pending"], background=t["tree_alt"])
        self.tree.tag_configure("RECORDING", foreground=t["tag_rec"], background=t["tree_bg"])
        self.tree.tag_configure("RECORDING_ALT", foreground=t["tag_rec"], background=t["tree_alt"])
        self.tree.tag_configure("WAITING", foreground=t["tag_wait"], background=t["tree_bg"])
        self.tree.tag_configure("WAITING_ALT", foreground=t["tag_wait"], background=t["tree_alt"])

    def _build_ui(self):
        self.header_banner = tk.Frame(self.root, padx=18, pady=10)
        self.header_banner.pack(fill=tk.X)

        self.title_box = tk.Frame(self.header_banner)
        self.title_box.pack(side=tk.LEFT)
        self.header_title_lbl = tk.Label(
            self.title_box,
            text="📺  IPTV Studio Pro — Validator, Editor EPG, Player & Timer Recorder",
            font=("Segoe UI", 13, "bold"),
        )
        self.header_title_lbl.pack(anchor=tk.W)
        self.header_sub_lbl = tk.Label(
            self.title_box,
            text="Seca, Vassel81, Pluto TV, Tvitava, Rakuten & iptv-org • Player integrato + VLC/ffplay • Timer Recorder",
            font=("Segoe UI", 9),
        )
        self.header_sub_lbl.pack(anchor=tk.W, pady=(2, 0))

        self.header_right_box = tk.Frame(self.header_banner)
        self.header_right_box.pack(side=tk.RIGHT, pady=2)

        self.ffmpeg_badge = tk.Label(
            self.header_right_box,
            text="ffmpeg: verifica...",
            font=("Segoe UI", 8, "bold"),
            padx=9,
            pady=5,
        )
        self.ffmpeg_badge.pack(side=tk.LEFT, padx=(0, 8))

        self.theme_btn = self._make_btn(
            self.header_right_box,
            text="☀️ Tema Chiaro" if self.theme_mode == "dark" else "🌙 Tema Scuro",
            command=self._toggle_theme,
            kind="neutral",
        )
        self.theme_btn.pack(side=tk.LEFT)

        main_frame = ttk.Frame(self.root, padding="12 10 12 10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        top_card = tk.Frame(main_frame, padx=12, pady=9)
        top_card.pack(fill=tk.X, pady=(0, 8))
        self.card_frames.append(top_card)

        row1 = ttk.Frame(top_card, style="Card.TFrame")
        row1.pack(fill=tk.X, pady=(0, 5))

        lbl_m3u = tk.Label(row1, text="📂 Playlist M3U:", width=14, anchor=tk.W, font=("Segoe UI", 9, "bold"))
        lbl_m3u.pack(side=tk.LEFT)
        self.themed_labels.append((lbl_m3u, "card"))

        self.file_path_var = tk.StringVar(value=DEFAULT_M3U_URL)
        ent_m3u = tk.Entry(row1, textvariable=self.file_path_var, font=("Segoe UI", 9))
        ent_m3u.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=4, padx=(0, 6))
        self.themed_entries.append(ent_m3u)

        self._make_btn(row1, "Apri File...", self._load_file, kind="neutral").pack(side=tk.LEFT, padx=(0, 5))
        self.load_url_btn = self._make_btn(
            row1, "🌐 Carica URL", lambda: self._load_m3u_from_url(silent=False), kind="accent"
        )
        self.load_url_btn.pack(side=tk.LEFT, padx=(0, 5))
        self._make_btn(row1, "Incolla Lista", self._open_paste_dialog, kind="neutral").pack(side=tk.LEFT)

        row_presets = ttk.Frame(top_card, style="Card.TFrame")
        row_presets.pack(fill=tk.X, pady=(0, 6))

        lbl_presets = tk.Label(row_presets, text="⚡ Liste Rapide:", width=14, anchor=tk.W, font=("Segoe UI", 9, "bold"))
        lbl_presets.pack(side=tk.LEFT)
        self.themed_labels.append((lbl_presets, "card"))

        self.load_seca_btn = self._make_btn(row_presets, "📺 Seca", self._load_seca_list, kind="success", padx=9, pady=4)
        self.load_seca_btn.pack(side=tk.LEFT, padx=(0, 5))

        self.load_vassel_btn = self._make_btn(row_presets, "🇮🇹 Vassel81", self._load_vassel81_list, kind="success", padx=9, pady=4)
        self.load_vassel_btn.pack(side=tk.LEFT, padx=(0, 5))

        self.load_pluto_btn = self._make_btn(row_presets, "🪐 Pluto TV + EPG", self._load_pluto_list, kind="warning", padx=9, pady=4)
        self.load_pluto_btn.pack(side=tk.LEFT, padx=(0, 5))

        self.load_tvitava_btn = self._make_btn(row_presets, "📡 Tvitava", self._load_tvitava_list, kind="accent", padx=9, pady=4)
        self.load_tvitava_btn.pack(side=tk.LEFT, padx=(0, 5))

        self.load_rakuten_btn = self._make_btn(row_presets, "🎬 Rakuten + EPG", self._load_rakuten_list, kind="warning", padx=9, pady=4)
        self.load_rakuten_btn.pack(side=tk.LEFT, padx=(0, 5))

        self.load_iptvorg_btn = self._make_btn(row_presets, "🌍 iptv-org", self._load_iptv_org_list, kind="neutral", padx=9, pady=4)
        self.load_iptvorg_btn.pack(side=tk.LEFT)

        row_epg = ttk.Frame(top_card, style="Card.TFrame")
        row_epg.pack(fill=tk.X, pady=(0, 6))

        lbl_epg = tk.Label(row_epg, text="🗓️ EPG XMLTV:", width=14, anchor=tk.W, font=("Segoe UI", 9, "bold"))
        lbl_epg.pack(side=tk.LEFT)
        self.themed_labels.append((lbl_epg, "card"))

        self.epg_source_var = tk.StringVar(value=", ".join(DEFAULT_EPG_URLS))
        ent_epg = tk.Entry(row_epg, textvariable=self.epg_source_var, font=("Segoe UI", 9))
        ent_epg.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=4, padx=(0, 6))
        self.themed_entries.append(ent_epg)

        self._make_btn(row_epg, "Apri .xml / .gz...", self._browse_epg_file, kind="neutral").pack(side=tk.LEFT, padx=(0, 5))
        self.load_epg_btn = self._make_btn(
            row_epg, "Carica EPG", lambda: self._start_epg_load(silent=False), kind="accent"
        )
        self.load_epg_btn.pack(side=tk.LEFT, padx=(0, 5))
        self._make_btn(row_epg, "✨ Auto-EPG", self._auto_match_epg_smart, kind="warning").pack(side=tk.LEFT)

        row_player = ttk.Frame(top_card, style="Card.TFrame")
        row_player.pack(fill=tk.X, pady=(0, 7))

        lbl_pl = tk.Label(row_player, text="🎬 Player Esterno:", width=14, anchor=tk.W, font=("Segoe UI", 9, "bold"))
        lbl_pl.pack(side=tk.LEFT)
        self.themed_labels.append((lbl_pl, "card"))

        self.player_type_var = tk.StringVar(value="vlc")
        ttk.Radiobutton(
            row_player, text="VLC", variable=self.player_type_var, value="vlc", command=self._on_player_type_change
        ).pack(side=tk.LEFT, padx=(0, 6))
        ttk.Radiobutton(
            row_player, text="ffplay", variable=self.player_type_var, value="ffplay", command=self._on_player_type_change
        ).pack(side=tk.LEFT, padx=(0, 8))

        self.player_exe_var = tk.StringVar()
        ent_pl = tk.Entry(row_player, textvariable=self.player_exe_var, font=("Segoe UI", 9))
        ent_pl.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=4, padx=(0, 5))
        self.themed_entries.append(ent_pl)

        self._make_btn(row_player, "Sfoglia...", self._browse_player, kind="neutral", padx=8).pack(side=tk.LEFT, padx=(0, 12))

        lbl_recdir = tk.Label(row_player, text="📁 Cartella REC:", anchor=tk.W, font=("Segoe UI", 9, "bold"))
        lbl_recdir.pack(side=tk.LEFT, padx=(0, 5))
        self.themed_labels.append((lbl_recdir, "card"))

        self.rec_folder_var = tk.StringVar()
        ent_recdir = tk.Entry(row_player, textvariable=self.rec_folder_var, width=24, font=("Segoe UI", 9))
        ent_recdir.pack(side=tk.LEFT, ipady=4, padx=(0, 5))
        self.themed_entries.append(ent_recdir)

        self._make_btn(row_player, "Scegli...", self._browse_rec_folder, kind="neutral", padx=8).pack(side=tk.LEFT, padx=(0, 4))
        self._make_btn(row_player, "Apri", self._open_rec_folder, kind="neutral", padx=8).pack(side=tk.LEFT)

        row2 = ttk.Frame(top_card, style="Card.TFrame")
        row2.pack(fill=tk.X)

        ttk.Label(row2, text="Timeout (s):").pack(side=tk.LEFT, padx=(0, 4))
        self.timeout_var = tk.IntVar(value=5)
        ttk.Spinbox(row2, from_=2, to=30, width=4, textvariable=self.timeout_var).pack(side=tk.LEFT, padx=(0, 12))

        ttk.Label(row2, text="Thread:").pack(side=tk.LEFT, padx=(0, 4))
        self.workers_var = tk.IntVar(value=12)
        ttk.Spinbox(row2, from_=1, to=30, width=4, textvariable=self.workers_var).pack(side=tk.LEFT, padx=(0, 12))

        self.deep_check_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            row2,
            text="Verifica manifest HLS",
            variable=self.deep_check_var,
        ).pack(side=tk.LEFT, padx=(0, 10))

        self.probe_quality_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            row2,
            text="Rileva Risoluzione (1080p/720p)",
            variable=self.probe_quality_var,
        ).pack(side=tk.LEFT, padx=(0, 12))

        self.stop_btn = self._make_btn(row2, "⏹ Ferma", self._stop_check, kind="danger", state=tk.DISABLED)
        self.stop_btn.pack(side=tk.RIGHT)

        self.start_btn = self._make_btn(row2, "⚡ Avvia Controllo Flussi", self._start_check, kind="accent")
        self.start_btn.pack(side=tk.RIGHT, padx=(0, 6))

        self.retry_offline_btn = self._make_btn(
            row2, "🔄 Retry Offline", self._recheck_offline_channels, kind="warning"
        )
        self.retry_offline_btn.pack(side=tk.RIGHT, padx=(0, 6))

        self._make_btn(row2, "🧹 Duplicati", self._remove_duplicates, kind="neutral").pack(side=tk.RIGHT, padx=(0, 6))
        self._make_btn(row2, "↩ Ordine Orig.", self._restore_original_order, kind="neutral").pack(side=tk.RIGHT, padx=(0, 6))

        stats_card = tk.Frame(main_frame, padx=12, pady=7)
        stats_card.pack(fill=tk.X, pady=(0, 8))
        self.card_frames.append(stats_card)

        self.stats_var = tk.StringVar(value="📊 Totale: 0   •   🟢 Online: 0   •   🔴 Offline: 0   •   🗓️ EPG: 0")
        lbl_stats = tk.Label(stats_card, textvariable=self.stats_var, font=("Segoe UI", 9, "bold"))
        lbl_stats.pack(side=tk.LEFT)
        self.themed_labels.append((lbl_stats, "card"))

        filter_box = ttk.Frame(stats_card, style="Card.TFrame")
        filter_box.pack(side=tk.RIGHT)

        ttk.Label(filter_box, text="🔍 Cerca Canale:").pack(side=tk.LEFT, padx=(0, 4))
        self.search_query_var = tk.StringVar()
        ent_search = tk.Entry(filter_box, textvariable=self.search_query_var, width=20, font=("Segoe UI", 9))
        ent_search.pack(side=tk.LEFT, ipady=3, padx=(0, 3))
        self.themed_entries.append(ent_search)
        self.search_query_var.trace_add("write", lambda *_: self._refresh_tree())

        self._make_btn(
            filter_box,
            "✖",
            lambda: self.search_query_var.set(""),
            kind="neutral",
            padx=6,
            pady=2,
        ).pack(side=tk.LEFT, padx=(0, 10))

        self.fav_only_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(
            filter_box,
            text="Solo ★",
            variable=self.fav_only_var,
            command=self._refresh_tree,
        ).pack(side=tk.LEFT, padx=(0, 10))

        ttk.Label(filter_box, text="🌍 Paese:").pack(side=tk.LEFT, padx=(0, 4))
        self.country_filter_var = tk.StringVar(value="Tutti i paesi")
        self.country_combo = ttk.Combobox(
            filter_box,
            textvariable=self.country_filter_var,
            values=["Tutti i paesi"],
            state="readonly",
            width=15,
        )
        self.country_combo.pack(side=tk.LEFT, padx=(0, 10))
        self.country_combo.bind("<<ComboboxSelected>>", lambda e: self._refresh_tree())

        self.filter_var = tk.StringVar(value="ALL")
        for label, val in [("Tutti", "ALL"), ("Online", "ONLINE"), ("Offline", "OFFLINE")]:
            ttk.Radiobutton(
                filter_box,
                text=label,
                variable=self.filter_var,
                value=val,
                command=self._refresh_tree,
            ).pack(side=tk.LEFT, padx=(0, 6))

        split_pane = ttk.PanedWindow(main_frame, orient=tk.HORIZONTAL)
        split_pane.pack(fill=tk.BOTH, expand=True, pady=(0, 8))

        table_card = tk.Frame(split_pane, padx=2, pady=2)
        self.card_frames.append(table_card)
        split_pane.add(table_card, weight=3)

        columns = ("idx", "fav", "status", "country", "name", "quality", "epg", "latency", "detail", "url")
        self.tree = ttk.Treeview(table_card, columns=columns, show="headings", selectmode="extended")

        self.tree.heading("idx", text="#")
        self.tree.heading("fav", text="★")
        self.tree.heading("status", text="Stato")
        self.tree.heading("country", text="Paese")
        self.tree.heading("name", text="Canale")
        self.tree.heading("quality", text="Qualità")
        self.tree.heading("epg", text="EPG / In Onda Ora")
        self.tree.heading("latency", text="Latenza")
        self.tree.heading("detail", text="Esito / HTTP")
        self.tree.heading("url", text="URL Flusso")

        self.tree.column("idx", width=42, anchor=tk.CENTER, stretch=False)
        self.tree.column("fav", width=34, anchor=tk.CENTER, stretch=False)
        self.tree.column("status", width=96, anchor=tk.CENTER, stretch=False)
        self.tree.column("country", width=112, anchor=tk.W, stretch=False)
        self.tree.column("name", width=165, anchor=tk.W)
        self.tree.column("quality", width=82, anchor=tk.CENTER, stretch=False)
        self.tree.column("epg", width=230, anchor=tk.W)
        self.tree.column("latency", width=66, anchor=tk.CENTER, stretch=False)
        self.tree.column("detail", width=135, anchor=tk.W)
        self.tree.column("url", width=210, anchor=tk.W)

        vsb = ttk.Scrollbar(table_card, orient="vertical", command=self.tree.yview)
        hsb = ttk.Scrollbar(table_card, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

        self.tree.grid(row=0, column=0, sticky=tk.NSEW)
        vsb.grid(row=0, column=1, sticky=tk.NS)
        hsb.grid(row=1, column=0, sticky=tk.EW)

        table_card.rowconfigure(0, weight=1)
        table_card.columnconfigure(0, weight=1)

        self.tree.bind("<Double-1>", lambda e: self._play_embedded_selected())

        self.ctx_menu = tk.Menu(self.root, tearoff=0)
        self.ctx_menu.add_command(label="▶  Riproduci nel Player Integrato", command=self._play_embedded_selected)
        self.ctx_menu.add_command(label="⧉  Avvia su Player Esterno (VLC / ffplay)", command=self._play_selected)
        self.ctx_menu.add_command(label="★  Aggiungi / Rimuovi dai Preferiti", command=self._toggle_favorite_selected)
        self.ctx_menu.add_command(label="✏️  Modifica Canale / Associa EPG...", command=self._open_edit_channel_dialog)
        self.ctx_menu.add_separator()
        self.ctx_menu.add_command(label="⬆  Sposta Canale Su", command=lambda: self._move_selected_channel(-1))
        self.ctx_menu.add_command(label="⬇  Sposta Canale Giù", command=lambda: self._move_selected_channel(1))
        self.ctx_menu.add_separator()
        self.ctx_menu.add_command(label="🔴  Registra Flusso Video Adesso...", command=self._start_recording_selected)
        self.ctx_menu.add_command(label="⏰  Programma Timer da EPG...", command=self._open_epg_record_dialog)
        self.ctx_menu.add_command(label="⏹  Ferma / Annulla Timer Canale", command=self._stop_recording_for_selected_channel)
        self.ctx_menu.add_command(label="📅  Mostra Guida EPG Canale", command=self._show_channel_epg_dialog)
        self.ctx_menu.add_separator()
        self.ctx_menu.add_command(label="📋  Copia URL flusso", command=self._copy_selected_url)
        self.ctx_menu.add_command(label="🔄  Ricontrolla selezionati", command=self._recheck_selected)
        self.ctx_menu.add_command(label="🗑️  Rimuovi selezionati dalla lista", command=self._remove_selected)
        self.tree.bind("<Button-3>", self._show_context_menu)

        player_card = tk.Frame(split_pane, padx=10, pady=8, width=420)
        self.card_frames.append(player_card)
        split_pane.add(player_card, weight=2)

        p_head = tk.Frame(player_card)
        p_head.pack(fill=tk.X, pady=(0, 6))

        self.embed_now_lbl = tk.Label(
            p_head,
            text="🎬 Player Integrato — Nessun flusso in riproduzione",
            font=("Segoe UI", 9, "bold"),
            anchor=tk.W,
        )
        self.embed_now_lbl.pack(side=tk.LEFT, fill=tk.X, expand=True)

        self.video_stage = tk.Frame(player_card, bg="#050811", height=230)
        self.video_stage.pack(fill=tk.BOTH, expand=True, pady=(0, 8))
        self.video_stage.pack_propagate(False)
        self.video_stage.bind("<Configure>", self._on_video_stage_resize)

        self.video_placeholder_lbl = tk.Label(
            self.video_stage,
            text="Seleziona un canale e clicca '▶ Player' oppure fai doppio clic\n(ffplay integrato o disponibile accanto all'eseguibile)",
            bg="#050811",
            fg="#94a3b8",
            font=("Segoe UI", 9),
            justify=tk.CENTER,
        )
        self.video_placeholder_lbl.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

        p_ctrl = tk.Frame(player_card)
        p_ctrl.pack(fill=tk.X)

        self.embed_play_btn = self._make_btn(
            p_ctrl, "▶ Player", self._play_embedded_selected, kind="success", padx=9, pady=4
        )
        self.embed_play_btn.pack(side=tk.LEFT, padx=(0, 4))

        self.embed_stop_btn = self._make_btn(
            p_ctrl, "⏹ Stop", self._stop_embedded_player, kind="danger", state=tk.DISABLED, padx=9, pady=4
        )
        self.embed_stop_btn.pack(side=tk.LEFT, padx=(0, 6))

        self.mute_btn = self._make_btn(
            p_ctrl, "🔊", self._toggle_mute_embedded, kind="neutral", padx=7, pady=4
        )
        self.mute_btn.pack(side=tk.LEFT, padx=(0, 3))

        self.volume_var = tk.IntVar(value=80)
        self.vol_scale = tk.Scale(
            p_ctrl,
            from_=0,
            to=100,
            orient=tk.HORIZONTAL,
            variable=self.volume_var,
            showvalue=False,
            length=75,
            command=self._on_volume_change,
        )
        self.vol_scale.pack(side=tk.LEFT, padx=(0, 6))

        self._make_btn(
            p_ctrl, "⧉ Esterno", self._play_selected, kind="neutral", padx=8, pady=4
        ).pack(side=tk.RIGHT)

        bottom_card = tk.Frame(main_frame, padx=12, pady=8)
        bottom_card.pack(fill=tk.X)
        self.card_frames.append(bottom_card)

        self.progress = ttk.Progressbar(bottom_card, mode="determinate", style="Modern.Horizontal.TProgressbar")
        self.progress.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 8))

        self.play_btn = self._make_btn(bottom_card, "▶ Play Esterno", self._play_selected, kind="success", padx=9)
        self.play_btn.pack(side=tk.LEFT, padx=(0, 4))

        self._make_btn(bottom_card, "★", self._toggle_favorite_selected, kind="neutral", padx=8).pack(
            side=tk.LEFT, padx=(0, 4)
        )
        self._make_btn(bottom_card, "⬆", lambda: self._move_selected_channel(-1), kind="neutral", padx=7).pack(
            side=tk.LEFT, padx=(0, 2)
        )
        self._make_btn(bottom_card, "⬇", lambda: self._move_selected_channel(1), kind="neutral", padx=7).pack(
            side=tk.LEFT, padx=(0, 4)
        )

        self.edit_btn = self._make_btn(bottom_card, "✏️ Modifica / EPG", self._open_edit_channel_dialog, kind="neutral", padx=9)
        self.edit_btn.pack(side=tk.LEFT, padx=(0, 8))

        ttk.Label(bottom_card, text="Min (0=∞):").pack(side=tk.LEFT, padx=(0, 3))
        self.rec_minutes_var = tk.IntVar(value=0)
        self.rec_minutes_spin = ttk.Spinbox(
            bottom_card,
            from_=0,
            to=1440,
            width=4,
            textvariable=self.rec_minutes_var,
        )
        self.rec_minutes_spin.pack(side=tk.LEFT, padx=(0, 5))

        self.rec_btn = self._make_btn(bottom_card, "🔴 Registra", self._start_recording_selected, kind="danger", padx=9)
        self.rec_btn.pack(side=tk.LEFT, padx=(0, 4))

        self.rec_epg_btn = self._make_btn(
            bottom_card, "⏰ Reg. da EPG...", self._open_epg_record_dialog, kind="warning", padx=9
        )
        self.rec_epg_btn.pack(side=tk.LEFT, padx=(0, 4))

        self.stop_rec_btn = self._make_btn(
            bottom_card,
            "Timer / Reg. (0)",
            self._on_stop_rec_button_click,
            kind="neutral",
            state=tk.DISABLED,
            padx=9,
        )
        self.stop_rec_btn.pack(side=tk.LEFT, padx=(0, 8))

        self.export_online_btn = self._make_btn(
            bottom_card,
            "💾 Esporta M3U Pulita",
            lambda: self._export_m3u(mode="online"),
            kind="accent",
            padx=10,
        )
        self.export_online_btn.pack(side=tk.RIGHT)

        self.export_epg_btn = self._make_btn(
            bottom_card,
            "🗓️ Esporta Con EPG",
            lambda: self._export_m3u(mode="epg"),
            kind="neutral",
            padx=9,
        )
        self.export_epg_btn.pack(side=tk.RIGHT, padx=(0, 4))

        self.export_all_btn = self._make_btn(
            bottom_card,
            "Esporta Vista",
            lambda: self._export_m3u(mode="view"),
            kind="neutral",
            padx=9,
        )
        self.export_all_btn.pack(side=tk.RIGHT, padx=(0, 4))

    def _find_ffplay_for_embed(self):
        ffp = self._find_binary("ffplay.exe")
        if ffp:
            return ffp
        if self.player_type_var.get() == "ffplay":
            cand = self.player_exe_var.get().strip()
            if cand and os.path.isfile(cand):
                return cand
        return ""

    def _attach_win32_child_window(self, parent_hwnd, w, h):
        if os.name != "nt" or not parent_hwnd:
            return None
        try:
            user32 = ctypes.windll.user32
            enum_proc = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.c_void_p, ctypes.c_void_p)
            found = []

            def callback(hwnd, _lparam):
                if user32.IsWindowVisible(hwnd):
                    pid = ctypes.c_ulong()
                    user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
                    if self.embed_proc and pid.value == self.embed_proc.pid:
                        found.append(hwnd)
                return True

            for _ in range(12):
                found.clear()
                user32.EnumWindows(enum_proc(callback), 0)
                if found:
                    child_hwnd = found[0]
                    user32.SetParent(child_hwnd, parent_hwnd)
                    user32.MoveWindow(child_hwnd, 0, 0, max(100, int(w)), max(80, int(h)), True)
                    return child_hwnd
                time.sleep(0.12)
        except Exception:
            pass
        return None

    def _on_video_stage_resize(self, event):
        if os.name != "nt" or not self.embed_hwnd:
            return
        try:
            w = max(100, int(event.width))
            h = max(80, int(event.height))
            ctypes.windll.user32.MoveWindow(self.embed_hwnd, 0, 0, w, h, True)
        except Exception:
            pass

    def _toggle_mute_embedded(self):
        self.embed_muted = not self.embed_muted
        self.mute_btn.config(text="🔇" if self.embed_muted else "🔊")
        if self.embed_proc and self.embed_proc.poll() is None and self.embed_channel_name:
            sel = self._get_selected_channels()
            if sel:
                self._launch_embedded_stream(sel[0])

    def _on_volume_change(self, _val):
        if self.embed_muted and int(self.volume_var.get()) > 0:
            self.embed_muted = False
            self.mute_btn.config(text="🔊")

    def _play_embedded_selected(self):
        sel = self._get_selected_channels()
        if not sel:
            messagebox.showinfo("Nessuna selezione", "Seleziona un canale nella tabella per riprodurlo nel player.")
            return
        ch = sel[0]
        if ch["status"] == "OFFLINE":
            if not messagebox.askyesno(
                "Canale segnato OFFLINE",
                f"Il canale '{ch['name']}' risulta OFFLINE dall'ultimo controllo.\nVuoi provare comunque ad avviarlo nel player?",
            ):
                return
        self._launch_embedded_stream(ch)

    def _launch_embedded_stream(self, ch):
        ffplay_exe = self._find_ffplay_for_embed()
        if not ffplay_exe:
            messagebox.showwarning(
                "ffplay non trovato",
                "Per usare il player integrato serve ffplay.exe.\n"
                "In alternativa puoi cliccare '⧉ Esterno' per aprire il flusso su VLC.",
            )
            return

        self._stop_embedded_player(clear_label=False)
        self.root.update_idletasks()

        wid = self.video_stage.winfo_id()
        w = max(200, self.video_stage.winfo_width())
        h = max(140, self.video_stage.winfo_height())

        ua = ch["ua"] or self.default_ua
        referer = ch["referer"]
        vol = 0 if self.embed_muted else max(0, min(100, int(self.volume_var.get())))

        cmd = [
            ffplay_exe,
            "-noborder",
            "-x",
            str(w),
            "-y",
            str(h),
            "-volume",
            str(vol),
            "-fflags",
            "nobuffer",
            "-flags",
            "low_delay",
            "-loglevel",
            "error",
        ]
        if ua:
            cmd.extend(["-user_agent", ua])
        if referer:
            cmd.extend(["-headers", f"Referer: {referer}\r\n"])
        cmd.append(ch["url"])

        env = os.environ.copy()
        if os.name == "nt":
            env["SDL_WINDOWID"] = str(wid)
            env["SDL_VIDEODRIVER"] = "windows"

        creationflags = subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0
        try:
            self.embed_proc = subprocess.Popen(
                cmd,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                env=env,
                creationflags=creationflags,
            )
            self.embed_channel_name = ch["name"]
            self.video_placeholder_lbl.place_forget()
            self.embed_now_lbl.config(text=f"▶ In onda: {ch['name']}")
            self.embed_stop_btn.config(state=tk.NORMAL)
            self._style_single_button(self.embed_stop_btn)

            if os.name == "nt":
                threading.Thread(
                    target=self._attach_win32_worker,
                    args=(wid, w, h),
                    daemon=True,
                ).start()

            if not self.embed_poll_scheduled:
                self.embed_poll_scheduled = True
                self.root.after(400, self._poll_embedded_player)
        except Exception as e:
            messagebox.showerror("Errore Player Integrato", f"Impossibile avviare il player integrato:\n{e}")
            self._stop_embedded_player()

    def _attach_win32_worker(self, parent_hwnd, w, h):
        child = self._attach_win32_child_window(parent_hwnd, w, h)
        if child and self.embed_proc and self.embed_proc.poll() is None:
            self.embed_hwnd = child

    def _poll_embedded_player(self):
        if self.embed_proc is None:
            self.embed_poll_scheduled = False
            return
        if self.embed_proc.poll() is not None:
            self._stop_embedded_player()
            return
        self.root.after(400, self._poll_embedded_player)

    def _stop_embedded_player(self, clear_label=True):
        self.embed_poll_scheduled = False
        self.embed_hwnd = None
        proc = self.embed_proc
        self.embed_proc = None
        if proc is not None and proc.poll() is None:
            try:
                proc.terminate()
                proc.wait(timeout=1.5)
            except Exception:
                try:
                    proc.kill()
                except Exception:
                    pass
        if clear_label:
            self.embed_channel_name = ""
            self.embed_now_lbl.config(text="🎬 Player Integrato — Nessun flusso in riproduzione")
            self.video_placeholder_lbl.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
            self.embed_stop_btn.config(state=tk.DISABLED)
            self._style_single_button(self.embed_stop_btn)

    def _load_preset_list(self, m3u_url, extra_epg_url=None):
        self.file_path_var.set(m3u_url)
        if extra_epg_url:
            cur_sources = self._split_epg_sources(self.epg_source_var.get().strip())
            if extra_epg_url not in cur_sources:
                cur_sources.append(extra_epg_url)
                self.epg_source_var.set(", ".join(cur_sources))
            self._start_epg_load(silent=True)
        self._load_m3u_from_url(silent=False)

    def _load_seca_list(self):
        self._load_preset_list(SECA_M3U_URL)

    def _load_vassel81_list(self):
        self._load_preset_list(VASSEL81_M3U_URL)

    def _load_pluto_list(self):
        self._load_preset_list(PLUTO_M3U_URL, extra_epg_url=PLUTO_EPG_URL)

    def _load_tvitava_list(self):
        self._load_preset_list(TVITAVA_M3U_URL)

    def _load_rakuten_list(self):
        self._load_preset_list(RAKUTEN_M3U_URL, extra_epg_url=RAKUTEN_EPG_URL)

    def _load_iptv_org_list(self):
        self._load_preset_list(IPTV_ORG_M3U_URL)

    def _toggle_favorite_selected(self):
        sel = self._get_selected_channels()
        if not sel:
            return
        target_state = not all(ch.get("favorite", False) for ch in sel)
        for ch in sel:
            ch["favorite"] = target_state
        self._refresh_tree()
        self._update_stats()

    def _move_selected_channel(self, direction):
        if self.is_running:
            return
        sel = self._get_selected_channels()
        if len(sel) != 1:
            messagebox.showinfo("Selezione singola", "Seleziona un solo canale per spostarlo su o giù nella scaletta.")
            return
        ch = sel[0]
        pos = self.channels.index(ch)
        new_pos = pos + direction
        if new_pos < 0 or new_pos >= len(self.channels):
            return
        self.channels[pos], self.channels[new_pos] = self.channels[new_pos], self.channels[pos]
        for i, item in enumerate(self.channels, start=1):
            item["idx"] = i
        self._refresh_tree()
        iid = str(ch["uid"])
        if self.tree.exists(iid):
            self.tree.selection_set(iid)
            self.tree.see(iid)

    def _restore_original_order(self):
        if self.is_running or not self.channels:
            return
        self.channels.sort(key=lambda c: c.get("orig_idx", c["idx"]))
        for i, ch in enumerate(self.channels, start=1):
            ch["idx"] = i
        self._refresh_tree()
        self._update_stats()

    def _recheck_offline_channels(self):
        if self.is_running:
            return
        offline_chs = [ch for ch in self.channels if ch["status"] == "OFFLINE"]
        if not offline_chs:
            messagebox.showinfo("Nessun canale OFFLINE", "Non ci sono canali segnati come OFFLINE da ricontrollare.")
            return
        self._start_check(subset=offline_chs)

    def _remove_duplicates(self):
        if self.is_running:
            return
        if not self.channels:
            return
        seen_urls = set()
        seen_names = set()
        removed = 0

        ordered = sorted(
            self.channels,
            key=lambda c: (
                0 if c.get("favorite") else 1,
                0 if c["status"] == "ONLINE" else 1,
            ),
        )
        kept_ids = set()
        for ch in ordered:
            u_key = ch["url"].strip()
            n_key = normalize_key(ch["name"])
            if u_key in seen_urls or (n_key and n_key in seen_names):
                removed += 1
                continue
            seen_urls.add(u_key)
            if n_key:
                seen_names.add(n_key)
            kept_ids.add(ch["uid"])

        if removed == 0:
            messagebox.showinfo("Nessun duplicato", "Non sono stati trovati canali duplicati nella lista.")
            return

        if not messagebox.askyesno(
            "Rimuovi Duplicati",
            f"Trovati {removed} canali duplicati (stesso URL o stesso nome).\nVuoi eliminarli mantenendo i migliori?",
        ):
            return

        self.channels = [ch for ch in self.channels if ch["uid"] in kept_ids]
        for i, ch in enumerate(self.channels, start=1):
            ch["idx"] = i
        self._update_country_filter_options()
        self._refresh_tree()
        self._update_stats()

    def _auto_match_epg_smart(self):
        if not self.epg_channels:
            messagebox.showinfo("EPG non caricata", "Carica prima una guida XMLTV nella barra 'EPG XMLTV' in alto.")
            return
        if not self.channels:
            return

        matched_before = sum(1 for c in self.channels if c.get("epg_matched_id"))
        self._match_channels_with_epg(use_smart_fallback=True)
        matched_after = sum(1 for c in self.channels if c.get("epg_matched_id"))
        self._refresh_tree()
        self._update_stats()
        diff = max(0, matched_after - matched_before)
        messagebox.showinfo(
            "Auto-Abbinamento EPG",
            f"Abbinamento automatico completato!\n"
            f"- Nuovi canali associati: {diff}\n"
            f"- Totale canali con EPG attiva: {matched_after} su {len(self.channels)}",
        )

    def _browse_rec_folder(self):
        folder = filedialog.askdirectory(title="Seleziona cartella predefinita per le registrazioni")
        if folder:
            self.rec_folder_var.set(folder)
            self._save_config()

    def _open_rec_folder(self):
        folder = self.rec_folder_var.get().strip() or get_app_base_dir()
        if not os.path.isdir(folder):
            messagebox.showwarning("Cartella non trovata", f"La cartella non esiste:\n{folder}")
            return
        try:
            if os.name == "nt":
                os.startfile(folder)
            else:
                subprocess.Popen(["xdg-open", folder])
        except Exception as e:
            messagebox.showerror("Errore apertura cartella", f"Impossibile aprire la cartella:\n{e}")

    def _open_edit_channel_dialog(self):
        sel = self._get_selected_channels()
        if not sel:
            messagebox.showinfo("Nessuna selezione", "Seleziona un canale nella tabella per modificarlo o associare l'EPG.")
            return

        ch = sel[0]
        win = tk.Toplevel(self.root)
        win.title(f"Modifica Canale & Associa EPG - #{ch['idx']} {ch['name']}")
        win.geometry("760x600")
        win.transient(self.root)
        win.grab_set()

        form_frame = ttk.LabelFrame(win, text="Dati Canale & Parametri Flusso", padding="10")
        form_frame.pack(fill=tk.X, padx=10, pady=(10, 8))

        name_var = tk.StringVar(value=ch["name"])
        country_var = tk.StringVar(value=ch["country"])
        tvg_id_var = tk.StringVar(value=ch.get("tvg_id", ""))
        url_var = tk.StringVar(value=ch["url"])
        ua_var = tk.StringVar(value=ch.get("ua", ""))
        ref_var = tk.StringVar(value=ch.get("referer", ""))

        r0 = ttk.Frame(form_frame)
        r0.pack(fill=tk.X, pady=(0, 6))
        ttk.Label(r0, text="Nome Canale:", width=14).pack(side=tk.LEFT)
        ttk.Entry(r0, textvariable=name_var).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        ttk.Label(r0, text="Paese:").pack(side=tk.LEFT, padx=(0, 4))
        country_values = sorted(set(list(COUNTRY_MAP.values()) + ["N/D", ch["country"]]))
        ttk.Combobox(r0, textvariable=country_var, values=country_values, width=18).pack(side=tk.LEFT)

        r1 = ttk.Frame(form_frame)
        r1.pack(fill=tk.X, pady=(0, 6))
        ttk.Label(r1, text="ID EPG (tvg-id):", width=14).pack(side=tk.LEFT)
        ttk.Entry(r1, textvariable=tvg_id_var).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 6))
        ttk.Button(r1, text="Rimuovi EPG", command=lambda: tvg_id_var.set("")).pack(side=tk.LEFT)

        r2 = ttk.Frame(form_frame)
        r2.pack(fill=tk.X, pady=(0, 6))
        ttk.Label(r2, text="URL Flusso:", width=14).pack(side=tk.LEFT)
        ttk.Entry(r2, textvariable=url_var).pack(side=tk.LEFT, fill=tk.X, expand=True)

        r3 = ttk.Frame(form_frame)
        r3.pack(fill=tk.X, pady=(0, 6))
        ttk.Label(r3, text="User-Agent:", width=14).pack(side=tk.LEFT)
        ttk.Entry(r3, textvariable=ua_var).pack(side=tk.LEFT, fill=tk.X, expand=True)

        r4 = ttk.Frame(form_frame)
        r4.pack(fill=tk.X)
        ttk.Label(r4, text="Referer:", width=14).pack(side=tk.LEFT)
        ttk.Entry(r4, textvariable=ref_var).pack(side=tk.LEFT, fill=tk.X, expand=True)

        epg_frame = ttk.LabelFrame(
            win,
            text="Associa Canale alla Guida EPG XMLTV (clicca su un canale per impostare tvg-id)",
            padding="10",
        )
        epg_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 8))

        search_row = ttk.Frame(epg_frame)
        search_row.pack(fill=tk.X, pady=(0, 6))
        ttk.Label(search_row, text="Cerca nella guida EPG:").pack(side=tk.LEFT, padx=(0, 6))
        search_var = tk.StringVar()
        ttk.Entry(search_row, textvariable=search_var).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 6))

        def prefill_search():
            search_var.set(name_var.get().strip())

        ttk.Button(search_row, text="Cerca Nome Canale", command=prefill_search).pack(side=tk.LEFT, padx=(0, 4))
        ttk.Button(search_row, text="Mostra Tutti", command=lambda: search_var.set("")).pack(side=tk.LEFT)

        epg_cols = ("cid", "label", "events")
        epg_list = ttk.Treeview(epg_frame, columns=epg_cols, show="headings", selectmode="browse")
        epg_list.heading("cid", text="ID XMLTV (tvg-id)")
        epg_list.heading("label", text="Nome Canale nella Guida")
        epg_list.heading("events", text="Eventi")

        epg_list.column("cid", width=240, anchor=tk.W)
        epg_list.column("label", width=330, anchor=tk.W)
        epg_list.column("events", width=80, anchor=tk.CENTER, stretch=False)

        vsb = ttk.Scrollbar(epg_frame, orient="vertical", command=epg_list.yview)
        epg_list.configure(yscrollcommand=vsb.set)
        epg_list.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        vsb.pack(side=tk.RIGHT, fill=tk.Y)

        all_epg_items = sorted(self.epg_channels.items(), key=lambda x: (x[1].lower(), x[0].lower()))

        def populate_epg_list(*_):
            epg_list.delete(*epg_list.get_children())
            if not all_epg_items:
                epg_list.insert("", tk.END, values=("", "Nessuna guida EPG caricata (caricala nella barra in alto)", "0"))
                return
            q = search_var.get().strip().lower()
            cur_id = tvg_id_var.get().strip()
            selected_iid = None
            for idx_e, (cid, lbl) in enumerate(all_epg_items):
                if q and q not in cid.lower() and q not in lbl.lower():
                    continue
                ev_count = len(self.epg_programmes.get(cid, []))
                iid = f"e_{idx_e}"
                epg_list.insert("", tk.END, iid=iid, values=(cid, lbl, ev_count))
                if cur_id and cid == cur_id:
                    selected_iid = iid
            if selected_iid:
                epg_list.selection_set(selected_iid)
                epg_list.see(selected_iid)

        def on_epg_select(_event=None):
            if not all_epg_items:
                return
            sel_e = epg_list.selection()
            if not sel_e:
                return
            vals = epg_list.item(sel_e[0], "values")
            if vals and vals[0]:
                tvg_id_var.set(vals[0])

        epg_list.bind("<<TreeviewSelect>>", on_epg_select)
        search_var.trace_add("write", populate_epg_list)
        populate_epg_list()

        def on_save():
            new_name = name_var.get().strip() or ch["name"]
            new_country = country_var.get().strip() or "N/D"
            new_tvg_id = tvg_id_var.get().strip()
            new_url = url_var.get().strip()
            if not new_url:
                messagebox.showwarning("URL mancante", "L'URL del flusso non può essere vuoto.")
                return

            ch["name"] = new_name
            ch["country"] = new_country
            ch["tvg_id"] = new_tvg_id
            ch["url"] = new_url
            ch["ua"] = ua_var.get().strip()
            ch["referer"] = ref_var.get().strip()
            ch["extinf"] = update_extinf_line(ch.get("extinf", ""), new_name, new_tvg_id)

            if self.epg_channels:
                self._match_channels_with_epg()
            else:
                ch["epg_matched_id"] = new_tvg_id if new_tvg_id else None
                ch["epg_text"] = f"tvg-id: {new_tvg_id}" if new_tvg_id else "Non abbinato"

            self._update_country_filter_options()
            self._refresh_tree()
            self._update_stats()
            win.destroy()

        epg_list.bind("<Double-1>", lambda e: (on_epg_select(), on_save()))

        btn_row = ttk.Frame(win)
        btn_row.pack(fill=tk.X, padx=10, pady=(0, 10))
        ttk.Button(btn_row, text="Salva Modifiche", command=on_save).pack(side=tk.RIGHT)
        ttk.Button(btn_row, text="Annulla", command=win.destroy).pack(side=tk.RIGHT, padx=(0, 6))

    def _find_binary(self, exe_name):
        bundled_bin = os.path.join(get_bundled_bin_dir(), exe_name)
        if os.path.isfile(bundled_bin):
            return bundled_bin
        base_dir = get_app_base_dir()
        local_bin = os.path.join(base_dir, exe_name)
        if os.path.isfile(local_bin):
            return local_bin
        found = shutil.which(exe_name.replace(".exe", ""))
        if found and os.path.isfile(found):
            return found
        player_exe = self.player_exe_var.get().strip()
        if player_exe:
            folder = os.path.dirname(player_exe)
            cand = os.path.join(folder, exe_name)
            if os.path.isfile(cand):
                return cand
        for path in [
            rf"C:\ffmpeg\bin\{exe_name}",
            rf"C:\Program Files\ffmpeg\bin\{exe_name}",
            rf"C:\Program Files (x86)\ffmpeg\bin\{exe_name}",
        ]:
            if os.path.isfile(path):
                return path
        return ""

    def _find_ffmpeg(self):
        return self._find_binary("ffmpeg.exe")

    def _find_ffprobe(self):
        return self._find_binary("ffprobe.exe")

    def _refresh_ffmpeg_badge(self):
        ff = self._find_ffmpeg()
        if ff:
            self.ffmpeg_badge.config(text="✔ ffmpeg: PRONTO", bg="#16a34a", fg="#ffffff")
        else:
            self.ffmpeg_badge.config(text="⚠ Fallback HLS (no ffmpeg)", bg="#d97706", fg="#ffffff")

    def _probe_stream_resolution(self, url, ua, referer, timeout):
        ffprobe = self._find_ffprobe()
        if not ffprobe:
            return ""
        cmd = [
            ffprobe,
            "-v",
            "error",
            "-select_streams",
            "v:0",
            "-show_entries",
            "stream=height",
            "-of",
            "csv=p=0",
        ]
        if ua:
            cmd.extend(["-user_agent", ua])
        if referer:
            cmd.extend(["-headers", f"Referer: {referer}\r\n"])
        cmd.append(url)
        with self.ffprobe_semaphore:
            if self.stop_requested:
                return ""
            try:
                creationflags = subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0
                res = subprocess.run(
                    cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.DEVNULL,
                    timeout=max(4, timeout + 2),
                    creationflags=creationflags,
                )
                out = (res.stdout or b"").decode("utf-8", errors="ignore").strip()
                for line in out.splitlines():
                    if line.strip().isdigit():
                        h = int(line.strip())
                        if h >= 2160:
                            return "4K (2160p)"
                        if h > 0:
                            return f"{h}p"
            except Exception:
                pass
        return ""

    def _get_current_epg_program(self, ch):
        cid = ch.get("epg_matched_id")
        if not cid or cid not in self.epg_programmes:
            return None
        now = datetime.now().astimezone()
        for start_dt, stop_dt, title, desc in self.epg_programmes[cid]:
            if start_dt and stop_dt and start_dt <= now <= stop_dt:
                return (start_dt, stop_dt, title, desc)
        return None

    def _get_channel_rec_state(self, ch_uid):
        has_rec = False
        has_wait = False
        for rec in self.active_recordings.values():
            if rec["ch_uid"] == ch_uid:
                if rec["state"] == "RECORDING":
                    has_rec = True
                elif rec["state"] == "WAITING":
                    has_wait = True
        if has_rec:
            return "RECORDING"
        if has_wait:
            return "WAITING"
        return None

    def _open_epg_record_dialog(self):
        sel = self._get_selected_channels()
        if not sel:
            messagebox.showinfo("Nessuna selezione", "Seleziona prima un canale nella tabella.")
            return

        ch = sel[0]
        cid = ch.get("epg_matched_id")
        if not cid or cid not in self.epg_programmes:
            if messagebox.askyesno(
                "EPG non abbinata al canale",
                f"Nessun palinsesto EPG trovato per '{ch['name']}'.\n"
                "Vuoi aprire la finestra di modifica per associare manualmente il canale all'EPG?",
            ):
                self._open_edit_channel_dialog()
            return

        now = datetime.now().astimezone()
        progs = self.epg_programmes[cid]
        relevant = [p for p in progs if (p[1] is None or p[1] >= now)]
        if not relevant:
            relevant = progs[-25:]

        win = tk.Toplevel(self.root)
        win.title(f"Timer & Registrazione EPG - {ch['name']}")
        win.geometry("760x480")
        win.transient(self.root)
        win.grab_set()

        ttk.Label(
            win,
            text="Seleziona un programma in onda (avvio immediato) oppure futuro (avvio automatico con timer):",
            font=("Segoe UI", 9, "bold"),
        ).pack(anchor=tk.W, padx=10, pady=(10, 6))

        cols = ("status", "time", "duration", "title")
        epg_tree = ttk.Treeview(win, columns=cols, show="headings", selectmode="browse")
        epg_tree.heading("status", text="Modalità")
        epg_tree.heading("time", text="Data / Orario")
        epg_tree.heading("duration", text="Durata / Avvio")
        epg_tree.heading("title", text="Titolo Programma")

        epg_tree.column("status", width=115, anchor=tk.CENTER, stretch=False)
        epg_tree.column("time", width=145, anchor=tk.CENTER, stretch=False)
        epg_tree.column("duration", width=155, anchor=tk.CENTER, stretch=False)
        epg_tree.column("title", width=310, anchor=tk.W)
        epg_tree.tag_configure("NOW", foreground="#16a34a")
        epg_tree.tag_configure("FUTURE", foreground="#2563eb")
        epg_tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 8))

        item_map = {}
        first_iid = None
        for idx_p, (start_dt, stop_dt, title, desc) in enumerate(relevant[:60]):
            s_str = start_dt.strftime("%d/%m %H:%M") if start_dt else "??:??"
            e_str = stop_dt.strftime("%H:%M") if stop_dt else "??:??"
            is_now = bool(start_dt and stop_dt and start_dt <= now <= stop_dt)
            is_future = bool(start_dt and start_dt > now)

            if is_now:
                dur_mins = max(1, math.ceil((stop_dt - now).total_seconds() / 60))
                status_txt = "IN ONDA ORA"
                dur_txt = f"{dur_mins} min restanti"
                tag = ("NOW",)
            elif is_future:
                if stop_dt and stop_dt > start_dt:
                    dur_mins = max(1, math.ceil((stop_dt - start_dt).total_seconds() / 60))
                else:
                    dur_mins = 60
                wait_mins = max(1, math.ceil((start_dt - now).total_seconds() / 60))
                status_txt = "TIMER FUTURO"
                dur_txt = f"{dur_mins} min (tra {wait_mins}m)"
                tag = ("FUTURE",)
            else:
                dur_mins = 60
                status_txt = "Manuale"
                dur_txt = "60 min (default)"
                tag = ()

            iid = f"p_{idx_p}"
            if first_iid is None:
                first_iid = iid
            item_map[iid] = (start_dt, stop_dt, title, dur_mins, is_future)
            epg_tree.insert(
                "",
                tk.END,
                iid=iid,
                values=(status_txt, f"{s_str} - {e_str}", dur_txt, title),
                tags=tag,
            )

        if first_iid:
            epg_tree.selection_set(first_iid)

        opt_row = ttk.Frame(win)
        opt_row.pack(fill=tk.X, padx=10, pady=(0, 8))

        ttk.Label(opt_row, text="Anticipo avvio timer (min):").pack(side=tk.LEFT, padx=(0, 4))
        pre_margin_var = tk.IntVar(value=1)
        ttk.Spinbox(opt_row, from_=0, to=30, width=4, textvariable=pre_margin_var).pack(side=tk.LEFT, padx=(0, 16))

        ttk.Label(opt_row, text="Margine extra finale (min):").pack(side=tk.LEFT, padx=(0, 4))
        post_margin_var = tk.IntVar(value=2)
        ttk.Spinbox(opt_row, from_=0, to=60, width=4, textvariable=post_margin_var).pack(side=tk.LEFT)

        def on_confirm_epg_rec():
            sel_items = epg_tree.selection()
            if not sel_items:
                return
            start_dt, stop_dt, title, base_mins, is_future = item_map[sel_items[0]]
            pre_m = max(0, int(pre_margin_var.get()))
            post_m = max(0, int(post_margin_var.get()))

            now_confirm = datetime.now().astimezone()
            scheduled_start_ts = None
            if is_future and start_dt is not None:
                target_start = start_dt - timedelta(minutes=pre_m)
                if target_start > now_confirm:
                    scheduled_start_ts = target_start.timestamp()
                    if stop_dt and stop_dt > target_start:
                        total_mins = max(1, math.ceil((stop_dt - target_start).total_seconds() / 60) + post_m)
                    else:
                        total_mins = max(1, base_mins + pre_m + post_m)
                else:
                    if stop_dt and stop_dt > now_confirm:
                        total_mins = max(1, math.ceil((stop_dt - now_confirm).total_seconds() / 60) + post_m)
                    else:
                        total_mins = max(1, base_mins + post_m)
            else:
                if stop_dt and stop_dt > now_confirm:
                    total_mins = max(1, math.ceil((stop_dt - now_confirm).total_seconds() / 60) + post_m)
                else:
                    total_mins = max(1, base_mins + post_m)

            self.rec_minutes_var.set(total_mins)
            win.destroy()
            self._start_recording_selected(
                custom_prog_title=title,
                scheduled_start_ts=scheduled_start_ts,
                duration_minutes_override=total_mins,
            )

        btn_row = ttk.Frame(win)
        btn_row.pack(fill=tk.X, padx=10, pady=(0, 10))
        ttk.Button(btn_row, text="Conferma Timer / Avvia Registrazione", command=on_confirm_epg_rec).pack(side=tk.RIGHT)
        ttk.Button(btn_row, text="Annulla", command=win.destroy).pack(side=tk.RIGHT, padx=(0, 6))

    def _start_recording_selected(
        self,
        custom_prog_title="",
        scheduled_start_ts=None,
        duration_minutes_override=None,
    ):
        sel = self._get_selected_channels()
        if not sel:
            messagebox.showinfo("Nessuna selezione", "Seleziona un canale dalla tabella per registrarne il flusso video.")
            return

        if duration_minutes_override is not None:
            mins = max(0, int(duration_minutes_override))
        else:
            try:
                mins = max(0, int(self.rec_minutes_var.get()))
            except Exception:
                mins = 0
                self.rec_minutes_var.set(0)

        ch = sel[0]
        prog_title = custom_prog_title.strip()
        if not prog_title and scheduled_start_ts is None:
            cur_epg = self._get_current_epg_program(ch)
            if cur_epg:
                prog_title = cur_epg[2]

        ref_dt = (
            datetime.fromtimestamp(scheduled_start_ts).astimezone()
            if scheduled_start_ts is not None
            else datetime.now().astimezone()
        )
        ts = ref_dt.strftime("%Y%m%d_%H%M%S")
        ch_part = sanitize_filename(ch["name"])
        epg_part = f"_{sanitize_filename(prog_title)}" if prog_title else ""
        timer_part = f"_{mins}min" if mins > 0 else ""
        default_name = f"{ch_part}{epg_part}_{ts}{timer_part}.ts"

        rec_dir = self.rec_folder_var.get().strip()
        if rec_dir and os.path.isdir(rec_dir):
            out_path = os.path.join(rec_dir, default_name)
        else:
            dialog_title = (
                f"Salva registrazione programmata - {ch['name']}"
                if scheduled_start_ts is not None
                else f"Salva registrazione - {ch['name']}"
            )
            out_path = filedialog.asksaveasfilename(
                title=dialog_title,
                defaultextension=".ts",
                initialfile=default_name,
                filetypes=[
                    ("Transport Stream Video (*.ts)", "*.ts"),
                    ("Video MP4 (*.mp4)", "*.mp4"),
                    ("Tutti i file", "*.*"),
                ],
            )
            if not out_path:
                return

        if any(os.path.abspath(r["file_path"]) == os.path.abspath(out_path) for r in self.active_recordings.values()):
            messagebox.showwarning("File in uso", "Questo file è già utilizzato da un'altra registrazione o timer attivo.")
            return

        now_ts = time.time()
        is_scheduled = scheduled_start_ts is not None and scheduled_start_ts > now_ts

        self.rec_counter += 1
        rec_id = self.rec_counter
        rec_info = {
            "id": rec_id,
            "ch_uid": ch["uid"],
            "channel_name": ch["name"],
            "prog_title": prog_title,
            "file_path": out_path,
            "state": "WAITING" if is_scheduled else "RECORDING",
            "scheduled_start": scheduled_start_ts if is_scheduled else now_ts,
            "start_time": scheduled_start_ts if is_scheduled else now_ts,
            "limit_seconds": mins * 60,
            "stop_event": threading.Event(),
            "timer_expired": False,
            "proc": None,
        }
        self.active_recordings[rec_id] = rec_info

        self._update_rec_controls_ui()
        self._update_channel_row_visual(ch)
        self._update_stats()

        ffmpeg_exe = self._find_ffmpeg()
        thread = threading.Thread(
            target=self._record_worker,
            args=(rec_info, dict(ch), ffmpeg_exe),
            daemon=True,
        )
        thread.start()

        if not self.rec_poll_scheduled:
            self.rec_poll_scheduled = True
            self.root.after(500, self._poll_recording_status)

        if is_scheduled:
            start_lbl = datetime.fromtimestamp(scheduled_start_ts).strftime("%d/%m/%Y alle %H:%M:%S")
            messagebox.showinfo(
                "Timer EPG Programmato",
                f"Timer impostato con successo!\n"
                f"Canale: {ch['name']}\n"
                f"Programma: {prog_title or 'N/D'}\n"
                f"Avvio automatico: {start_lbl}\n"
                f"Durata impostata: {mins} minuti\n"
                f"File: {out_path}\n\n"
                f"Lascia aperto il programma: la registrazione partirà e si fermerà automaticamente.",
            )

    def _download_hls_loop_fallback(self, rec_info, url, headers, out_path, deadline):
        stop_ev = rec_info["stop_event"]
        seen_segments = []
        seen_set = set()
        with open(out_path, "wb") as f_out:
            while not stop_ev.is_set():
                if deadline is not None and time.time() >= deadline:
                    rec_info["timer_expired"] = True
                    stop_ev.set()
                    break

                req = urllib.request.Request(url, headers=headers, method="GET")
                with urllib.request.urlopen(req, timeout=12, context=self.ssl_ctx) as resp:
                    final_url = resp.geturl()
                    body = resp.read().decode("utf-8", errors="ignore")

                lines = [ln.strip() for ln in body.splitlines() if ln.strip()]
                if not lines or not lines[0].startswith("#EXTM3U"):
                    with urllib.request.urlopen(req, timeout=15, context=self.ssl_ctx) as raw_resp:
                        while not stop_ev.is_set():
                            if deadline is not None and time.time() >= deadline:
                                rec_info["timer_expired"] = True
                                stop_ev.set()
                                break
                            chunk = raw_resp.read(16384)
                            if not chunk:
                                break
                            f_out.write(chunk)
                            f_out.flush()
                    break

                variant_url = None
                for i, ln in enumerate(lines):
                    if ln.startswith("#EXT-X-STREAM-INF") and i + 1 < len(lines) and not lines[i + 1].startswith("#"):
                        variant_url = urllib.parse.urljoin(final_url, lines[i + 1])
                if variant_url:
                    url = variant_url
                    continue

                target_dur = 2.0
                seg_urls = []
                for ln in lines:
                    if ln.startswith("#EXT-X-TARGETDURATION:"):
                        try:
                            target_dur = max(1.0, float(ln.split(":", 1)[1].strip()))
                        except Exception:
                            pass
                    elif not ln.startswith("#"):
                        seg_urls.append(urllib.parse.urljoin(final_url, ln))

                new_downloaded = 0
                for seg in seg_urls:
                    if stop_ev.is_set():
                        break
                    if deadline is not None and time.time() >= deadline:
                        rec_info["timer_expired"] = True
                        stop_ev.set()
                        break
                    if seg in seen_set:
                        continue
                    seen_set.add(seg)
                    seen_segments.append(seg)
                    if len(seen_segments) > 400:
                        old = seen_segments.pop(0)
                        seen_set.discard(old)

                    seg_req = urllib.request.Request(seg, headers=headers, method="GET")
                    with urllib.request.urlopen(seg_req, timeout=12, context=self.ssl_ctx) as s_resp:
                        while not stop_ev.is_set():
                            data = s_resp.read(16384)
                            if not data:
                                break
                            f_out.write(data)
                    f_out.flush()
                    new_downloaded += 1

                if "#EXT-X-ENDLIST" in body and new_downloaded == 0:
                    break

                wait_s = min(target_dur * 0.6, 3.0) if new_downloaded > 0 else 1.5
                end_wait = time.time() + wait_s
                while time.time() < end_wait and not stop_ev.is_set():
                    time.sleep(0.2)

    def _record_worker(self, rec_info, ch, ffmpeg_exe):
        url = ch["url"]
        ua = ch["ua"] or self.default_ua
        referer = ch["referer"]
        out_path = rec_info["file_path"]
        limit_seconds = rec_info["limit_seconds"]
        stop_ev = rec_info["stop_event"]
        err_msg = None

        try:
            if rec_info["state"] == "WAITING":
                while not stop_ev.is_set() and time.time() < rec_info["scheduled_start"]:
                    time.sleep(0.25)
                if stop_ev.is_set():
                    return
                rec_info["state"] = "RECORDING"
                rec_info["start_time"] = time.time()
                self.root.after(0, self._on_scheduled_recording_started, rec_info["ch_uid"])

            deadline = (rec_info["start_time"] + limit_seconds) if limit_seconds > 0 else None

            if ffmpeg_exe:
                cmd = [
                    ffmpeg_exe,
                    "-y",
                    "-hide_banner",
                    "-loglevel",
                    "error",
                    "-reconnect",
                    "1",
                    "-reconnect_streamed",
                    "1",
                    "-reconnect_delay_max",
                    "5",
                ]
                if ua:
                    cmd.extend(["-user_agent", ua])
                if referer:
                    cmd.extend(["-headers", f"Referer: {referer}\r\n"])
                cmd.extend(["-i", url])
                if limit_seconds > 0:
                    cmd.extend(["-t", str(limit_seconds)])
                cmd.extend(["-c", "copy"])
                if out_path.lower().endswith(".mp4"):
                    cmd.extend(["-bsf:a", "aac_adtstoasc", "-movflags", "+frag_keyframe+empty_moov"])
                cmd.append(out_path)

                creationflags = subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0
                proc = subprocess.Popen(
                    cmd,
                    stdin=subprocess.PIPE,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.PIPE,
                    creationflags=creationflags,
                )
                rec_info["proc"] = proc

                while not stop_ev.is_set():
                    if proc.poll() is not None:
                        break
                    if deadline is not None and time.time() >= deadline:
                        rec_info["timer_expired"] = True
                        stop_ev.set()
                        break
                    time.sleep(0.25)

                if proc.poll() is None:
                    try:
                        proc.stdin.write(b"q\n")
                        proc.stdin.flush()
                    except Exception:
                        pass
                    try:
                        proc.wait(timeout=4)
                    except Exception:
                        proc.terminate()
                        try:
                            proc.wait(timeout=2)
                        except Exception:
                            proc.kill()
                else:
                    if proc.returncode not in (0, 255) and not stop_ev.is_set():
                        stderr_out = (proc.stderr.read() or b"").decode("utf-8", errors="ignore").strip()
                        err_msg = stderr_out or f"ffmpeg terminato con codice {proc.returncode}"
            else:
                headers = {"User-Agent": ua, "Accept": "*/*"}
                if referer:
                    headers["Referer"] = referer
                self._download_hls_loop_fallback(rec_info, url, headers, out_path, deadline)
        except Exception as e:
            if not stop_ev.is_set():
                err_msg = str(e)
        finally:
            self.root.after(0, self._on_recording_finished, rec_info["id"], err_msg)

    def _on_scheduled_recording_started(self, ch_uid):
        for ch in self.channels:
            if ch["uid"] == ch_uid:
                self._update_channel_row_visual(ch)
                break
        self._update_rec_controls_ui()
        self._update_stats()
        self._refresh_rec_manager_tree()

    def _stop_single_recording(self, rec_id):
        rec = self.active_recordings.get(rec_id)
        if rec:
            rec["timer_expired"] = False
            rec["stop_event"].set()

    def _stop_all_recordings(self):
        for rec_id in list(self.active_recordings.keys()):
            self._stop_single_recording(rec_id)

    def _stop_recording_for_selected_channel(self):
        sel = self._get_selected_channels()
        if not sel:
            return
        ch_uid = sel[0]["uid"]
        matching = [rec_id for rec_id, r in self.active_recordings.items() if r["ch_uid"] == ch_uid]
        if not matching:
            messagebox.showinfo("Nessun timer o registrazione", f"Nessun timer o registrazione attiva per '{sel[0]['name']}'.")
            return
        for rec_id in matching:
            self._stop_single_recording(rec_id)

    def _on_stop_rec_button_click(self):
        count = len(self.active_recordings)
        if count == 0:
            return
        if count == 1:
            only_id = next(iter(self.active_recordings.keys()))
            self._stop_single_recording(only_id)
        else:
            self._open_active_recordings_manager()

    def _open_active_recordings_manager(self):
        if self.rec_manager_win is not None and self.rec_manager_win.winfo_exists():
            self.rec_manager_win.lift()
            return

        win = tk.Toplevel(self.root)
        win.title("Gestione Timer EPG & Registrazioni Attive")
        win.geometry("820x350")
        win.transient(self.root)
        self.rec_manager_win = win

        ttk.Label(
            win,
            text="Timer programmati e registrazioni in corso (puoi annullarne/fermarne uno singolo oppure tutti):",
            font=("Segoe UI", 9, "bold"),
        ).pack(anchor=tk.W, padx=10, pady=(10, 6))

        cols = ("id", "state", "channel", "program", "time", "size", "file")
        rtree = ttk.Treeview(win, columns=cols, show="headings", selectmode="extended")
        rtree.heading("id", text="ID")
        rtree.heading("state", text="Stato")
        rtree.heading("channel", text="Canale")
        rtree.heading("program", text="Programma EPG")
        rtree.heading("time", text="Timer / Durata")
        rtree.heading("size", text="Dimensione")
        rtree.heading("file", text="File di destinazione")

        rtree.column("id", width=38, anchor=tk.CENTER, stretch=False)
        rtree.column("state", width=95, anchor=tk.CENTER, stretch=False)
        rtree.column("channel", width=135, anchor=tk.W)
        rtree.column("program", width=155, anchor=tk.W)
        rtree.column("time", width=155, anchor=tk.CENTER, stretch=False)
        rtree.column("size", width=80, anchor=tk.CENTER, stretch=False)
        rtree.column("file", width=140, anchor=tk.W)
        rtree.tag_configure("RECORDING", foreground="#d97706")
        rtree.tag_configure("WAITING", foreground="#2563eb")
        rtree.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 8))
        self.rec_manager_tree = rtree

        def stop_selected_in_manager():
            sel_ids = rtree.selection()
            for sid in sel_ids:
                try:
                    self._stop_single_recording(int(sid))
                except ValueError:
                    pass

        btn_row = ttk.Frame(win)
        btn_row.pack(fill=tk.X, padx=10, pady=(0, 10))

        ttk.Button(btn_row, text="Ferma / Annulla Selezionato", command=stop_selected_in_manager).pack(side=tk.LEFT)
        ttk.Button(btn_row, text="Ferma / Annulla Tutti", command=self._stop_all_recordings).pack(
            side=tk.LEFT, padx=(8, 0)
        )
        ttk.Button(btn_row, text="Chiudi Finestra", command=win.destroy).pack(side=tk.RIGHT)

        self._refresh_rec_manager_tree()

    def _refresh_rec_manager_tree(self):
        if self.rec_manager_win is None or not self.rec_manager_win.winfo_exists():
            return
        if self.rec_manager_tree is None:
            return

        rtree = self.rec_manager_tree
        selected = set(rtree.selection())
        rtree.delete(*rtree.get_children())

        now = time.time()
        for rec_id, rec in list(self.active_recordings.items()):
            if rec["state"] == "WAITING":
                rem_start = max(0, int(rec["scheduled_start"] - now))
                start_hhmm = datetime.fromtimestamp(rec["scheduled_start"]).strftime("%H:%M")
                state_lbl = "TIMER ATTESA"
                t_str = f"Avvio {start_hhmm} (tra {format_duration(rem_start)})"
                size_str = "-"
            else:
                state_lbl = "IN CORSO"
                elapsed = int(now - rec["start_time"])
                if rec["limit_seconds"] > 0:
                    rem = max(0, rec["limit_seconds"] - elapsed)
                    t_str = f"{format_duration(elapsed)} / {format_duration(rec['limit_seconds'])} (-{format_duration(rem)})"
                else:
                    t_str = f"{format_duration(elapsed)} (∞)"
                mb = 0.0
                if os.path.isfile(rec["file_path"]):
                    mb = os.path.getsize(rec["file_path"]) / (1024 * 1024)
                size_str = f"{mb:.1f} MB"

            rtree.insert(
                "",
                tk.END,
                iid=str(rec_id),
                values=(
                    rec_id,
                    state_lbl,
                    rec["channel_name"],
                    rec["prog_title"] or "-",
                    t_str,
                    size_str,
                    os.path.basename(rec["file_path"]),
                ),
                tags=(rec["state"],),
            )
            if str(rec_id) in selected:
                rtree.selection_add(str(rec_id))

    def _update_rec_controls_ui(self):
        count = len(self.active_recordings)
        if count == 0:
            self.stop_rec_btn._btn_kind = "neutral"
            self.stop_rec_btn.config(text="Timer / Reg. (0)", state=tk.DISABLED)
        elif count == 1:
            rec = next(iter(self.active_recordings.values()))
            lbl = "Annulla Timer (1)" if rec["state"] == "WAITING" else "⏹ Ferma Reg. (1)"
            self.stop_rec_btn._btn_kind = "warning"
            self.stop_rec_btn.config(text=lbl, state=tk.NORMAL)
        else:
            self.stop_rec_btn._btn_kind = "warning"
            self.stop_rec_btn.config(text=f"📋 Timer / Reg. ({count})", state=tk.NORMAL)
        self._style_single_button(self.stop_rec_btn)

    def _poll_recording_status(self):
        if not self.active_recordings:
            self.rec_poll_scheduled = False
            self._update_stats()
            self._refresh_rec_manager_tree()
            return

        now = time.time()
        for rec in list(self.active_recordings.values()):
            if (
                rec["state"] == "RECORDING"
                and rec["limit_seconds"] > 0
                and (now - rec["start_time"]) >= rec["limit_seconds"]
            ):
                rec["timer_expired"] = True
                rec["stop_event"].set()

        self._update_stats()
        self._refresh_rec_manager_tree()
        self.root.after(500, self._poll_recording_status)

    def _on_recording_finished(self, rec_id, err_msg):
        rec = self.active_recordings.pop(rec_id, None)
        self._update_rec_controls_ui()
        self._update_stats()
        self._refresh_rec_manager_tree()

        if not rec:
            return

        for ch in self.channels:
            if ch["uid"] == rec["ch_uid"]:
                self._update_channel_row_visual(ch)
                break

        if rec["state"] == "WAITING":
            messagebox.showinfo(
                "Timer Annullato",
                f"Timer programmato annullato prima dell'avvio:\nCanale: {rec['channel_name']}\nProgramma: {rec['prog_title'] or 'N/D'}",
            )
            return

        out_path = rec["file_path"]
        was_timer_end = rec["timer_expired"]
        was_manual_stop = rec["stop_event"].is_set() and not was_timer_end

        size_mb = 0.0
        if os.path.isfile(out_path):
            size_mb = os.path.getsize(out_path) / (1024 * 1024)

        if err_msg and size_mb < 0.01:
            messagebox.showerror(
                "Errore Registrazione",
                f"Canale: {rec['channel_name']}\nImpossibile registrare il flusso:\n{err_msg}",
            )
        else:
            if was_timer_end:
                status_txt = "completata allo scadere del timer"
            elif was_manual_stop:
                status_txt = "interrotta manualmente"
            else:
                status_txt = "terminata"

            prog_line = f"Programma EPG: {rec['prog_title']}\n" if rec["prog_title"] else ""
            messagebox.showinfo(
                "Registrazione Completata",
                f"Registrazione {status_txt}!\n"
                f"Canale: {rec['channel_name']}\n"
                f"{prog_line}"
                f"File: {out_path}\n"
                f"Dimensione: {size_mb:.2f} MB",
            )

    def _on_close(self):
        self._stop_embedded_player(clear_label=False)
        if self.active_recordings:
            n = len(self.active_recordings)
            if not messagebox.askyesno(
                "Timer o registrazioni attive",
                f"Ci sono {n} timer o registrazioni video attive. Vuoi fermarle tutte e uscire?",
            ):
                return
            for rec in list(self.active_recordings.values()):
                rec["stop_event"].set()
                proc = rec.get("proc")
                if proc and proc.poll() is None:
                    try:
                        proc.terminate()
                    except Exception:
                        pass
        self._save_config()
        self.stop_requested = True
        self.root.destroy()

    def _browse_epg_file(self):
        path = filedialog.askopenfilename(
            title="Seleziona file EPG XMLTV",
            filetypes=[("File XMLTV", "*.xml *.gz"), ("Tutti i file", "*.*")],
        )
        if path:
            self.epg_source_var.set(path)
            self._start_epg_load(silent=False)

    def _split_epg_sources(self, raw_src):
        if not raw_src:
            return []
        if os.path.isfile(raw_src.strip()):
            return [raw_src.strip()]
        parts = [p.strip() for p in re.split(r"[,;\n]+", raw_src) if p.strip()]
        return parts

    def _start_epg_load(self, silent=False):
        raw_src = self.epg_source_var.get().strip()
        sources = self._split_epg_sources(raw_src)
        if not sources:
            if not silent:
                messagebox.showwarning(
                    "EPG mancante",
                    "Inserisci uno o più URL XMLTV (separati da virgola) oppure seleziona un file .xml / .xml.gz locale.",
                )
            return

        self.load_epg_btn.config(state=tk.DISABLED)
        self._style_single_button(self.load_epg_btn)
        thread = threading.Thread(target=self._epg_worker, args=(sources, silent), daemon=True)
        thread.start()

    def _epg_worker(self, sources, silent):
        errors = []
        epg_channels = {}
        epg_name_to_id = {}
        epg_smart_to_id = {}
        epg_programmes = {}

        for src in sources:
            try:
                if src.lower().startswith(("http://", "https://")):
                    req = urllib.request.Request(src, headers={"User-Agent": self.default_ua})
                    with urllib.request.urlopen(req, timeout=25, context=self.ssl_ctx) as resp:
                        raw_bytes = resp.read()
                else:
                    with open(src, "rb") as f:
                        raw_bytes = f.read()

                if raw_bytes[:2] == b"\x1f\x8b" or src.lower().endswith(".gz"):
                    xml_bytes = gzip.decompress(raw_bytes)
                else:
                    xml_bytes = raw_bytes

                root_xml = ET.fromstring(xml_bytes)

                for ch_el in root_xml.findall("channel"):
                    cid = (ch_el.get("id") or "").strip()
                    if not cid:
                        continue
                    disp_names = [
                        dn.text.strip() for dn in ch_el.findall("display-name") if dn.text and dn.text.strip()
                    ]
                    label = disp_names[0] if disp_names else cid
                    if cid not in epg_channels:
                        epg_channels[cid] = label
                    epg_name_to_id.setdefault(normalize_key(cid), cid)
                    sk_cid = smart_channel_key(cid)
                    if sk_cid:
                        epg_smart_to_id.setdefault(sk_cid, cid)
                    for dn in disp_names:
                        epg_name_to_id.setdefault(normalize_key(dn), cid)
                        sk_dn = smart_channel_key(dn)
                        if sk_dn:
                            epg_smart_to_id.setdefault(sk_dn, cid)

                for prog_el in root_xml.findall("programme"):
                    cid = (prog_el.get("channel") or "").strip()
                    if not cid:
                        continue
                    start_dt = parse_xmltv_datetime(prog_el.get("start"))
                    stop_dt = parse_xmltv_datetime(prog_el.get("stop"))
                    title_el = prog_el.find("title")
                    desc_el = prog_el.find("desc")
                    title = title_el.text.strip() if (title_el is not None and title_el.text) else "Senza titolo"
                    desc = desc_el.text.strip() if (desc_el is not None and desc_el.text) else ""
                    epg_programmes.setdefault(cid, []).append((start_dt, stop_dt, title, desc))
            except Exception as e:
                errors.append(f"{src}: {e}")

        for cid in epg_programmes:
            epg_programmes[cid].sort(key=lambda x: x[0] or datetime.min.replace(tzinfo=timezone.utc))

        err_text = "\n".join(errors) if errors else None
        self.root.after(
            0,
            self._on_epg_loaded,
            epg_channels,
            epg_name_to_id,
            epg_smart_to_id,
            epg_programmes,
            err_text,
            silent,
        )

    def _on_epg_loaded(self, epg_channels, epg_name_to_id, epg_smart_to_id, epg_programmes, err, silent):
        self.load_epg_btn.config(state=tk.NORMAL)
        self._style_single_button(self.load_epg_btn)
        if err and not epg_channels:
            if not silent:
                messagebox.showerror("Errore caricamento EPG", f"Impossibile caricare o analizzare le guide EPG:\n{err}")
            return

        self.epg_channels = epg_channels
        self.epg_name_to_id = epg_name_to_id
        self.epg_smart_to_id = epg_smart_to_id
        self.epg_programmes = epg_programmes

        self._match_channels_with_epg(use_smart_fallback=True)
        self._refresh_tree()
        self._update_stats()

        if not silent:
            tot_progs = sum(len(v) for v in epg_programmes.values())
            warn_part = f"\n\nAvvisi su alcune sorgenti:\n{err}" if err else ""
            messagebox.showinfo(
                "EPG Caricata",
                f"Guide XMLTV caricate con successo!\n"
                f"- Canali nella guida: {len(epg_channels)}\n"
                f"- Eventi / programmi letti: {tot_progs}{warn_part}",
            )

    def _match_channels_with_epg(self, use_smart_fallback=False):
        now = datetime.now().astimezone()
        for ch in self.channels:
            matched_id = None
            tvg_id = ch.get("tvg_id", "")
            tvg_name = ch.get("tvg_name", "")

            if tvg_id and tvg_id in self.epg_channels:
                matched_id = tvg_id
            elif tvg_id and normalize_key(tvg_id) in self.epg_name_to_id:
                matched_id = self.epg_name_to_id[normalize_key(tvg_id)]
            elif tvg_name and normalize_key(tvg_name) in self.epg_name_to_id:
                matched_id = self.epg_name_to_id[normalize_key(tvg_name)]
            elif normalize_key(ch["name"]) in self.epg_name_to_id:
                matched_id = self.epg_name_to_id[normalize_key(ch["name"])]
            elif use_smart_fallback:
                sk = smart_channel_key(ch["name"])
                if sk and sk in self.epg_smart_to_id:
                    matched_id = self.epg_smart_to_id[sk]
                    if not ch.get("tvg_id"):
                        ch["tvg_id"] = matched_id

            ch["epg_matched_id"] = matched_id
            if not matched_id:
                ch["epg_text"] = f"tvg-id: {tvg_id}" if tvg_id else "Non abbinato"
                continue

            progs = self.epg_programmes.get(matched_id, [])
            current_prog = None
            next_prog = None
            for start_dt, stop_dt, title, _ in progs:
                if start_dt and stop_dt and start_dt <= now <= stop_dt and current_prog is None:
                    current_prog = (start_dt, stop_dt, title)
                elif start_dt and start_dt > now and next_prog is None:
                    next_prog = (start_dt, stop_dt, title)
                if current_prog and next_prog:
                    break

            if current_prog:
                s_str = current_prog[0].strftime("%H:%M")
                e_str = current_prog[1].strftime("%H:%M")
                if next_prog:
                    n_str = next_prog[0].strftime("%H:%M")
                    ch["epg_text"] = f"[{s_str}-{e_str}] {current_prog[2]} | Poi {n_str}: {next_prog[2]}"
                else:
                    ch["epg_text"] = f"[{s_str}-{e_str}] {current_prog[2]}"
            elif progs:
                ch["epg_text"] = f"OK ({len(progs)} eventi)"
            else:
                ch["epg_text"] = f"ID OK ({matched_id})"

    def _show_channel_epg_dialog(self):
        sel = self._get_selected_channels()
        if not sel:
            return
        ch = sel[0]
        cid = ch.get("epg_matched_id")
        if not cid or cid not in self.epg_programmes:
            if messagebox.askyesno(
                "Nessun dato EPG",
                f"Nessuna programmazione trovata per '{ch['name']}'.\n"
                "Vuoi aprire la finestra di modifica per associare manualmente un canale EPG?",
            ):
                self._open_edit_channel_dialog()
            return

        win = tk.Toplevel(self.root)
        win.title(f"Guida EPG - {ch['name']} ({cid})")
        win.geometry("640x420")
        win.transient(self.root)

        txt = tk.Text(win, wrap=tk.WORD, padx=10, pady=10, font=("Segoe UI", 9))
        txt.pack(fill=tk.BOTH, expand=True)

        now = datetime.now().astimezone()
        progs = self.epg_programmes[cid]
        for start_dt, stop_dt, title, desc in progs[:60]:
            s_str = start_dt.strftime("%d/%m %H:%M") if start_dt else "??:??"
            e_str = stop_dt.strftime("%H:%M") if stop_dt else "??:??"
            marker = " >>> IN ONDA ORA <<<" if (start_dt and stop_dt and start_dt <= now <= stop_dt) else ""
            txt.insert(tk.END, f"[{s_str} - {e_str}] {title}{marker}\n")
            if desc:
                txt.insert(tk.END, f"    {desc}\n")
            txt.insert(tk.END, "\n")
        txt.config(state=tk.DISABLED)

    def _auto_detect_player(self):
        self.detected_players = {"vlc": "", "ffplay": ""}
        vlc_path = shutil.which("vlc")
        if not vlc_path:
            for candidate in [
                r"C:\Program Files\VideoLAN\VLC\vlc.exe",
                r"C:\Program Files (x86)\VideoLAN\VLC\vlc.exe",
            ]:
                if os.path.isfile(candidate):
                    vlc_path = candidate
                    break
        self.detected_players["vlc"] = vlc_path or ""
        self.detected_players["ffplay"] = self._find_binary("ffplay.exe") or ""

        saved_exe = self.saved_cfg.get("player_exe", "").strip()
        choice = self.player_type_var.get()
        if saved_exe and os.path.isfile(saved_exe):
            self.detected_players[choice] = saved_exe
        self._on_player_type_change()

    def _on_player_type_change(self):
        choice = self.player_type_var.get()
        self.player_exe_var.set(self.detected_players.get(choice, ""))
        self._refresh_ffmpeg_badge()

    def _browse_player(self):
        path = filedialog.askopenfilename(
            title="Seleziona eseguibile player",
            filetypes=[("Eseguibili", "*.exe"), ("Tutti i file", "*.*")],
        )
        if path:
            choice = self.player_type_var.get()
            self.detected_players[choice] = path
            self.player_exe_var.set(path)
            self._refresh_ffmpeg_badge()

    def _play_selected(self):
        sel = self._get_selected_channels()
        if not sel:
            messagebox.showinfo("Nessuna selezione", "Seleziona un canale nella tabella per avviarlo sul player esterno.")
            return

        ch = sel[0]
        exe = self.player_exe_var.get().strip()
        player = self.player_type_var.get()

        if not exe or not os.path.isfile(exe):
            messagebox.showerror(
                "Player non trovato",
                f"Impossibile trovare l'eseguibile per {player.upper()}.\nSelezionalo con il pulsante 'Sfoglia...'.",
            )
            return

        ua = ch["ua"] or self.default_ua
        referer = ch["referer"]
        url = ch["url"]

        cmd = [exe]
        if player == "vlc":
            if ua:
                cmd.append(f":http-user-agent={ua}")
            if referer:
                cmd.append(f":http-referrer={referer}")
            cmd.append(url)
        else:
            if ua:
                cmd.extend(["-user_agent", ua])
            if referer:
                cmd.extend(["-headers", f"Referer: {referer}\r\n"])
            cmd.extend(["-window_title", ch["name"], url])

        try:
            subprocess.Popen(cmd)
        except Exception as e:
            messagebox.showerror("Errore avvio player", f"Impossibile avviare il player:\n{e}")

    def _load_file(self):
        path = filedialog.askopenfilename(
            title="Seleziona playlist IPTV",
            filetypes=[("Playlist M3U / M3U8", "*.m3u *.m3u8"), ("Tutti i file", "*.*")],
        )
        if not path:
            return
        self.file_path_var.set(path)
        try:
            with open(path, "r", encoding="utf-8", errors="replace") as f:
                content = f.read()
            self._parse_m3u_content(content, preserve_epg_box=True)
        except Exception as e:
            messagebox.showerror("Errore lettura file", f"Impossibile aprire il file:\n{e}")

    def _set_preset_buttons_state(self, state):
        for btn in (
            self.load_url_btn,
            self.load_seca_btn,
            self.load_vassel_btn,
            self.load_pluto_btn,
            self.load_tvitava_btn,
            self.load_rakuten_btn,
            self.load_iptvorg_btn,
        ):
            btn.config(state=state)
            self._style_single_button(btn)

    def _load_m3u_from_url(self, silent=False):
        url = self.file_path_var.get().strip()
        if not url.lower().startswith(("http://", "https://")):
            if not silent:
                messagebox.showinfo(
                    "URL M3U non valido",
                    "Inserisci nella casella 'Playlist M3U' un indirizzo valido che inizi con http:// oppure https://",
                )
            return

        self._set_preset_buttons_state(tk.DISABLED)

        def worker():
            err = None
            content = ""
            try:
                req = urllib.request.Request(url, headers={"User-Agent": self.default_ua})
                with urllib.request.urlopen(req, timeout=18, context=self.ssl_ctx) as resp:
                    raw = resp.read()
                content = raw.decode("utf-8", errors="replace")
            except Exception as e:
                err = str(e)
            self.root.after(0, on_done, content, err)

        def on_done(content, err):
            self._set_preset_buttons_state(tk.NORMAL)
            if err:
                if not silent:
                    messagebox.showerror("Errore download M3U", f"Impossibile scaricare la playlist dall'URL:\n{err}")
                return
            self._parse_m3u_content(content, preserve_epg_box=True)

        threading.Thread(target=worker, daemon=True).start()

    def _open_paste_dialog(self):
        win = tk.Toplevel(self.root)
        win.title("Incolla contenuto M3U o elenco URL")
        win.geometry("620x400")
        win.transient(self.root)
        win.grab_set()

        ttk.Label(win, text="Incolla qui il testo della playlist M3U oppure uno o più URL (uno per riga):").pack(
            anchor=tk.W, padx=10, pady=(10, 5)
        )
        txt = tk.Text(win, wrap=tk.NONE, font=("Consolas", 9))
        txt.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))

        try:
            clip = self.root.clipboard_get()
            if clip:
                txt.insert("1.0", clip)
        except tk.TclError:
            pass

        def on_confirm():
            raw = txt.get("1.0", tk.END).strip()
            if raw:
                self.file_path_var.set("[Lista incollata]")
                self._parse_m3u_content(raw, preserve_epg_box=True)
            win.destroy()

        btn_row = ttk.Frame(win)
        btn_row.pack(fill=tk.X, padx=10, pady=(0, 10))
        ttk.Button(btn_row, text="Carica nella tabella", command=on_confirm).pack(side=tk.RIGHT)
        ttk.Button(btn_row, text="Annulla", command=win.destroy).pack(side=tk.RIGHT, padx=(0, 6))

    def _parse_m3u_content(self, content, preserve_epg_box=True):
        lines = [line.strip() for line in content.splitlines() if line.strip()]
        parsed = []
        self.m3u_header_epg = ""

        current_extinf = None
        current_name = None
        current_group = ""
        current_tvg_id = ""
        current_tvg_name = ""
        current_ua = ""
        current_ref = ""
        extra_opts = []

        for line in lines:
            if line.startswith("#EXTM3U"):
                m_epg = re.search(r'(?:url-tvg|x-tvg-url)\s*=\s*"([^"]+)"', line, re.IGNORECASE)
                if m_epg:
                    self.m3u_header_epg = m_epg.group(1).strip()
                    if not preserve_epg_box or not self.epg_source_var.get().strip():
                        self.epg_source_var.set(self.m3u_header_epg)
                continue
            elif line.startswith("#EXTINF:"):
                current_extinf = line
                m_grp = re.search(r'group-title\s*=\s*"([^"]*)"', line, re.IGNORECASE)
                if m_grp:
                    current_group = m_grp.group(1).strip()
                m_tid = re.search(r'tvg-id\s*=\s*"([^"]*)"', line, re.IGNORECASE)
                if m_tid:
                    current_tvg_id = m_tid.group(1).strip()
                m_tname = re.search(r'tvg-name\s*=\s*"([^"]*)"', line, re.IGNORECASE)
                if m_tname:
                    current_tvg_name = m_tname.group(1).strip()
                if "," in line:
                    current_name = line.split(",", 1)[1].strip()
                else:
                    current_name = "Canale senza nome"
            elif line.startswith("#EXTVLCOPT:"):
                opt = line.split(":", 1)[1].strip()
                low = opt.lower()
                if low.startswith("http-user-agent="):
                    current_ua = opt.split("=", 1)[1].strip()
                elif low.startswith("http-referrer="):
                    current_ref = opt.split("=", 1)[1].strip()
                else:
                    extra_opts.append(line)
            elif line.startswith("#EXTGRP:"):
                current_group = line.split(":", 1)[1].strip()
                extra_opts.append(line)
            elif line.startswith("#"):
                continue
            else:
                raw_url = line
                clean_url = raw_url
                ua = current_ua
                ref = current_ref

                if "|" in raw_url:
                    base_part, pipe_part = raw_url.split("|", 1)
                    clean_url = base_part.strip()
                    for kv in pipe_part.split("&"):
                        if "=" in kv:
                            k, v = kv.split("=", 1)
                            kl = k.strip().lower()
                            val = urllib.parse.unquote(v.strip())
                            if kl == "user-agent" and not ua:
                                ua = val
                            elif kl in ("referer", "referrer") and not ref:
                                ref = val

                idx = len(parsed) + 1
                self.uid_counter += 1
                name = current_name or f"Canale {idx}"
                country = detect_country(current_extinf, current_group, name, clean_url)
                epg_label = f"tvg-id: {current_tvg_id}" if current_tvg_id else "N/D"

                parsed.append(
                    {
                        "uid": self.uid_counter,
                        "orig_idx": idx,
                        "idx": idx,
                        "favorite": False,
                        "name": name,
                        "country": country,
                        "quality": "-",
                        "tvg_id": current_tvg_id,
                        "tvg_name": current_tvg_name,
                        "epg_matched_id": None,
                        "epg_text": epg_label,
                        "extinf": current_extinf or f"#EXTINF:-1,{name}",
                        "url": clean_url,
                        "raw_url": raw_url,
                        "ua": ua,
                        "referer": ref,
                        "extra_opts": list(extra_opts),
                        "status": "PENDING",
                        "latency": "-",
                        "detail": "In attesa",
                    }
                )

                current_extinf = None
                current_name = None
                current_group = ""
                current_tvg_id = ""
                current_tvg_name = ""
                current_ua = ""
                current_ref = ""
                extra_opts = []

        self.channels = parsed
        if self.epg_channels:
            self._match_channels_with_epg(use_smart_fallback=True)
        self._update_country_filter_options()
        self.progress["value"] = 0
        self.progress["maximum"] = max(1, len(self.channels))
        self._refresh_tree()
        self._update_stats()

    def _update_country_filter_options(self):
        countries = sorted({ch["country"] for ch in self.channels if ch["country"]})
        options = ["Tutti i paesi"] + countries
        self.country_combo["values"] = options
        if self.country_filter_var.get() not in options:
            self.country_filter_var.set("Tutti i paesi")

    def _matches_filters(self, ch):
        flt = self.filter_var.get()
        if flt != "ALL" and ch["status"] != flt:
            return False
        if self.fav_only_var.get() and not ch.get("favorite", False):
            return False
        c_flt = self.country_filter_var.get()
        if c_flt and c_flt != "Tutti i paesi" and ch["country"] != c_flt:
            return False
        q = self.search_query_var.get().strip().lower()
        if q:
            if q not in ch["name"].lower():
                return False
        return True

    def _get_row_display_values_and_tag(self, ch, row_pos=0):
        rec_state = self._get_channel_rec_state(ch["uid"])
        if rec_state == "RECORDING":
            status_label = "● REC"
            base_tag = "RECORDING"
        elif rec_state == "WAITING":
            status_label = "⏰ TIMER"
            base_tag = "WAITING"
        else:
            status_label = {
                "ONLINE": "● ONLINE",
                "OFFLINE": "✖ OFFLINE",
                "PENDING": "○ ATTESA",
            }.get(ch["status"], ch["status"])
            base_tag = ch["status"]

        tag = f"{base_tag}_ALT" if (row_pos % 2 == 1) else base_tag
        fav_star = "★" if ch.get("favorite", False) else "☆"
        vals = (
            ch["idx"],
            fav_star,
            status_label,
            ch["country"],
            ch["name"],
            ch.get("quality", "-"),
            ch["epg_text"],
            ch["latency"],
            ch["detail"],
            ch["url"],
        )
        return vals, tag

    def _update_channel_row_visual(self, ch):
        iid = str(ch["uid"])
        if self.tree.exists(iid):
            row_pos = self.tree.index(iid)
            vals, tag = self._get_row_display_values_and_tag(ch, row_pos=row_pos)
            self.tree.item(iid, values=vals, tags=(tag,))

    def _refresh_tree(self):
        self.tree.delete(*self.tree.get_children())

        row_pos = 0
        for ch in self.channels:
            if not self._matches_filters(ch):
                continue
            vals, tag = self._get_row_display_values_and_tag(ch, row_pos=row_pos)
            self.tree.insert(
                "",
                tk.END,
                iid=str(ch["uid"]),
                values=vals,
                tags=(tag,),
            )
            row_pos += 1

    def _update_stats(self):
        total = len(self.channels)
        online = sum(1 for c in self.channels if c["status"] == "ONLINE")
        offline = sum(1 for c in self.channels if c["status"] == "OFFLINE")
        epg_ok = sum(1 for c in self.channels if c.get("epg_matched_id") or c.get("tvg_id"))
        fav_cnt = sum(1 for c in self.channels if c.get("favorite"))

        parts = [
            f"📊 Totale: {total}",
            f"🟢 Online: {online}",
            f"🔴 Offline: {offline}",
            f"🗓️ EPG: {epg_ok}",
            f"★ Pref: {fav_cnt}",
        ]
        if self.is_running:
            parts.append("⚡ Scansione...")

        rec_count = len(self.active_recordings)
        if rec_count == 1:
            rec = next(iter(self.active_recordings.values()))
            now = time.time()
            label_rec = f"{rec['channel_name']} - {rec['prog_title']}" if rec["prog_title"] else rec["channel_name"]
            if rec["state"] == "WAITING":
                rem_start = max(0, int(rec["scheduled_start"] - now))
                start_hhmm = datetime.fromtimestamp(rec["scheduled_start"]).strftime("%H:%M")
                parts.append(f"⏰ TIMER {label_rec}: avvio {start_hhmm} (-{format_duration(rem_start)})")
            else:
                elapsed = int(now - rec["start_time"])
                mb = 0.0
                if os.path.isfile(rec["file_path"]):
                    mb = os.path.getsize(rec["file_path"]) / (1024 * 1024)
                if rec["limit_seconds"] > 0:
                    rem = max(0, rec["limit_seconds"] - elapsed)
                    time_info = f"{format_duration(elapsed)}/{format_duration(rec['limit_seconds'])} (-{format_duration(rem)})"
                else:
                    time_info = format_duration(elapsed)
                parts.append(f"🔴 REC {label_rec}: {time_info} ({mb:.1f} MB)")
        elif rec_count > 1:
            n_rec = sum(1 for r in self.active_recordings.values() if r["state"] == "RECORDING")
            n_wait = sum(1 for r in self.active_recordings.values() if r["state"] == "WAITING")
            total_mb = sum(
                (os.path.getsize(r["file_path"]) / (1024 * 1024))
                for r in self.active_recordings.values()
                if r["state"] == "RECORDING" and os.path.isfile(r["file_path"])
            )
            parts.append(f"🔴 REC: {n_rec} | ⏰ TIMER: {n_wait} ({total_mb:.1f} MB)")

        self.stats_var.set("  •  ".join(parts))

    def _read_bounded(self, resp, max_bytes, deadline):
        chunks = []
        total = 0
        sock = None
        try:
            fp = getattr(resp, "fp", None)
            raw_fp = getattr(fp, "raw", None)
            sock = getattr(raw_fp, "_sock", None)
        except Exception:
            sock = None

        while total < max_bytes:
            if self.stop_requested:
                break
            rem = deadline - time.perf_counter()
            if rem <= 0:
                raise socket.timeout("Timeout lettura dati flusso")
            if sock is not None:
                try:
                    sock.settimeout(max(0.2, rem))
                except Exception:
                    pass
            to_read = min(1024, max_bytes - total)
            part = resp.read(to_read)
            if not part:
                break
            chunks.append(part)
            total += len(part)
        return b"".join(chunks)

    def _check_single_channel(self, ch, timeout, deep_check, probe_quality, session_id):
        if self.stop_requested or session_id != self.check_session_id:
            return ch

        url = ch["url"]
        ua = ch["ua"] or self.default_ua
        referer = ch["referer"]

        if not url.lower().startswith(("http://", "https://")):
            ch["status"] = "OFFLINE"
            ch["latency"] = "-"
            ch["quality"] = "-"
            ch["detail"] = "Protocollo non HTTP(S)"
            return ch

        headers = {
            "User-Agent": ua,
            "Accept": "*/*",
            "Connection": "close",
        }
        if referer:
            headers["Referer"] = referer

        start_t = time.perf_counter()
        deadline = start_t + timeout
        resp = None
        try:
            req = urllib.request.Request(url, headers=headers, method="GET")
            resp = urllib.request.urlopen(req, timeout=timeout, context=self.ssl_ctx)
            code = resp.getcode()
            content_type = (resp.headers.get("Content-Type") or "").lower()

            if code not in (200, 206):
                elapsed_ms = int((time.perf_counter() - start_t) * 1000)
                ch["status"] = "OFFLINE"
                ch["latency"] = f"{elapsed_ms} ms"
                ch["quality"] = "-"
                ch["detail"] = f"HTTP {code}"
                return ch

            target_bytes = 4096 if deep_check else 16
            chunk = self._read_bounded(resp, target_bytes, deadline)
            elapsed_ms = int((time.perf_counter() - start_t) * 1000)

            if deep_check:
                if not chunk:
                    ch["status"] = "OFFLINE"
                    ch["latency"] = f"{elapsed_ms} ms"
                    ch["quality"] = "-"
                    ch["detail"] = "Risposta vuota (0 byte)"
                    return ch

                text_sample = chunk.decode("utf-8", errors="ignore").lstrip()
                is_m3u_url = ".m3u8" in url.lower() or ".m3u" in url.lower() or "mpegurl" in content_type

                if text_sample.startswith("#EXTM3U"):
                    if "#EXT-X-ENDLIST" in text_sample and "#EXTINF" not in text_sample:
                        ch["status"] = "OFFLINE"
                        ch["latency"] = f"{elapsed_ms} ms"
                        ch["quality"] = "-"
                        ch["detail"] = "Manifest vuoto / scaduto"
                    else:
                        ch["status"] = "ONLINE"
                        ch["latency"] = f"{elapsed_ms} ms"
                        ch["detail"] = f"HTTP {code} (HLS valido)"
                        q_hls = parse_hls_quality(text_sample) if probe_quality else ""
                        if q_hls:
                            ch["quality"] = q_hls
                        elif probe_quality and not self.stop_requested:
                            ch["quality"] = self._probe_stream_resolution(url, ua, referer, timeout) or "HLS"
                        else:
                            ch["quality"] = "HLS"
                elif text_sample.lower().startswith("<!doctype html") or text_sample.lower().startswith("<html"):
                    ch["status"] = "OFFLINE"
                    ch["latency"] = f"{elapsed_ms} ms"
                    ch["quality"] = "-"
                    ch["detail"] = "Pagina HTML (no stream)"
                elif is_m3u_url and "#EXT" not in text_sample:
                    ch["status"] = "OFFLINE"
                    ch["latency"] = f"{elapsed_ms} ms"
                    ch["quality"] = "-"
                    ch["detail"] = "Manifest non valido"
                else:
                    ch["status"] = "ONLINE"
                    ch["latency"] = f"{elapsed_ms} ms"
                    ch["detail"] = f"HTTP {code} (Flusso attivo)"
                    if probe_quality and not self.stop_requested:
                        ch["quality"] = self._probe_stream_resolution(url, ua, referer, timeout) or "Stream"
                    else:
                        ch["quality"] = "Stream"
            else:
                ch["status"] = "ONLINE"
                ch["latency"] = f"{elapsed_ms} ms"
                ch["detail"] = f"HTTP {code}"
                if probe_quality and not self.stop_requested:
                    ch["quality"] = self._probe_stream_resolution(url, ua, referer, timeout) or "-"

        except urllib.error.HTTPError as e:
            elapsed_ms = int((time.perf_counter() - start_t) * 1000)
            ch["status"] = "OFFLINE"
            ch["latency"] = f"{elapsed_ms} ms"
            ch["quality"] = "-"
            ch["detail"] = f"HTTP {e.code} ({e.reason})"
        except urllib.error.URLError as e:
            ch["status"] = "OFFLINE"
            ch["latency"] = "-"
            ch["quality"] = "-"
            reason = str(getattr(e, "reason", e))
            if "timed out" in reason.lower():
                ch["detail"] = "Timeout connessione"
            else:
                ch["detail"] = f"Errore rete: {reason[:32]}"
        except (socket.timeout, TimeoutError):
            ch["status"] = "OFFLINE"
            ch["latency"] = "-"
            ch["quality"] = "-"
            ch["detail"] = "Timeout lettura flusso"
        except Exception as e:
            ch["status"] = "OFFLINE"
            ch["latency"] = "-"
            ch["quality"] = "-"
            ch["detail"] = f"Errore: {str(e)[:35]}"
        finally:
            if resp is not None:
                try:
                    resp.close()
                except Exception:
                    pass

        return ch

    def _start_check(self, subset=None):
        if self.is_running:
            return
        targets = subset if subset is not None else self.channels
        if not targets:
            messagebox.showwarning("Nessun canale", "Carica o incolla prima una playlist M3U.")
            return

        for ch in targets:
            ch["status"] = "PENDING"
            ch["latency"] = "-"
            ch["quality"] = "-"
            ch["detail"] = "Verifica..."

        self.check_session_id += 1
        current_session = self.check_session_id

        with self.ui_lock:
            self.pending_updates.clear()
            self.completed_count = 0
            self.total_targets = len(targets)
            self.scan_finished_flag = False

        self.is_running = True
        self.stop_requested = False
        self.start_btn.config(state=tk.DISABLED)
        self.retry_offline_btn.config(state=tk.DISABLED)
        self.stop_btn.config(state=tk.NORMAL)
        self._style_single_button(self.start_btn)
        self._style_single_button(self.retry_offline_btn)
        self._style_single_button(self.stop_btn)
        self.progress["value"] = 0
        self.progress["maximum"] = len(targets)

        self._refresh_tree()
        self._update_stats()

        timeout = max(2, int(self.timeout_var.get()))
        workers = max(1, min(30, int(self.workers_var.get())))
        deep_check = self.deep_check_var.get()
        probe_quality = self.probe_quality_var.get()

        self.root.after(120, self._poll_ui_updates, current_session)

        thread = threading.Thread(
            target=self._worker_pool,
            args=(list(targets), timeout, workers, deep_check, probe_quality, current_session),
            daemon=True,
        )
        thread.start()

    def _stop_check(self):
        if self.is_running:
            self.stop_requested = True
            self.check_session_id += 1
            self.is_running = False
            self.start_btn.config(state=tk.NORMAL)
            self.retry_offline_btn.config(state=tk.NORMAL)
            self.stop_btn.config(state=tk.DISABLED)
            self._style_single_button(self.start_btn)
            self._style_single_button(self.retry_offline_btn)
            self._style_single_button(self.stop_btn)
            for ch in self.channels:
                if ch["status"] == "PENDING" and ch["detail"] == "Verifica...":
                    ch["detail"] = "Interrotto"
            self._refresh_tree()
            self._update_stats()

    def _worker_pool(self, targets, timeout, workers, deep_check, probe_quality, session_id):
        executor = concurrent.futures.ThreadPoolExecutor(max_workers=workers)
        try:
            futures = [
                executor.submit(self._check_single_channel, ch, timeout, deep_check, probe_quality, session_id)
                for ch in targets
            ]
            for fut in concurrent.futures.as_completed(futures):
                if self.stop_requested or session_id != self.check_session_id:
                    for f in futures:
                        f.cancel()
                    break
                try:
                    ch = fut.result()
                except Exception:
                    continue
                with self.ui_lock:
                    if session_id == self.check_session_id:
                        self.pending_updates.append(ch)
                        self.completed_count += 1
        finally:
            executor.shutdown(wait=False, cancel_futures=True)
            with self.ui_lock:
                if session_id == self.check_session_id:
                    self.scan_finished_flag = True

    def _poll_ui_updates(self, session_id):
        if session_id != self.check_session_id:
            return

        with self.ui_lock:
            batch = list(self.pending_updates)
            self.pending_updates.clear()
            completed = self.completed_count
            finished = self.scan_finished_flag

        if batch:
            self.progress["value"] = completed
            need_full_refresh = False
            for ch in batch:
                iid = str(ch["uid"])
                visible = self._matches_filters(ch)
                if self.tree.exists(iid):
                    if not visible:
                        self.tree.delete(iid)
                    else:
                        row_pos = self.tree.index(iid)
                        vals, tag = self._get_row_display_values_and_tag(ch, row_pos=row_pos)
                        self.tree.item(iid, values=vals, tags=(tag,))
                elif visible:
                    need_full_refresh = True

            if need_full_refresh:
                self._refresh_tree()
            self._update_stats()

        if finished:
            self.is_running = False
            self.stop_requested = False
            self.start_btn.config(state=tk.NORMAL)
            self.retry_offline_btn.config(state=tk.NORMAL)
            self.stop_btn.config(state=tk.DISABLED)
            self._style_single_button(self.start_btn)
            self._style_single_button(self.retry_offline_btn)
            self._style_single_button(self.stop_btn)
            self._update_stats()
        elif self.is_running:
            self.root.after(120, self._poll_ui_updates, session_id)

    def _show_context_menu(self, event):
        row_id = self.tree.identify_row(event.y)
        if row_id:
            if row_id not in self.tree.selection():
                self.tree.selection_set(row_id)
            self.ctx_menu.post(event.x_root, event.y_root)

    def _get_selected_channels(self):
        selected_ids = set(self.tree.selection())
        return [ch for ch in self.channels if str(ch["uid"]) in selected_ids]

    def _copy_selected_url(self):
        sel = self._get_selected_channels()
        if not sel:
            return
        urls = "\n".join(ch["url"] for ch in sel)
        self.root.clipboard_clear()
        self.root.clipboard_append(urls)

    def _recheck_selected(self):
        sel = self._get_selected_channels()
        if sel and not self.is_running:
            self._start_check(subset=sel)

    def _remove_selected(self):
        if self.is_running:
            return
        selected_ids = set(self.tree.selection())
        if not selected_ids:
            return
        self.channels = [ch for ch in self.channels if str(ch["uid"]) not in selected_ids]
        for i, ch in enumerate(self.channels, start=1):
            ch["idx"] = i
        self._update_country_filter_options()
        self._refresh_tree()
        self._update_stats()

    def _export_m3u(self, mode="online"):
        if not self.channels:
            messagebox.showwarning("Lista vuota", "Nessun canale da esportare.")
            return

        c_flt = self.country_filter_var.get()
        to_export = []
        for ch in self.channels:
            if mode == "online":
                if ch["status"] != "ONLINE":
                    continue
                if c_flt and c_flt != "Tutti i paesi" and ch["country"] != c_flt:
                    continue
                if self.fav_only_var.get() and not ch.get("favorite", False):
                    continue
            elif mode == "epg":
                if not (ch.get("epg_matched_id") or ch.get("tvg_id")):
                    continue
                if ch["status"] == "OFFLINE":
                    continue
            elif mode == "view":
                if not self._matches_filters(ch):
                    continue
            to_export.append(ch)

        if not to_export:
            messagebox.showwarning(
                "Nessun canale valido",
                "Non ci sono canali corrispondenti ai criteri selezionati da esportare.",
            )
            return

        to_export.sort(key=lambda c: 0 if c.get("favorite", False) else 1)

        name_map = {
            "online": "playlist_valida.m3u",
            "epg": "playlist_con_epg.m3u",
            "view": "playlist_filtrata.m3u",
        }
        default_name = name_map.get(mode, "playlist_valida.m3u")
        save_path = filedialog.asksaveasfilename(
            title="Salva playlist M3U",
            defaultextension=".m3u",
            initialfile=default_name,
            filetypes=[("Playlist M3U", "*.m3u"), ("Playlist M3U8", "*.m3u8"), ("Tutti i file", "*.*")],
        )
        if not save_path:
            return

        raw_epg = self.epg_source_var.get().strip() or self.m3u_header_epg
        epg_urls = [u for u in self._split_epg_sources(raw_epg) if u.lower().startswith(("http://", "https://"))]
        if epg_urls:
            header = f'#EXTM3U url-tvg="{",".join(epg_urls)}"'
        else:
            header = "#EXTM3U"

        out_lines = [header]
        for ch in to_export:
            matched_id = ch.get("epg_matched_id") or ch.get("tvg_id", "")
            extinf_line = update_extinf_line(ch.get("extinf", ""), ch["name"], matched_id)
            out_lines.append(extinf_line)
            for opt in ch["extra_opts"]:
                out_lines.append(opt)
            if ch["ua"]:
                out_lines.append(f"#EXTVLCOPT:http-user-agent={ch['ua']}")
            if ch["referer"]:
                out_lines.append(f"#EXTVLCOPT:http-referrer={ch['referer']}")
            out_lines.append(ch["url"])

        try:
            with open(save_path, "w", encoding="utf-8") as f:
                f.write("\n".join(out_lines) + "\n")
            messagebox.showinfo(
                "Esportazione completata",
                f"Esportati {len(to_export)} canali in:\n{save_path}",
            )
        except Exception as e:
            messagebox.showerror("Errore salvataggio", f"Impossibile salvare il file:\n{e}")


if __name__ == "__main__":
    root = tk.Tk()
    app = IPTVCheckerApp(root)
    root.mainloop()
