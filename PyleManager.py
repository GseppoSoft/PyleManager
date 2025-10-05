from tkinter import *
from tkinter import ttk
import json
from tkinter import simpledialog
import shutil
import os
import easygui
from tkinter import filedialog
from tkinter import messagebox as mb

# current open pyle path (None when nothing loaded)
current_pyle_path = None
from pathlib import Path

USER_DOCS = Path.home() / 'Documents'
GSPM_PATH = USER_DOCS / 'GSPM'
GSPM_PATH.mkdir(parents=True, exist_ok=True)

# Configuration file for persistent settings
CONFIG_PATH = GSPM_PATH / 'pylemanager_config.json'

def load_config():
    if CONFIG_PATH.exists():
        try:
            with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return {}
    return {}

def save_config(cfg):
    try:
        with open(CONFIG_PATH, 'w', encoding='utf-8') as f:
            json.dump(cfg, f, indent=2)
    except Exception:
        pass

config = load_config()

def _in_gspm(path):
    # Check if the path is within the GSPM directory
    try:
        return Path(path).resolve().is_relative_to(GSPM_PATH.resolve())
    except Exception:
        try:
            return str(Path(path).resolve()).startswith(str(GSPM_PATH.resolve()))
        except Exception:
            return False

def open_window():
    read = easygui.fileopenbox(default=str(GSPM_PATH) + os.sep)
    return read

def open_pyle():
    global current_pyle_path
    string = open_window()
    if not string:
        return
    current_pyle_path = string
    try:
        with open(string, 'r', encoding='utf-8') as f:
            data = f.read()
            editor.delete('1.0', END)
            editor.insert('1.0', data)
            return
    except Exception:
        try:
            os.startfile(string)
        except Exception:
            mb.showinfo('confirmation', "Pyle not Found!")

def copy_pyle():
    source1 = open_window()
    if not source1:
        return
    if not _in_gspm(source1):
        mb.showinfo('Error', 'Pyle must be inside GSPM')
        return
    destination1 = filedialog.askdirectory(initialdir=str(GSPM_PATH))
    if source1 and destination1:
        dest = Path(destination1)
        if not _in_gspm(dest):
            mb.showinfo('Error', 'Destination must be inside GSPM')
            return
        dest_file = dest / Path(source1).name
        # if the destination file exists, ask before overwriting
        if dest_file.exists():
            if config.get('confirmations', True):
                if not mb.askyesno('Overwrite', f'Pyle "{dest_file.name}" already exists. Overwrite?'):
                    return
        shutil.copy(source1, destination1)
        mb.showinfo('confirmation', "Pyle Copied!")

def delete_pyle():
    p = open_window()
    if p and os.path.exists(p) and _in_gspm(p):
        if config.get('confirmations', True):
            if not mb.askyesno('Delete', f'Delete Pyle "{os.path.basename(p)}"?'):
                return
        os.remove(p)
    else:
        mb.showinfo('confirmation', "Pyle not found!")

def rename_pyle():
    chosen = open_window()
    if not chosen:
        return
    if not _in_gspm(chosen):
        mb.showinfo('Error', 'Pyle must be inside GSPM')
        return
    path1 = os.path.dirname(chosen)
    extension = os.path.splitext(chosen)[1]
    print("Enter new name for the chosen Pyle")
    newName = input()
    path = os.path.join(path1, newName + extension)
    if os.path.exists(path):
        if config.get('confirmations', True):
            if not mb.askyesno('Overwrite', f'"{os.path.basename(path)}" already exists. Overwrite?'):
                return
    if config.get('confirmations', True):
        if not mb.askyesno('Rename', f'Rename "{os.path.basename(chosen)}" to "{os.path.basename(path)}"?'):
            return
    os.rename(chosen, path)
    mb.showinfo('confirmation', "Pyle Renamed!")

def move_pyle():
    source = open_window()
    if not source:
        return
    if not _in_gspm(source):
        mb.showinfo('Error', 'Pyle must be inside GSPM')
        return
    destination = filedialog.askdirectory(initialdir=str(GSPM_PATH))
    if not destination:
        return
    if not _in_gspm(destination):
        mb.showinfo('Error', 'Destination must be inside GSPM')
        return
    dest_file = Path(destination) / Path(source).name
    if source == destination:
        mb.showinfo('confirmation', "Source and destination are the same")
    else:
        if dest_file.exists():
            if config.get('confirmations', True):
                if not mb.askyesno('Overwrite', f'"{dest_file.name}" already exists in destination. Overwrite?'):
                    return
        if config.get('confirmations', True):
            if not mb.askyesno('Move', f'Move "{os.path.basename(source)}" to "{destination}"?'):
                return
        shutil.move(source, destination)
        mb.showinfo('confirmation', "Pyle Moved")

 
#---------------------------[Make the Window]------------------------------------------------------------#

root = Tk()
root.title('GseppoSoft PyleManager')

# --- Modern JellyFish-like theme (colors and ttk styles) ---
style = ttk.Style(root)
try:
    style.theme_use('clam')
except Exception:
    pass

root.update_idletasks()
dpi = root.winfo_fpixels('1i')
# Start with a reasonable default size but allow the user to resize to any screen size

# JellyFish palette: deep navy background, cyan/teal accents, soft lavenders
BG_DARK = '#071025'
BG_CANVAS = '#0b1a2a'
FG_TEXT = '#E6EEF6'
ACCENT = '#7DD3FC'
ACCENT2 = '#7C3AED'
COMMENT = '#94A3B8'
NUMBER = '#F97316'

style.configure('Jelly.TFrame', background=BG_DARK)
style.configure('Jelly.TLabel', background=BG_DARK, foreground=ACCENT, font=('Helvetica', max(8, int(dpi/16))))
style.configure('Jelly.TButton', background='#0f3b47', foreground=FG_TEXT, relief='flat', padding=6)
style.map('Jelly.TButton', background=[('active', ACCENT)])
style.configure('Jelly.TCombobox', fieldbackground=BG_CANVAS, background=BG_CANVAS, foreground=FG_TEXT)
default_w = int(round(4 * dpi))
default_h = int(round(3 * dpi))
root.geometry(f'{default_w}x{default_h}')
root.resizable(True, True)

# Prevent window from becoming so small that controls get cut off
min_w = max(320, int(dpi * 3.5))
min_h = max(200, int(dpi * 2.0))
root.minsize(min_w, min_h)

# initial editor frame (will be updated on resize)
canv_w = int(default_w * 0.65)
canv_h = default_h - 8
editor_frame = ttk.Frame(root, style='Jelly.TFrame')
editor_frame.grid(row=0, column=0, rowspan=10, sticky='nsew', padx=0, pady=0)

base_font_size = 8
editor_font = ('Consolas', base_font_size)
# Text widget with scrollbars
v_scroll = ttk.Scrollbar(editor_frame, orient='vertical')
# Use word wrapping and remove horizontal scrollbar
editor = Text(editor_frame, bg=BG_CANVAS, fg=FG_TEXT, wrap='word', font=editor_font, bd=0, highlightthickness=0)
v_scroll.config(command=editor.yview)
editor.config(yscrollcommand=v_scroll.set)
v_scroll.pack(side='right', fill='y')
editor.pack(side='left', fill='both', expand=True)

ctrl_frame = ttk.Frame(root, style='Jelly.TFrame')
ctrl_frame.grid(row=0, column=1, sticky='n', padx=6, pady=6)
ttk.Label(ctrl_frame, text="GseppoSoft PyleManager", style='Jelly.TLabel').pack(pady=(4,8))
ttk.Button(ctrl_frame, text = "Open a Pyle", command = open_pyle, style='Jelly.TButton').pack(fill='x', pady=3)
ttk.Button(ctrl_frame, text = "Save Pyle", command = lambda: save_pyle(), style='Jelly.TButton').pack(fill='x', pady=3)
ttk.Button(ctrl_frame, text = "Rename a Pyle", command = rename_pyle, style='Jelly.TButton').pack(fill='x', pady=3)

lang_var = StringVar(value='Auto')
combobox = ttk.Combobox(ctrl_frame, textvariable=lang_var, values=('Auto','Python','C/C++','Java','C#'), style='Jelly.TCombobox', state='readonly')
combobox.pack(pady=8, fill='x')

# Keybind selection: VSCode or VIM
keymap_var = StringVar(value=config.get('keymap', 'VSCode'))
ttk.Label(ctrl_frame, text='Keybinds', style='Jelly.TLabel').pack(pady=(6,0))
keymap_box = ttk.Combobox(ctrl_frame, textvariable=keymap_var, values=('VSCode','VIM'), style='Jelly.TCombobox', state='readonly')
keymap_box.pack(pady=4, fill='x')

# Status label for Vim mode
mode_label = ttk.Label(ctrl_frame, text='Mode: VSCode', style='Jelly.TLabel')
mode_label.pack(pady=(6,0))

# Vim state
vim_normal = False
vim_bindings_active = False
# VIM internal state
pending_count = 0
pending_op = None
yank_buffer = ''

def enter_insert_mode(event=None):
    global vim_normal, pending_count, pending_op
    vim_normal = False
    pending_count = 0
    pending_op = None
    mode_label.config(text='Mode: Insert')
    # allow normal text insertion
    return None

def enter_normal_mode(event=None):
    global vim_normal, pending_count, pending_op
    vim_normal = True
    pending_count = 0
    pending_op = None
    mode_label.config(text='Mode: Normal')
    # swallow the Escape key
    return 'break'

def vim_on_key(event):
    # handle keys only in normal mode
    global pending_count, pending_op, yank_buffer
    if not vim_normal:
        return None
    ch = event.char
    # ex command trigger ':'
    if ch == ':':
        prompt_ex_command()
        return 'break'
    # digits: build a count unless it's a single '0' command
    if ch.isdigit():
        if ch == '0' and pending_count == 0:
            # go to line start
            line = int(editor.index('insert').split('.')[0])
            editor.mark_set('insert', f'{line}.0')
            return 'break'
        pending_count = pending_count * 10 + int(ch)
        return 'break'

    count = pending_count or 1

    # operators: d (delete), y (yank)
    if ch in ('d', 'y'):
        if pending_op is None:
            pending_op = ch
            return 'break'
        else:
            # dd or yy
            if ch == pending_op:
                try:
                    line = int(editor.index('insert').split('.')[0])
                    start = f'{line}.0'
                    end = f'{line+count}.0'
                    if pending_op == 'd':
                        editor.delete(start, end)
                    else:
                        # yank
                        txt = editor.get(start, end)
                        yank_buffer = txt
                        root.clipboard_clear()
                        root.clipboard_append(txt)
                    pending_op = None
                    pending_count = 0
                except Exception:
                    pass
            return 'break'

    # simple motions
    try:
        if ch == 'h':
            for _ in range(count):
                editor.mark_set('insert', 'insert -1c')
        elif ch == 'l':
            for _ in range(count):
                editor.mark_set('insert', 'insert +1c')
        elif ch == 'j':
            for _ in range(count):
                editor.mark_set('insert', 'insert +1line')
        elif ch == 'k':
            for _ in range(count):
                editor.mark_set('insert', 'insert -1line')
        elif ch == 'x':
            for _ in range(count):
                editor.delete('insert', 'insert +1c')
        elif ch == 'i':
            enter_insert_mode()
            editor.focus_set()
        elif ch == 'a':
            editor.mark_set('insert', 'insert +1c')
            enter_insert_mode()
            editor.focus_set()
        elif ch == 'o':
            editor.insert('insert lineend', '\n')
            enter_insert_mode()
            editor.focus_set()
        elif ch == '0':
            line = int(editor.index('insert').split('.')[0])
            editor.mark_set('insert', f'{line}.0')
        elif ch == '$':
            line = int(editor.index('insert').split('.')[0])
            editor.mark_set('insert', f'{line}.end')
        elif ch == 'p':
            if yank_buffer:
                editor.insert('insert', yank_buffer)
        elif ch == 'w':
            for _ in range(count):
                idx = editor.search(r'\s', 'insert', regexp=True, stopindex='end')
                if idx:
                    nxt = editor.search(r'\S', idx, regexp=True, stopindex='end')
                    if nxt:
                        editor.mark_set('insert', nxt)
                    else:
                        editor.mark_set('insert', 'end-1c')
        elif ch == 'b':
            for _ in range(count):
                idx = editor.search(r'\S', 'insert', regexp=True, backwards=True, stopindex='1.0')
                if idx:
                    editor.mark_set('insert', idx)
    except Exception:
        pass

    pending_count = 0
    pending_op = None
    return 'break'

def apply_keymap(mode=None):
    global vim_bindings_active, vim_normal
    if mode is None:
        mode = keymap_var.get()
    if mode == 'VIM':
        # bind Escape to enter normal mode, and add key handler
        if not vim_bindings_active:
            editor.bind('<Escape>', lambda e: enter_normal_mode())
            editor.bind('<Key>', lambda e: vim_on_key(e))
            vim_bindings_active = True
        vim_normal = False
        mode_label.config(text='Mode: Insert')
    else:
        # remove vim-specific bindings
        if vim_bindings_active:
            try:
                editor.unbind('<Escape>')
                editor.unbind('<Key>')
            except Exception:
                pass
            vim_bindings_active = False
        vim_normal = False
        mode_label.config(text='Mode: VSCode')

def on_keymap_change(event=None):
    # persist the keymap choice and apply it
    km = keymap_var.get()
    config['keymap'] = km
    save_config(config)
    apply_keymap(km)

# apply initial keymap and persist changes
keymap_box.bind('<<ComboboxSelected>>', on_keymap_change)
apply_keymap()
 
# Settings persistence controls
confirm_var = BooleanVar(value=config.get('confirmations', True))
    # No Settings button (we persist keymap via combobox change)
    # VIM ex-command support (minimal): ':' prompt from normal mode
def handle_ex_command(cmd):
    """Handle minimal ex commands: :w, :q, :wq, :e <file>"""
    global current_pyle_path
    cmd = cmd.strip()
    if cmd == 'w':
        # save current file
        if current_pyle_path:
            save_pyle()
        else:
            # ask for save location
            dest = filedialog.asksaveasfilename(initialdir=str(GSPM_PATH), defaultextension='.txt')
            if dest:
                with open(dest, 'w', encoding='utf-8') as f:
                    f.write(editor.get('1.0', END))
    elif cmd == 'q':
        root.quit()
    elif cmd == 'wq':
        if current_pyle_path:
            save_pyle()
        root.quit()
    elif cmd.startswith('e '):
        # open file
        path = cmd[2:].strip()
        if path:
            full = Path(path)
            if not full.exists():
                # try relative to GSPM
                full = GSPM_PATH / path
            if full.exists() and _in_gspm(full):
                try:
                    with open(full, 'r', encoding='utf-8') as f:
                        editor.delete('1.0', END)
                        editor.insert('1.0', f.read())
                        current_pyle_path = str(full)
                except Exception:
                    mb.showinfo('Error', f'Could not open {path}')
            else:
                mb.showinfo('Error', 'File not found in GSPM')

def prompt_ex_command(event=None):
    # show a simple prompt dialog and handle the command
    cmd = simpledialog.askstring('Ex command', ':')
    if cmd is not None:
        handle_ex_command(cmd)
    return 'break'


editor.tag_configure('kw', foreground=ACCENT)
editor.tag_configure('str', foreground=ACCENT2)
editor.tag_configure('com', foreground=COMMENT)
editor.tag_configure('num', foreground=NUMBER)

py_keywords = set('''False None True and as assert break class continue def del elif else except finally for from global if import in is lambda nonlocal not or pass raise return try while with yield'''.split())
cpp_keywords = set('''auto break case char const continue default do double else enum extern float for goto if inline int long register return short signed sizeof static struct switch typedef union unsigned void volatile while class public private protected namespace using new delete try catch throw'''.split())
csharp_keywords = set('''abstract as base bool break byte case catch char checked class const continue decimal default delegate do double else enum event explicit extern false finally fixed float for foreach goto if implicit in int interface internal is lock long namespace new null object operator out override params private protected public readonly ref return sbyte sealed short sizeof stackalloc static string struct switch this throw true try typeof uint ulong unchecked unsafe ushort using virtual void volatile while'''.split())
java_keywords = set('''abstract assert boolean break byte case catch char class const continue default do double else enum extends final finally float for goto if implements import instanceof int interface long native new package private protected public return short static strictfp super switch synchronized this throw throws transient try void volatile while'''.split())

def detect_lang(path):
    if not path:
        return 'Auto'
    lower = path.lower()
    if lower.endswith(('.py',)):
        return 'Python'
    if lower.endswith(('.c', '.cpp', '.h', '.hpp', '.cc', '.cxx')):
        return 'C/C++'
    if lower.endswith(('.java',)):
        return 'Java'
    if lower.endswith(('.cs',)):
        return 'C#'
    return 'Auto'

def highlight_all(event=None):
    editor.tag_remove('kw', '1.0', END)
    editor.tag_remove('str', '1.0', END)
    editor.tag_remove('com', '1.0', END)
    editor.tag_remove('num', '1.0', END)
    text = editor.get('1.0', END)
    lang = lang_var.get()
    if lang == 'Auto':
        lang = detect_lang(current_pyle_path)
    if lang == 'Python':
        i = '1.0'
        import re
        for m in re.finditer(r"\b[0-9]+\b", text):
            start = f'1.0+{m.start()}c'
            end = f'1.0+{m.end()}c'
            editor.tag_add('num', start, end)
        for m in re.finditer(r"\b[A-Za-z_][A-Za-z0-9_]*\b", text):
            if m.group(0) in py_keywords:
                start = f'1.0+{m.start()}c'
                end = f'1.0+{m.end()}c'
                editor.tag_add('kw', start, end)
        for m in re.finditer(r"(\".*?\"|\'.*?\')", text, re.S):
            start = f'1.0+{m.start()}c'
            end = f'1.0+{m.end()}c'
            editor.tag_add('str', start, end)
        for m in re.finditer(r"#.*", text):
            start = f'1.0+{m.start()}c'
            end = f'1.0+{m.end()}c'
            editor.tag_add('com', start, end)
    elif lang == 'C/C++' or lang == 'Java' or lang == 'C#':
        import re
        for m in re.finditer(r"\b[0-9]+\b", text):
            start = f'1.0+{m.start()}c'
            end = f'1.0+{m.end()}c'
            editor.tag_add('num', start, end)
        for m in re.finditer(r"\b[A-Za-z_][A-Za-z0-9_]*\b", text):
            if (lang == 'Java' and m.group(0) in java_keywords) or (lang == 'C/C++' and m.group(0) in cpp_keywords) or (lang == 'C#' and m.group(0) in csharp_keywords):
                start = f'1.0+{m.start()}c'
                end = f'1.0+{m.end()}c'
                editor.tag_add('kw', start, end)
        # Strings: normal quoted strings, verbatim strings @"...", and interpolated ($"..." or $@"...")
        for m in re.finditer(r"@\"[\s\S]*?\"|\$@\"[\s\S]*?\"|\$\"[\s\S]*?\"|\"(?:\\.|[^\\\"])*\"|'(?:\\.|[^\\'])*'", text, re.S):
            start = f'1.0+{m.start()}c'
            end = f'1.0+{m.end()}c'
            editor.tag_add('str', start, end)
        # Comments: single-line // and multi-line /* */ and XML doc comments ///
        for m in re.finditer(r"///.*|//.*|/\*[\s\S]*?\*/", text):
            start = f'1.0+{m.start()}c'
            end = f'1.0+{m.end()}c'
            editor.tag_add('com', start, end)

editor.bind('<KeyRelease>', highlight_all)

def save_pyle():
    global current_pyle_path
    if not current_pyle_path:
        mb.showinfo('Info', 'No Pyle currently open')
        return
    try:
        data = editor.get('1.0', END)
        with open(current_pyle_path, 'w', encoding='utf-8') as f:
            f.write(data)
        mb.showinfo('Saved', 'Pyle saved')
    except Exception as e:
        mb.showinfo('Error', f'Could not save Pyle: {e}')

def _save_shortcut(event=None):
    save_pyle()

root.bind('<Control-s>', _save_shortcut)

def _on_resize(event=None):
    try:
        # Get current window inner size
        w = root.winfo_width()
        h = root.winfo_height()
        # Compute editor frame size as 65% of width and full height
        new_canv_w = int(w * 0.65)
        new_canv_h = max(32, h)
        editor_frame.configure(width=new_canv_w, height=new_canv_h)
        # Font is fixed at 8pt by design
        editor.config(font=('Consolas', base_font_size))
    except Exception:
        pass

# Make grid expandable so the editor_frame grows when window is resized
root.grid_rowconfigure(0, weight=1)
root.grid_columnconfigure(0, weight=1)
# Ensure control column keeps a usable minimum width so buttons are not hidden
ctrl_min = max(180, int(default_w * 0.28))
root.grid_columnconfigure(1, minsize=ctrl_min)

# Bind resize events to update layout and font sizes
root.bind('<Configure>', _on_resize)

_on_resize()

root.mainloop()
