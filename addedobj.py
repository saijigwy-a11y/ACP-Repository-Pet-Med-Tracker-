import tkinter as tk
from tkinter import messagebox, ttk
from datetime import datetime
import json

# ===== COLOR PALETTE =====
BG         = "#fdf2f8"
NAVIGATION = "#ffffff"
COLOR1     = "#e879a0"
COLOR2     = "#c084fc"
TEXT       = "#1e1b4b"
TEXT2      = "#9ca3af"
WHITE      = "#ffffff"
BORDER     = "#f3e8ff"
DANGER     = "#f43f5e"
SUCCESS    = "#34d399"
CARD       = "#ffffff"

DATA_FILE = "pets_data.json"

FREQUENCIES = ["Once daily", "Twice daily", "Every other day", "Weekly", "As needed"]

# ── Data helpers ──────────────────────────────────────────────────────────────

def load_data():
    try:
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {"pets": [], "schedules": [], "intakes": []}

def save_data(d):
    with open(DATA_FILE, "w") as f:
        json.dump(d, f, indent=4)

def today_str():
    return datetime.now().strftime("%Y-%m-%d")

def doses_required_today(frequency: str) -> int:
    """Return how many doses are expected today for a given frequency."""
    return {"Once daily": 1, "Twice daily": 2, "Every other day": 1,
            "Weekly": 1, "As needed": 0}.get(frequency, 1)

def doses_given_today(pet: str, med: str, intakes: list) -> int:
    return sum(
        1 for i in intakes
        if i.get("pet") == pet and i.get("med") == med
        and i.get("date", "").startswith(today_str())
    )

def schedule_status(schedule: dict, intakes: list) -> tuple[str, str]:
    """Return (label, color) for a schedule entry."""
    freq = schedule.get("frequency", "Once daily")
    if freq == "As needed":
        return "As needed", TEXT2
    required = doses_required_today(freq)
    given = doses_given_today(schedule["pet"], schedule["med"], intakes)
    if given >= required:
        return f"Done ✅ ({given}/{required})", SUCCESS
    return f"Pending ⏳ ({given}/{required})", "#f59e0b"

# ── App ───────────────────────────────────────────────────────────────────────

class PetMedApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Paws and Pills")
        self.root.geometry("1100x720")
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
                    background=WHITE, foreground=TEXT,
                    fieldbackground=WHITE, rowheight=38,
                    font=("Segoe UI", 10), borderwidth=0)
        s.configure("Pink.Treeview.Heading",
                    background=BG, foreground=TEXT2,
                    font=("Segoe UI Bold", 9), borderwidth=0, relief="flat")
        s.map("Pink.Treeview",
              background=[("selected", "#fce7f3")],
              foreground=[("selected", COLOR1)])

    # ── Layout skeleton ───────────────────────────────────────────────────────

    def _build_layout(self):
        navbar = tk.Frame(self.root, bg=NAVIGATION, height=64)
        navbar.pack(side="top", fill="x")
        navbar.pack_propagate(False)

        tk.Label(navbar, text="Paws and Pills", font=("Segoe UI Bold", 16),
                 bg=NAVIGATION, fg=TEXT).pack(side="left", padx=24)

        self._nav_btns = []
        nav_items = [
            ("Dashboard",      self.show_dashboard),
            ("Add Pet",        self.show_add_pet),
            ("Schedules",      self.show_schedules),
            ("Record Intake",  self.show_record_intake),
            ("View Records",   self.show_view_records),
        ]
        links = tk.Frame(navbar, bg=NAVIGATION)
        links.pack(side="left", padx=16)
        for text, cmd in nav_items:
            btn = tk.Button(links, text=text, font=("Segoe UI Semibold", 10),
                            bg=NAVIGATION, fg=TEXT2, bd=0, padx=14, pady=8,
                            cursor="hand2", activebackground="#fff0f7",
                            activeforeground=COLOR1, relief="flat",
                            command=lambda c=cmd, t=text: self._nav(c, t))
            btn.pack(side="left", padx=2)
            self._nav_btns.append((btn, text))

        tk.Frame(self.root, bg=BORDER, height=2).pack(fill="x")
        self.main = tk.Frame(self.root, bg=BG)
        self.main.pack(fill="both", expand=True)

    def _nav(self, command, text):
        for btn, t in self._nav_btns:
            active = t == text
            btn.configure(fg=COLOR1 if active else TEXT2,
                          bg="#fff0f7" if active else NAVIGATION,
                          font=("Segoe UI Bold", 10) if active else ("Segoe UI Semibold", 10))
        command()

    def _clear(self):
        for w in self.main.winfo_children():
            w.destroy()

    # ── Reusable widgets ──────────────────────────────────────────────────────

    def _card(self, parent, padx=20, pady=20):
        return tk.Frame(parent, bg=CARD, highlightthickness=1,
                        highlightbackground=BORDER, padx=padx, pady=pady)

    def _section(self, parent, text):
        tk.Label(parent, text=text, font=("Segoe UI Bold", 11),
                 bg=BG, fg=TEXT).pack(anchor="w", pady=(14, 4))

    def _field_label(self, parent, text):
        tk.Label(parent, text=text, bg=CARD, fg=TEXT2,
                 font=("Segoe UI Bold", 9)).pack(anchor="w", pady=(10, 2))

    def _entry(self, parent):
        e = tk.Entry(parent, font=("Segoe UI", 11), bd=0,
                     highlightthickness=1, highlightbackground="#f3e8ff",
                     bg="#fdf4ff", fg=TEXT)
        e.pack(fill="x", ipady=9)
        return e

    def _scrollable(self):
        """Return (canvas, container) with vertical scrollbar wired up."""
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
                  font=("Segoe UI Bold", 11), bd=0, pady=12,
                  cursor="hand2", activebackground="#be185d",
                  command=command).pack(fill="x")

    # ── DASHBOARD ─────────────────────────────────────────────────────────────

    def show_dashboard(self):
        self._clear()
        data = load_data()
        _, cont = self._scrollable()

        # Hero
        hero = tk.Frame(cont, bg="#fce7f3", padx=28, pady=22,
                        highlightthickness=1, highlightbackground="#f9a8d4")
        hero.pack(fill="x", pady=(0, 20))
        lf = tk.Frame(hero, bg="#fce7f3")
        lf.pack(side="left", fill="both", expand=True)
        tk.Label(lf, text="Good day! 👋", font=("Segoe UI", 12),
                 bg="#fce7f3", fg=COLOR1).pack(anchor="w")
        tk.Label(lf, text="Check your Pets & Medication Schedule",
                 font=("Segoe UI Bold", 18), bg="#fce7f3", fg=TEXT).pack(anchor="w", pady=(4, 2))
        tk.Label(lf, text="Keep your furry friends healthy 🐶🐱",
                 font=("Segoe UI", 10), bg="#fce7f3", fg="#be185d").pack(anchor="w")
        tk.Label(hero, text="🐾", font=("Segoe UI", 56), bg="#fce7f3").pack(side="right", padx=20)

        # Stat cards
        row = tk.Frame(cont, bg=BG)
        row.pack(fill="x", pady=(0, 6))
        for icon, val, label, clr in [
            ("🐾", f"{len(data['pets'])}",     "Pets",       COLOR1),
            ("📅", f"{len(data['schedules'])}", "Schedules",  COLOR2),
            ("📋", f"{len(data['intakes'])}",   "Total Logs", "#f59e0b"),
        ]:
            card = self._card(row, padx=18, pady=16)
            card.pack(side="left", fill="both", expand=True, padx=(0, 12))
            top = tk.Frame(card, bg=CARD)
            top.pack(fill="x")
            tk.Label(top, text=icon, font=("Segoe UI", 20), bg=CARD).pack(side="left")
            tk.Label(top, text=val,  font=("Segoe UI Bold", 22), bg=CARD, fg=clr).pack(side="right")
            tk.Label(card, text=label, font=("Segoe UI", 10), bg=CARD, fg=TEXT2).pack(anchor="w", pady=(6, 0))

        # Today's schedule status
        self._section(cont, "Today's Medication Status")
        sched_card = self._card(cont, padx=16, pady=16)
        sched_card.pack(fill="x", pady=(0, 12))

        if not data["schedules"]:
            tk.Label(sched_card, text="No schedules yet. Add one via the Schedules tab.",
                     font=("Segoe UI", 10), bg=CARD, fg=TEXT2).pack(anchor="w")
        else:
            cols = ("pet", "med", "frequency", "today")
            tree = ttk.Treeview(sched_card, columns=cols, show="headings",
                                style="Pink.Treeview", height=min(len(data["schedules"]), 6))
            for col, head, w in zip(cols, ("Pet", "Medication", "Frequency", "Today's Status"), [130, 160, 130, 200]):
                tree.heading(col, text=head)
                tree.column(col, width=w, anchor="center")
            tree.pack(fill="x")
            for sc in data["schedules"]:
                label, _ = schedule_status(sc, data["intakes"])
                tree.insert("", "end", values=(sc["pet"], sc["med"], sc["frequency"], label))

        # Recent history
        self._section(cont, "Recent Intake History")
        hist_card = self._card(cont, padx=16, pady=16)
        hist_card.pack(fill="both", expand=True)
        cols = ("date", "pet", "med", "dose", "status")
        tree = ttk.Treeview(hist_card, columns=cols, show="headings",
                            style="Pink.Treeview", height=8)
        for col, w in zip(cols, [170, 110, 130, 100, 110]):
            tree.heading(col, text=col.capitalize())
            tree.column(col, width=w, anchor="center")
        tree.pack(fill="both", expand=True)
        for i in reversed(data["intakes"][-12:]):
            tree.insert("", "end", values=(i.get("date"), i.get("pet"),
                                           i.get("med"), i.get("dose"), i.get("status")))

    # ── ADD PET ───────────────────────────────────────────────────────────────

    def show_add_pet(self):
        self._clear()
        data = load_data()
        cont = tk.Frame(self.main, bg=BG, padx=40, pady=28)
        cont.pack(fill="both", expand=True)

        tk.Label(cont, text="Add New Pet", font=("Segoe UI Bold", 20),
                 bg=BG, fg=TEXT).pack(anchor="w", pady=(0, 16))

        card = self._card(cont, padx=28, pady=28)
        card.pack(fill="x")

        self._field_label(card, "Pet Name")
        name_ent = self._entry(card)
        self._field_label(card, "Species")
        species_ent = self._entry(card)
        self._field_label(card, "Age (years)")
        age_ent = self._entry(card)

        def save():
            name = name_ent.get().strip()
            species = species_ent.get().strip()
            age = age_ent.get().strip()
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

        tk.Label(cont, text="Medication Schedules", font=("Segoe UI Bold", 20),
                 bg=BG, fg=TEXT).pack(anchor="w", pady=(0, 4))
        tk.Label(cont, text="Set a frequency per pet+medication pair. The dashboard will track daily progress.",
                 font=("Segoe UI", 10), bg=BG, fg=TEXT2).pack(anchor="w", pady=(0, 16))

        # ── Add schedule form ──
        form_card = self._card(cont, padx=28, pady=24)
        form_card.pack(fill="x", pady=(0, 20))
        tk.Label(form_card, text="Add New Schedule", font=("Segoe UI Bold", 12),
                 bg=CARD, fg=TEXT).pack(anchor="w", pady=(0, 8))

        self._field_label(form_card, "Pet")
        pet_names = [p["name"] for p in data["pets"]] or ["No pets added"]
        pet_cb = ttk.Combobox(form_card, values=pet_names, state="readonly", font=("Segoe UI", 11))
        pet_cb.pack(fill="x", ipady=6)
        if pet_names:
            pet_cb.current(0)

        self._field_label(form_card, "Medication Name")
        med_ent = self._entry(form_card)

        self._field_label(form_card, "Frequency")
        freq_cb = ttk.Combobox(form_card, values=FREQUENCIES, state="readonly", font=("Segoe UI", 11))
        freq_cb.pack(fill="x", ipady=6)
        freq_cb.current(0)

        def add_schedule():
            pet = pet_cb.get()
            med = med_ent.get().strip()
            freq = freq_cb.get()
            if pet == "No pets added" or not med:
                messagebox.showwarning("Missing Fields", "Select a pet and enter a medication name.")
                return
            # Prevent duplicates
            if any(s["pet"] == pet and s["med"] == med for s in data["schedules"]):
                messagebox.showwarning("Duplicate", f"A schedule for {pet} / {med} already exists.")
                return
            data["schedules"].append({"pet": pet, "med": med, "frequency": freq})
            save_data(data)
            self.show_schedules()

        self._primary_btn(form_card, "Add Schedule", add_schedule)

        # ── Current schedules table ──
        self._section(cont, "Current Schedules")
        table_card = self._card(cont, padx=16, pady=16)
        table_card.pack(fill="both", expand=True)

        cols = ("pet", "med", "frequency", "today_status")
        tree = ttk.Treeview(table_card, columns=cols, show="headings",
                            style="Pink.Treeview", height=max(len(data["schedules"]), 1))
        for col, head, w in zip(cols,
                                ("Pet", "Medication", "Frequency", "Today's Status"),
                                [140, 160, 130, 200]):
            tree.heading(col, text=head)
            tree.column(col, width=w, anchor="center")
        tree.pack(fill="both", expand=True)

        for sc in data["schedules"]:
            status_label, _ = schedule_status(sc, data["intakes"])
            tree.insert("", "end", values=(sc["pet"], sc["med"], sc["frequency"], status_label))

        # Delete
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
                  bg=DANGER, fg=WHITE, font=("Segoe UI Bold", 9),
                  bd=0, padx=12, pady=6, cursor="hand2",
                  command=delete_schedule).pack()

    # ── RECORD INTAKE ─────────────────────────────────────────────────────────

    def show_record_intake(self):
        self._clear()
        data = load_data()
        cont = tk.Frame(self.main, bg=BG, padx=40, pady=28)
        cont.pack(fill="both", expand=True)

        tk.Label(cont, text="Record Medication Intake", font=("Segoe UI Bold", 20),
                 bg=BG, fg=TEXT).pack(anchor="w", pady=(0, 16))

        card = self._card(cont, padx=28, pady=28)
        card.pack(fill="x")

        self._field_label(card, "Select Pet")
        pet_names = [p["name"] for p in data["pets"]] or ["No pets added"]
        pet_cb = ttk.Combobox(card, values=pet_names, state="readonly", font=("Segoe UI", 11))
        pet_cb.pack(fill="x", ipady=6)
        if pet_names:
            pet_cb.current(0)

        self._field_label(card, "Medication Name")
        med_ent = self._entry(card)

        self._field_label(card, "Dosage (e.g. 1 pill, 5ml)")
        dose_ent = self._entry(card)

        self._field_label(card, "Given By")
        user_ent = self._entry(card)

        def save_intake():
            pet  = pet_cb.get()
            med  = med_ent.get().strip()
            dose = dose_ent.get().strip()
            user = user_ent.get().strip()
            if pet == "No pets added" or not med or not dose:
                messagebox.showwarning("Missing Fields", "Pet, medication, and dosage are required.")
                return
            data["intakes"].append({
                "date":     datetime.now().strftime("%Y-%m-%d %I:%M %p"),
                "pet":      pet,
                "med":      med,
                "dose":     dose,
                "given_by": user,
                "status":   "Given ✅"
            })
            save_data(data)
            messagebox.showinfo("Success", "✅ Intake recorded!")
            self.show_dashboard()

        self._primary_btn(card, "Record Intake", save_intake)

    # ── VIEW RECORDS ──────────────────────────────────────────────────────────

    def show_view_records(self):
        self._clear()
        data = load_data()
        cont = tk.Frame(self.main, bg=BG, padx=40, pady=28)
        cont.pack(fill="both", expand=True)

        tk.Label(cont, text="View Records", font=("Segoe UI Bold", 20),
                 bg=BG, fg=TEXT).pack(anchor="w")

        tab_frame = tk.Frame(cont, bg=BG)
        tab_frame.pack(fill="x", pady=14)

        table_cont = tk.Frame(cont, bg=BG)
        table_cont.pack(fill="both", expand=True)

        tab_btns = {}

        def display_tab(cat, pet_filter="All"):
            for c, b in tab_btns.items():
                b.configure(bg=COLOR1 if c == cat else WHITE,
                            fg=WHITE  if c == cat else TEXT2,
                            font=("Segoe UI Bold", 10) if c == cat else ("Segoe UI", 10))

            for w in table_cont.winfo_children():
                w.destroy()

            card = self._card(table_cont, padx=16, pady=16)
            card.pack(fill="both", expand=True)

            # Per-pet filter only on history tab
            if cat == "intakes":
                filter_frame = tk.Frame(card, bg=CARD)
                filter_frame.pack(fill="x", pady=(0, 10))
                tk.Label(filter_frame, text="Filter by pet:", bg=CARD,
                         fg=TEXT2, font=("Segoe UI Bold", 9)).pack(side="left", padx=(0, 8))
                pet_names = ["All"] + [p["name"] for p in data["pets"]]
                filter_cb = ttk.Combobox(filter_frame, values=pet_names,
                                         state="readonly", font=("Segoe UI", 10), width=20)
                filter_cb.pack(side="left")
                filter_cb.set(pet_filter)
                filter_cb.bind("<<ComboboxSelected>>",
                               lambda e: display_tab("intakes", filter_cb.get()))

            # Columns per tab
            if cat == "pets":
                cols = ("name", "species", "age")
                heads = ("Pet Name", "Species", "Age")
                rows = data["pets"]
            elif cat == "schedules":
                cols = ("pet", "med", "frequency", "status")
                heads = ("Pet", "Medication", "Frequency", "Today's Status")
                rows = [{"pet": s["pet"], "med": s["med"],
                         "frequency": s["frequency"],
                         "status": schedule_status(s, data["intakes"])[0]}
                        for s in data["schedules"]]
            else:  # intakes
                cols  = ("date", "pet", "med", "dose", "status")
                heads = ("Date", "Pet", "Medication", "Dose", "Status")
                rows  = [i for i in data["intakes"]
                         if pet_filter == "All" or i.get("pet") == pet_filter]

            tree = ttk.Treeview(card, columns=cols, show="headings",
                                style="Pink.Treeview", height=14)
            for col, head in zip(cols, heads):
                tree.heading(col, text=head)
                tree.column(col, anchor="center")
            tree.pack(fill="both", expand=True)

            for row in rows:
                tree.insert("", "end", values=tuple(row[k] for k in cols))

            # Delete (not on intakes — history is immutable)
            if cat != "intakes":
                btn_row = tk.Frame(card, bg=CARD)
                btn_row.pack(anchor="e", pady=(10, 0))

                def delete_item(c=cat):
                    sel = tree.selection()
                    if not sel:
                        return
                    first_val = tree.item(sel[0])["values"][0]
                    key = "pets" if c == "pets" else "schedules"
                    if messagebox.askyesno("Confirm Delete", f"Delete '{first_val}'?"):
                        data[key] = [x for x in data[key] if list(x.values())[0] != first_val]
                        save_data(data)
                        display_tab(c)

                tk.Button(btn_row, text="🗑  Delete Selected",
                          bg=DANGER, fg=WHITE, font=("Segoe UI Bold", 9),
                          bd=0, padx=12, pady=6, cursor="hand2",
                          command=delete_item).pack()

        for label, key in [("Pets 🐾", "pets"), ("Schedules 📅", "schedules"), ("History 📋", "intakes")]:
            b = tk.Button(tab_frame, text=label, font=("Segoe UI", 10),
                          bg=WHITE, fg=TEXT2, bd=0, padx=16, pady=8,
                          cursor="hand2", highlightthickness=1,
                          highlightbackground=BORDER,
                          command=lambda k=key: display_tab(k))
            b.pack(side="left", padx=(0, 8))
            tab_btns[key] = b

        display_tab("pets")


if __name__ == "__main__":
    root = tk.Tk()
    PetMedApp(root)
    root.mainloop()