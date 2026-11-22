#!/usr/bin/env python3
"""
Mudlet 4.15.1 "Lite" feature-removal patch.
Applied to a fresh checkout of Mudlet/Mudlet @ Mudlet-4.15.1.

Strategy (keeps the build reliable):
  - Updater / 3D Mapper / variable splash / fonts : WITH_* env vars (in workflow)
  - TextToSpeech : `QT -= texttospeech` + no module installed
  - Hunspell     : header stubs (no-op) + unlink real lib + no DLL packaged
  - IRC / Discord: menu entries removed from main_window.ui and their slots
                   turned into no-ops, so the features are unreachable. The
                   classes still compile/link (they are deeply intertwined with
                   Host/mudlet.cpp), which avoids fragile source surgery.

Usage:
  python apply_lite_patch.py <path-to-Mudlet-checkout>
"""

import os
import re
import sys

ROOT = os.path.abspath(sys.argv[1]) if len(sys.argv) > 1 else os.getcwd()
log = []


def read(rel):
    p = os.path.join(ROOT, rel)
    if not os.path.exists(p):
        raise FileNotFoundError(f"Expected file missing: {p}")
    with open(p, "r", encoding="utf-8", errors="surrogateescape") as f:
        return f.read()


def write(rel, text):
    p = os.path.join(ROOT, rel)
    with open(p, "w", encoding="utf-8", errors="surrogateescape", newline="") as f:
        f.write(text)


def sub(rel, pattern, repl, flags=0, required=False, label=None):
    src = read(rel)
    new, n = re.subn(pattern, repl, src, flags=flags)
    tag = label or pattern
    if n == 0:
        if required:
            raise RuntimeError(f"[FATAL] no match for {tag!r} in {rel}")
        log.append(f"[WARN] no match for {tag!r} in {rel}")
    else:
        log.append(f"[OK]   {tag!r}: {n} replacement(s) in {rel}")
        write(rel, new)
    return n


# ---------------------------------------------------------------------------
# 1. src/mudlet.pro -- build-level changes
# ---------------------------------------------------------------------------
PRO = "src/mudlet.pro"

# Comment out the TextToSpeech qtHaveModule block (best effort); the
# authoritative removal is `QT -= texttospeech` appended below.
sub(PRO, r"qtHaveModule\s*\(\s*texttospeech\s*\)\s*\{[^}]*\}",
    "# LITE: TextToSpeech module disabled", re.S, required=False,
    label="texttospeech module block")

# --- MSYS2/UCRT64 library name adaptation ----------------------------------
# Mudlet 4.15.1's qmake expects the appveyor MinGW layout. Under MSYS2 UCRT64:
#   * PCRE import lib is libpcre.dll.a -> link flag must be -lpcre (not -lpcre-1)
#   * lua51 import lib is liblua5.1.dll.a, header in include/lua5.1 (the
#     MSYS2 branch of mudlet.pro already uses -llua5.1 / include/lua5.1, which
#     is selected by WITH_MAIN_BUILD_SYSTEM=NO in the workflow).
sub(PRO, r"-lpcre-1", "-lpcre", label="pcre link name -> -lpcre")

STUBS = os.path.abspath(os.path.join(os.path.dirname(__file__), "stubs")).replace("\\", "/")
append = [
    "",
    "# ===== LITE build: feature removal (appended by apply_lite_patch.py) =====",
    "# Disable the Qt TextToSpeech module:",
    "QT -= texttospeech",
    "",
    "# Drop Hunspell from the link line and redirect its headers to no-op stubs:",
    "PKGCONFIG -= hunspell",
    "LIBS -= -lhunspell-1.6 -lhunspell-1.7 -llibhunspell-1.7 -lhunspell",
    "INCLUDEPATH = " + STUBS + " $$INCLUDEPATH",
    "",
    "# MSYS2's GCC defaults to C23, which rejects old-style function pointer",
    "# declarations in bundled Oniguruma (st.c/regparse.c). Force gnu11, which",
    "# is what Mudlet 4.15.1 was originally built against:",
    "QMAKE_CFLAGS += -std=gnu11",
    "QMAKE_CXXFLAGS += -std=gnu++17",
    "",
    "# Reduce compiler memory usage: Mudlet forces -O3, which makes cc1plus",
    "# consume 4-5GB on the big files and exhausts the GitHub runner's 7GB RAM.",
    "# -O1 cuts memory usage roughly in half with negligible impact on a GUI app:",
    "QMAKE_CXXFLAGS_RELEASE -= -O3",
    "QMAKE_CXXFLAGS_RELEASE -= -O2",
    "QMAKE_CXXFLAGS_RELEASE += -O1",
    "QMAKE_CFLAGS_RELEASE -= -O3",
    "QMAKE_CFLAGS_RELEASE -= -O2",
    "QMAKE_CFLAGS_RELEASE += -O1",
    "# =======================================================================",
    "",
]
with open(os.path.join(ROOT, PRO), "a", encoding="utf-8") as _f:
    _f.write("\n".join(append))
log.append(f"[OK]   appended LITE config to {PRO} (stub dir: {STUBS})")

# ---------------------------------------------------------------------------
# 2. src/ui/main_window.ui -- remove IRC/Discord menu entries
# ---------------------------------------------------------------------------
UI = "src/ui/main_window.ui"
for action in ["actionIRC", "actionDiscord", "actionMudletDiscord", "actionLiveHelpChat",
               "dactionIRC", "dactionDiscord", "dactionMudletDiscord", "dactionLiveHelpChat"]:
    # Removing only <addaction .../> keeps the <action> definition, so uic
    # still generates ui->dactionIRC and mudlet.cpp keeps compiling.
    sub(UI, rf"\s*<addaction\s+name=\"{action}\"\s*/>\s*\n", "\n",
        required=False, label=f"menu entry {action}")

# ---------------------------------------------------------------------------
# 3. src/mudlet.cpp -- turn IRC/Discord slots into no-ops
# ---------------------------------------------------------------------------
CPP = "src/mudlet.cpp"

# Replace each slot body with a no-op. The body regex is non-greedy up to a
# closing brace at column 0 (Mudlet uses 4-space indentation for nested braces).
for slot in ["slot_irc", "slot_discord", "slot_mudlet_discord"]:
    pat = rf"(void mudlet::{slot}\(\)\s*\{{\n).*?(\n\}})"
    n = sub(CPP, pat, r"\1    // LITE: feature disabled\n\2", re.S,
            required=False, label=f"no-op {slot}")
    if n == 0:
        # Fallback: match a one-line or differently formatted definition.
        sub(CPP, rf"(void mudlet::{slot}\(\)\s*\{{)[^\n]*(\}})",
            r"\1 /* LITE: disabled */ \2", required=False,
            label=f"no-op {slot} (fallback)")

# Hide the Discord toolbar button (QToolButton created in mudlet::mudlet()).
# Keep all objects/actions alive to avoid null derefs; just don't show it.
sub(CPP, r"(mpButtonDiscord->setAutoRaise\(true\);)",
    r"\1\n    mpButtonDiscord->setVisible(false); // LITE: hide Discord toolbar button",
    required=False, label="hide Discord toolbar button")

# Restore the 4.11.3 whole-UI font. 4.15.1 dropped the global setFont(mainFont)
# and the tab-bar setFont() calls, so menus, tabs, buttons and dialogs fell back
# to the Windows system font. Re-add them for the 4.11.3 look.
# mpTabBar is created earlier in the constructor (well before this point), so
# it is safe to set its font here.
ui_font_pat = (
    r'    QFont mainFont = QFont\(qsl\("Bitstream Vera Sans Mono"\), 8, QFont::Normal\);\n'
    r'    mpWidget_profileContainer->setFont\(mainFont\);\n'
    r'    mpWidget_profileContainer->show\(\);'
)
ui_font_repl = (
    '    QFont mainFont = QFont(qsl("Bitstream Vera Sans Mono"), 8, QFont::Normal);\n'
    '    // LITE: restore the 4.11.3 UI font (removed upstream in 4.15.1)\n'
    '    setFont(mainFont);\n'
    '    mpWidget_profileContainer->setFont(mainFont);\n'
    '    QFont mdiFont = QFont(qsl("Bitstream Vera Sans Mono"), 8, QFont::Normal);\n'
    '    mpTabBar->setFont(mdiFont);\n'
    '    mpWidget_profileContainer->show();'
)
sub(CPP, ui_font_pat, ui_font_repl, required=True,
    label="restore 4.11.3 UI font (whole window + tab bar)")

# ---------------------------------------------------------------------------
# 4. src/TLuaInterpreter.cpp -- fix resetProfile Lua state leak (upstream #9110)
# ---------------------------------------------------------------------------
# resetProfile() calls initLuaGlobals() again on the same TLuaInterpreter.
# Without closing the previous state first, the whole Lua heap (scripts, room
# tables, closures, triggers) leaks on every reset. Upstream 4.21.0 fixed this
# by closing the old state before creating a new one. The constructor sets
# pGlobalLua = nullptr before the first initLuaGlobals() call, so the guard is
# safe on first use.
LUA = "src/TLuaInterpreter.cpp"
# 4.15.1 uses pGlobalLua = newstate(); (Mudlet's own wrapper). Newer versions
# use luaL_newstate(). Match either form.
fix_pat = (
    r"(void TLuaInterpreter::initLuaGlobals\(\)\s*\{\s*\n)"
    r"(\s*)(pGlobalLua\s*=\s*(?:newstate|luaL_newstate)\(\)\s*;)"
)
fix_repl = (
    r"\1"
    r"\2// FIX: close the previous Lua state to avoid leaking it on resetProfile()\n"
    r"\2if (pGlobalLua) {\n"
    r"\2    lua_close(pGlobalLua);\n"
    r"\2}\n"
    r"\2\3"
)
n = sub(LUA, fix_pat, fix_repl, required=True,
        label="close old lua_State in initLuaGlobals (leak fix)")
if n == 0:
    raise RuntimeError(
        "FATAL: could not locate 'pGlobalLua = newstate()/luaL_newstate();' in "
        "TLuaInterpreter::initLuaGlobals(). Refusing to build with the leak unfixed.")

print("\n".join(log))
print(f"\n[LITE PATCH] Applied to {ROOT}")
