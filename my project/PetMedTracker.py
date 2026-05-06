import tkinter as tk
from tkinter import messagebox, ttk
from datetime import datetime
import json

# ===== COLOR PALETTE =====
BG         = "#fdf2f8"
NAVIGATION_COLOR = "#ffffff"
COLOR1     = "#e879a0"
COLOR2     = "#c084fc"
TEXT       = "#000000"
TEXT2      = "#646970"
TEXT3      = "#b83764"
MUTED_PINK = "#ebbbd6"
WHITE      = "#ffffff"
BORDER     = "#f3e8ff"
DANGER     = "#f43f5e"
SUCCESS    = "#34d399"
CARD       = "#ffffff"
NAV_FONT   = ("Montserrat SemiBold", 11)

DATA_FILE = "pets_data.json"

FREQUENCIES  = ["Once a day", "Twice a day", "Every other day"]
DAYS_OF_WEEK = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

# DATA HELPER

def load_data():
    try:
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {"pets": [], "schedules": [], "intakes": []}

def save_data(d): # used to save the data back to the json file after any changes are made to it in the app
    with open(DATA_FILE, "w") as f:
        json.dump(d, f, indent=4)

def today_str():
    return datetime.now().strftime("%Y-%m-%d")

def today_weekday() -> str:
    """Return full weekday name for today, e.g. 'Monday'."""
    return datetime.now().strftime("%A")

def doses_required_today(frequency: str) -> int:
    return {"Once a day": 1, "Twice a day": 2,
            "Every other day": 1}.get(frequency, 1)

def doses_given_today(pet: str, med: str, intakes: list) -> int:
    return sum(
        1 for i in intakes
        if i.get("pet") == pet and i.get("med") == med
        and i.get("date", "").startswith(datetime.now().strftime("%B %#d, %Y %I:%M %p"))
    )

def is_due_today(schedule: dict) -> bool:
    """
    For Once/Twice a day: check if today is in saved days (if days list is present).
    For Every other day: check if today is in the saved days list.
    """
    freq = schedule.get("frequency", "Once a day")
    days = schedule.get("days", [])
    # If days are specified, always check against them regardless of frequency
    if days:
        return today_weekday() in days
    # No days specified = every day
    return True

def schedule_status(schedule: dict, intakes: list) -> tuple:
    if not is_due_today(schedule):
        return "Not due today", TEXT2
    freq     = schedule.get("frequency", "Once a day")
    required = doses_required_today(freq)
    given    = doses_given_today(schedule["pet"], schedule["med"], intakes)
    if given >= required:
        return f"Done ({given}/{required})", SUCCESS
    return f"Pending ⏳ ({given}/{required})", "#f59e0b"

# ── App ───────────────────────────────────────────────────────────────────────

class PetMedApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Paws and Pills")
        self.root.geometry("1100x900")
        self.root.configure(bg=BG)
        self.root.resizable(True, True)
        self._setup_styles()
        self._build_layout()
        self.show_dashboard()

    # ── Styles ────────────────────────────────────────────────────────────────

    def _setup_styles(self):
        s = ttk.Style()
        s.theme_use("clam")
        s.configure("Pink.Treeview",
                    background=WHITE, foreground=TEXT, fieldbackground=WHITE, rowheight=38,
                    font=("Montserrat Regular", 10), borderwidth=0)
        s.configure("Pink.Treeview.Heading",
                    background=BG, foreground=TEXT2, font=("Montserrat Bold", 9), borderwidth=0, relief="flat")
        s.map("Pink.Treeview", background=[("selected", "#fce7f3")], foreground=[("selected", COLOR1)])

    # ── Layout skeleton ───────────────────────────────────────────────────────

    def _build_layout(self):
        navbar = tk.Frame(self.root, bg=NAVIGATION_COLOR, height=64)
        navbar.pack(side="top", fill="x")
        navbar.pack_propagate(False)

        tk.Label(navbar, text="Paws and Pills", font=("Rubik Spray Paint Regular", 16), bg=NAVIGATION_COLOR, fg=COLOR1).pack(side="left", padx=24)

        self._nav_btns = [] # to keep references for updating styles on click
        nav_items = [ 
            ("Dashboard",     self.show_dashboard),
            ("Add Pet",       self.show_add_pet),
            ("Schedules",     self.show_schedules),
            ("Record Intake", self.show_record_intake),
            ("View Records",  self.show_view_records),
        ]
        links = tk.Frame(navbar, bg=NAVIGATION_COLOR)
        links.pack(side="left", padx=16)
        for text, cmd in nav_items:
            btn = tk.Button(links, text=text, font=NAV_FONT, bg=NAVIGATION_COLOR, fg=TEXT2, bd=0, padx=14, pady=8, cursor="hand2", activebackground="#fff0f7",
                            activeforeground=COLOR1, relief="flat", command=lambda c=cmd, t=text: self._nav(c, t))
            btn.pack(side="left", padx=2)
            self._nav_btns.append((btn, text))

        tk.Frame(self.root, bg=BORDER, height=2).pack(fill="x")
        self.main = tk.Frame(self.root, bg=BG)
        self.main.pack(fill="both", expand=True)

    def _nav(self, command, text):
        for btn, t in self._nav_btns:
            active = t == text
            btn.configure(fg=COLOR1 if active else TEXT2,
                          bg="#fff0f7" if active else NAVIGATION_COLOR,
                          font=NAV_FONT)
        command()

    def _clear(self):
        for w in self.main.winfo_children():
            w.destroy()

    # ── Reusable widgets ──────────────────────────────────────────────────────

    def _card(self, parent, padx=20, pady=20):
        return tk.Frame(parent, bg=CARD, highlightthickness=1,
                        highlightbackground=BORDER, padx=padx, pady=pady)

    def _section(self, parent, text):
        tk.Label(parent, text=text, font=("Montserrat Bold", 12),
                 bg=BG, fg=TEXT).pack(anchor="w", pady=(14, 4))

    def _field_label(self, parent, text):
        tk.Label(parent, text=text, bg=CARD, fg=TEXT2,
                 font=("Montserrat Bold", 9)).pack(anchor="w", pady=(10, 2))

    def _entry(self, parent):
        e = tk.Entry(parent, font=("Montserrat Regular", 11), bd=0,
                     highlightthickness=1, highlightbackground="#f3e8ff",
                     bg="#fdf4ff", fg=TEXT)
        e.pack(fill="x", ipady=9)
        return e

    def _scrollable(self):
        canvas = tk.Canvas(self.main, bg=BG, highlightthickness=0)
        sb = ttk.Scrollbar(self.main, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=sb.set)
        sb.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)
        cont = tk.Frame(canvas, bg=BG, padx=40, pady=28)
        win = canvas.create_window((0, 0), window=cont, anchor="nw")
        cont.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.bind("<Configure>", lambda e: canvas.itemconfig(win, width=e.width))
        return canvas, cont

    def _primary_btn(self, parent, text, command):
        tk.Frame(parent, bg=CARD, height=14).pack()
        tk.Button(parent, text=text, bg=COLOR1, fg=WHITE,
                  font=("Montserrat Bold", 11), bd=0, pady=12,
                  cursor="hand2", activebackground="#be185d",
                  command=command).pack(fill="x")

    def _day_picker(self, parent, preselect=None):
        frame = tk.Frame(parent, bg=CARD)
        frame.pack(fill="x", pady=(6, 2))
        vars_ = {}
        for day in DAYS_OF_WEEK:
            var = tk.BooleanVar(value=(day in (preselect or [])))
            cb = tk.Checkbutton(frame, text=day[:3], variable=var,
                                bg=CARD, fg=TEXT, selectcolor="#fce7f3",
                                activebackground=CARD,
                                font=("Montserrat Regular", 9),
                                cursor="hand2")
            cb.pack(side="left", padx=4)
            vars_[day] = var
        return vars_

# DASHBOARD 

    def show_dashboard(self):
        self._clear()
        data = load_data()
        cont = tk.Frame(self.main, bg=BG, padx=40, pady=28)
        cont.pack(fill="both", expand=True)

        # Greeting
        greeting = tk.Frame(cont, bg="#fce7f3", padx=15, pady=5,
                            highlightthickness=0.5, highlightbackground="#f9a8d4")
        greeting.pack(fill="x", pady=(0, 10))
        inner = tk.Frame(greeting, bg="#fce7f3")
        inner.pack(anchor="center")
        tk.Label(inner, text="    /)/)\n( ˶•༝•)\n୭( づ✿", font=("Montserrat Regular", 18),
                 fg=TEXT3, bg="#fce7f3").pack(side="left", padx=(0, 12))
        text_frame = tk.Frame(inner, bg="#fce7f3")
        text_frame.pack(side="left")
        tk.Label(text_frame, text="H e l l o ! \n Welcome to Paws & Pills",
                 font=("Rubik Spray Paint Regular", 15), bg="#fce7f3", fg=TEXT3).pack(anchor="center", pady=0)
        tk.Label(text_frame, text="Here's a quick overview of your pets' medication schedules and status.",
                 font=("Montserrat Regular", 10), bg="#fce7f3", fg=TEXT2).pack(anchor="center", pady=(4, 0))

        # Stat cards for pets, schedules, and today's intakes (overview sha)
        row = tk.Frame(cont, bg=BG, padx=10, pady=0)
        row.pack(fill="x", padx=10, pady=(0, 20))
        for kyotie, label, val, clr in [
            ("૮꒰ ˶• ༝ •˶꒱ა", "Pets",       f"{len(data['pets'])}",      COLOR1),
            ("────୨ৎ────", "Schedules",  f"{len(data['schedules'])}", COLOR2),
            (" 𓆉 𓆝 ⋆.˚ ", "Total Logs", f"{len(data['intakes'])}",   "#f59e0b"),]:
            # Create a stat card for each overview
            card = self._card(row, padx=18, pady=16)
            card.pack(side="left", fill="both", expand=True, padx=(0, 12))
            top = tk.Frame(card, bg=CARD)
            top.pack(fill="both", expand=True)
            tk.Label(top, text=kyotie,  font=("Montserrat Bold", 15), bg=CARD, fg=MUTED_PINK).pack(side="top")
            tk.Label(top, text=label, font=("Montserrat Bold", 20), bg=CARD).pack(side="left")
            tk.Label(top, text=val,   font=("Montserrat Bold", 22), bg=CARD, fg=clr).pack(side="right")

        # Medication status
        self._section(cont, "Medication Status")
        sched_card = self._card(cont, padx=16, pady=16)
        sched_card.pack(fill="x", pady=(0, 12))

        if not data["schedules"]:
            tk.Label(sched_card, text="No schedules yet.",
                     font=("Montserrat Regular", 10), bg=CARD, fg=TEXT2).pack(anchor="w")
        else:
            cols = ("pet", "med", "frequency", "days", "today", "datetime")
            tree = ttk.Treeview(sched_card, columns=cols, show="headings",
                                style="Pink.Treeview", height=min(len(data["schedules"]), 6))
            for col, head, w in zip(cols,
                                    ("Pet", "Medication", "Frequency", "Days", "Status", "Date & Time"),
                                    [110, 130, 110, 180, 160, 160]):
                tree.heading(col, text=head)
                tree.column(col, width=w, anchor="center")
            tree.pack(fill="x")
            for sc in data["schedules"]:
                lbl, _ = schedule_status(sc, data["intakes"])
                days_val = ", ".join(sc["days"]) if sc.get("days") else "Every day"
                tree.insert("", "end", values=(sc["pet"], sc["med"], sc["frequency"], days_val, lbl, datetime.now().strftime("%B %#d, %Y %I:%M %p")
                ))

    # ── ADD PET ───────────────────────────────────────────────────────────────

    def show_add_pet(self):
        self._clear()
        data = load_data()
        cont = tk.Frame(self.main, bg=BG, padx=40, pady=28)
        cont.pack(fill="both", expand=True)

        tk.Label(cont, text="Add New Pet", font=("Montserrat Bold", 20),
                 bg=BG, fg=TEXT).pack(anchor="w", pady=(0, 16))

        card = self._card(cont, padx=28, pady=28)
        card.pack(fill="x")

        self._field_label(card, "Pet Name")
        name_ent = self._entry(card)
        self._field_label(card, "Species")
        species_ent = self._entry(card)
        self._field_label(card, "Age (years/months)")
        age_ent = self._entry(card)

        def save():
            name    = name_ent.get().strip()
            species = species_ent.get().strip()
            age     = age_ent.get().strip()
            if not name or not age:
                messagebox.showwarning("Missing Fields", "Pet Name and Age are required.")
                return
            data["pets"].append({"name": name, "species": species, "age": age})
            save_data(data)
            messagebox.showinfo("Success", f"✅ {name} has been added!")
            self.show_dashboard()

        self._primary_btn(card, "Save Pet Profile", save)

    # ── SCHEDULES ─────────────────────────────────────────────────────────────

    def show_schedules(self):
        self._clear()
        data = load_data()
        _, cont = self._scrollable()

        tk.Label(cont, text="Medication Schedules", font=("Montserrat Bold", 20),
                 bg=BG, fg=TEXT).pack(anchor="w", pady=(0, 4))
        tk.Label(cont,
                 text="Set a frequency per pet+medication pair. The dashboard will track daily progress.",
                 font=("Montserrat Regular", 10), bg=BG, fg=TEXT2).pack(anchor="w", pady=(0, 16))

        # ── Add schedule form ──
        form_card = self._card(cont, padx=28, pady=24)
        form_card.pack(fill="x", pady=(0, 20))
        tk.Label(form_card, text="Add New Schedule", font=("Montserrat Bold", 12),
                 bg=CARD, fg=TEXT).pack(anchor="w", pady=(0, 8))

        self._field_label(form_card, "Pet")
        pet_names = [p["name"] for p in data["pets"]] or ["No pets added"]
        pet_cb = ttk.Combobox(form_card, values=pet_names, state="readonly",
                              font=("Montserrat Regular", 11))
        pet_cb.pack(fill="x", ipady=6)
        if pet_names:
            pet_cb.current(0)

        self._field_label(form_card, "Medication Name")
        med_ent = self._entry(form_card)

        self._field_label(form_card, "Frequency")
        freq_cb = ttk.Combobox(form_card, values=FREQUENCIES, state="readonly",
                               font=("Montserrat Regular", 11))
        freq_cb.pack(fill="x", ipady=6)
        freq_cb.current(0)

        # ── Day picker (shown for ALL frequencies) ──
        day_picker_label = tk.Label(form_card, text="Days to give medication",
                                    bg=CARD, fg=TEXT2, font=("Montserrat Bold", 9))
        day_picker_hint  = tk.Label(form_card, bg=CARD, fg=TEXT2,
                                    font=("Montserrat Regular", 8),
                                    text="Leave all unchecked to give every day.")
        day_picker_frame = tk.Frame(form_card, bg=CARD)
        day_vars = {}

        def refresh_day_picker(event=None):
            freq = freq_cb.get()
            nonlocal day_vars

            # Clear old checkboxes
            for w in day_picker_frame.winfo_children():
                w.destroy()

            # Always show the day picker
            day_picker_label.pack(anchor="w", pady=(10, 2))
            day_picker_hint.pack(anchor="w", pady=(0, 2))
            day_picker_frame.pack(fill="x", pady=(0, 4))

            # Default selections per frequency
            if freq == "Every other day":
                defaults = ["Monday", "Wednesday", "Friday"]
            else:
                # Once a day / Twice a day: all days checked by default
                defaults = DAYS_OF_WEEK[:]

            day_vars = {}
            for day in DAYS_OF_WEEK:
                var = tk.BooleanVar(value=(day in defaults))
                cb = tk.Checkbutton(day_picker_frame, text=day[:3], variable=var,
                                    bg=CARD, fg=TEXT, selectcolor="#fce7f3",
                                    activebackground=CARD,
                                    font=("Montserrat Regular", 9),
                                    cursor="hand2")
                cb.pack(side="left", padx=4)
                day_vars[day] = var

        freq_cb.bind("<<ComboboxSelected>>", refresh_day_picker)
        refresh_day_picker()  # init state

        def add_schedule():
            pet  = pet_cb.get()
            med  = med_ent.get().strip()
            freq = freq_cb.get()
            if pet == "No pets added" or not med:
                messagebox.showwarning("Missing Fields", "Select a pet and enter a medication name.")
                return
            if any(s["pet"] == pet and s["med"] == med for s in data["schedules"]):
                messagebox.showwarning("Duplicate", f"A schedule for {pet} / {med} already exists.")
                return

            # Collect selected days for all frequencies
            selected_days = [d for d, v in day_vars.items() if v.get()]
            # If user unchecked everything, treat as "every day" (empty list)
            # If "Every other day" and nothing selected, warn
            if freq == "Every other day" and not selected_days:
                messagebox.showwarning("No Days Selected",
                                       "Please select at least one day for this frequency.")
                return

            data["schedules"].append({
                "pet":       pet,
                "med":       med,
                "frequency": freq,
                "days":      selected_days   # empty = every day for Once/Twice a day
            })
            save_data(data)
            self.show_schedules()

        self._primary_btn(form_card, "Add Schedule", add_schedule)

        # ── Current schedules table ──
        self._section(cont, "Current Schedules")
        table_card = self._card(cont, padx=16, pady=16)
        table_card.pack(fill="both", expand=True)

        cols = ("pet", "med", "frequency", "days", "today_status")
        tree = ttk.Treeview(table_card, columns=cols, show="headings",
                            style="Pink.Treeview", height=max(len(data["schedules"]), 1))
        for col, head, w in zip(cols,
                                ("Pet", "Medication", "Frequency", "Days", "Today's Status"),
                                [120, 140, 110, 200, 160]):
            tree.heading(col, text=head)
            tree.column(col, width=w, anchor="center")
        tree.pack(fill="both", expand=True)

        for sc in data["schedules"]:
            lbl, _ = schedule_status(sc, data["intakes"])
            days_val = ", ".join(sc["days"]) if sc.get("days") else "Every day"
            tree.insert("", "end", values=(sc["pet"], sc["med"], sc["frequency"], days_val, lbl))

        btn_row = tk.Frame(table_card, bg=CARD)
        btn_row.pack(anchor="e", pady=(10, 0))

        def delete_schedule():
            sel = tree.selection()
            if not sel:
                return
            vals = tree.item(sel[0])["values"]
            pet_v, med_v = vals[0], vals[1]
            if messagebox.askyesno("Delete Schedule", f"Remove schedule for {pet_v} / {med_v}?"):
                data["schedules"] = [s for s in data["schedules"]
                                     if not (s["pet"] == pet_v and s["med"] == med_v)]
                save_data(data)
                self.show_schedules()

        tk.Button(btn_row, text="🗑  Delete Selected",
                  bg=DANGER, fg=WHITE, font=("Montserrat Bold", 9),
                  bd=0, padx=12, pady=6, cursor="hand2",
                  command=delete_schedule).pack()

    # ── RECORD INTAKE ─────────────────────────────────────────────────────────

    def show_record_intake(self):
        self._clear()
        data = load_data()
        cont = tk.Frame(self.main, bg=BG, padx=40, pady=28)
        cont.pack(fill="both", expand=True)

        tk.Label(cont, text="Record Medication Intake", font=("Montserrat Bold", 20),
                 bg=BG, fg=TEXT).pack(anchor="w", pady=(0, 16))

        card = self._card(cont, padx=28, pady=28)
        card.pack(fill="x")

        self._field_label(card, "Select Pet")
        pet_names = [p["name"] for p in data["pets"]] or ["No pets added"]
        pet_cb = ttk.Combobox(card, values=pet_names, state="readonly",
                              font=("Montserrat Regular", 11))
        pet_cb.pack(fill="x", ipady=6)
        if pet_names:
            pet_cb.current(0)

        self._field_label(card, "Medication")
        med_cb = ttk.Combobox(card, state="readonly", font=("Montserrat Regular", 11))
        med_cb.pack(fill="x", ipady=6)

        def refresh_meds(event=None):
            pet  = pet_cb.get()
            meds = [s["med"] for s in data["schedules"] if s["pet"] == pet]
            if meds:
                med_cb["values"] = meds
                med_cb.current(0)
            else:
                med_cb["values"] = ["No medicine for this pet."]
                med_cb.set("No medicine for this pet.")

        pet_cb.bind("<<ComboboxSelected>>", refresh_meds)
        refresh_meds()

        self._field_label(card, "Given By")
        user_ent = self._entry(card)

        def save_intake():
            pet  = pet_cb.get()
            med  = med_cb.get()
            user = user_ent.get().strip()
            if pet == "No pets added" or not med or med == "No medicine for this pet.":
                messagebox.showwarning("Missing Fields", "Select a valid pet and medication.")
                return
            data["intakes"].append({
                "date":     datetime.now().strftime("%Y-%m-%d %I:%M %p"),
                "pet":      pet,
                "med":      med,
                "given_by": user,
                "status":   "Given ✅"
            })
            save_data(data)
            messagebox.showinfo("Success", "Intake recorded!")
            self.show_dashboard()

        self._primary_btn(card, "Record Intake", save_intake)

    # ── VIEW RECORDS ──────────────────────────────────────────────────────────

    def show_view_records(self):
        self._clear()
        data = load_data()
        _, cont = self._scrollable()

        tk.Label(cont, text="View Records", font=("Montserrat Bold", 20),
                 bg=BG, fg=TEXT).pack(anchor="w")

        tab_frame = tk.Frame(cont, bg=BG)
        tab_frame.pack(fill="x", pady=14)

        table_cont = tk.Frame(cont, bg=BG)
        table_cont.pack(fill="both", expand=True)

        tab_btns = {}

        def display_tab(cat, pet_filter="All"):
            for c, b in tab_btns.items():
                b.configure(
                    bg=COLOR1 if c == cat else WHITE,
                    fg=WHITE   if c == cat else TEXT2,
                    font=("Montserrat Bold", 10) if c == cat else ("Montserrat Regular", 10))

            for w in table_cont.winfo_children():
                w.destroy()

            card = self._card(table_cont, padx=16, pady=16)
            card.pack(fill="both", expand=True)

            # Per-pet filter on history tab
            if cat == "intakes":
                filter_frame = tk.Frame(card, bg=CARD)
                filter_frame.pack(fill="x", pady=(0, 10))
                tk.Label(filter_frame, text="Filter by pet:", bg=CARD,
                         fg=TEXT2, font=("Montserrat Bold", 9)).pack(side="left", padx=(0, 8))
                pet_names = ["All"] + [p["name"] for p in data["pets"]]
                filter_cb = ttk.Combobox(filter_frame, values=pet_names,
                                         state="readonly", font=("Montserrat Regular", 10), width=20)
                filter_cb.pack(side="left")
                filter_cb.set(pet_filter)
                filter_cb.bind("<<ComboboxSelected>>",
                               lambda e: display_tab("intakes", filter_cb.get()))

            # Columns per tab
            if cat == "pets":
                cols  = ("name", "species", "age")
                heads = ("Pet Name", "Species", "Age")
                rows  = data["pets"]
            elif cat == "schedules":
                cols  = ("pet", "med", "frequency", "days", "status")
                heads = ("Pet", "Medication", "Frequency", "Days", "Today's Status")
                rows  = [{"pet": s["pet"], "med": s["med"],
                          "frequency": s["frequency"],
                          "days": ", ".join(s["days"]) if s.get("days") else "Every day",
                          "status": schedule_status(s, data["intakes"])[0]}
                         for s in data["schedules"]]
            else:  # intakes
                cols  = ("date", "pet", "med", "given_by", "status")
                heads = ("Date", "Pet", "Medication", "Given By", "Status")
                rows  = [i for i in data["intakes"]
                         if pet_filter == "All" or i.get("pet") == pet_filter]

            tree = ttk.Treeview(card, columns=cols, show="headings",
                                style="Pink.Treeview", height=max(len(rows), 1))
            for col, head in zip(cols, heads):
                tree.heading(col, text=head)
                tree.column(col, anchor="center")
            tree.pack(fill="x")

            for row in rows:
                tree.insert("", "end", values=tuple(row.get(k, "") for k in cols))

            # Delete button — all tabs
            btn_row = tk.Frame(card, bg=CARD)
            btn_row.pack(anchor="e", pady=(10, 0))

            def delete_item(c=cat, pf=pet_filter):
                sel = tree.selection()
                if not sel:
                    return
                vals = tree.item(sel[0])["values"]

                if c == "pets":
                    key     = "pets"
                    match   = lambda x: x["name"] == vals[0]
                    confirm = f"Delete pet '{vals[0]}'?"
                elif c == "schedules":
                    key     = "schedules"
                    match   = lambda x: x["pet"] == vals[0] and x["med"] == vals[1]
                    confirm = f"Delete schedule for '{vals[0]} / {vals[1]}'?"
                else:
                    key     = "intakes"
                    match   = lambda x: (x.get("date") == vals[0]
                                         and x.get("pet") == vals[1]
                                         and x.get("med") == vals[2])
                    confirm = f"Delete intake record for {vals[1]} — {vals[2]} on {vals[0]}?"

                if messagebox.askyesno("Confirm Delete", confirm):
                    for i, x in enumerate(data[key]):
                        if match(x):
                            data[key].pop(i)
                            break
                    save_data(data)
                    display_tab(c, pf)

            tk.Button(btn_row, text="🗑  Delete Selected",
                      bg=DANGER, fg=WHITE, font=("Montserrat Bold", 9),
                      bd=0, padx=12, pady=6, cursor="hand2",
                      command=delete_item).pack()

        for label, key in [("Pets 🐾", "pets"), ("Schedules 📅", "schedules"), ("History 📋", "intakes")]:
            b = tk.Button(tab_frame, text=label, font=("Montserrat Regular", 10),
                          bg=WHITE, fg=TEXT2, bd=0, padx=16, pady=8,
                          cursor="hand2", highlightthickness=1, highlightbackground=BORDER,
                          command=lambda k=key: display_tab(k))
            b.pack(side="left", padx=(0, 8))
            tab_btns[key] = b

        display_tab("pets")


if __name__ == "__main__":
    root = tk.Tk()
    PetMedApp(root)
    root.mainloop()