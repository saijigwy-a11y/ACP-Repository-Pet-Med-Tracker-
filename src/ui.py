import tkinter as tk
from tkinter import messagebox, ttk
from datetime import datetime
from .color_palette import BG, NAVIGATION_COLOR, COLOR1, COLOR2, TEXT, TEXT2, TEXT3, MUTED_PINK, WHITE, BORDER, DANGER, SUCCESS, CARD, NAV_FONT
from .time_n_schedule import schedule_status

FREQUENCIES  = ["Once a day", "Every other day"]
DAYS_OF_WEEK = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

class PetMedApp:
    def __init__(self, root, save_data, load_data):
        self.root = root
        self.root.title("Paws and Pills")
        self.root.geometry("1100x900")
        self.root.configure(bg=BG)
        self.root.resizable(True, True)
        self._setup_styles()
        self._build_layout()
        
        self.save_data = save_data
        self.load_data = load_data
        
        self.show_dashboard()

    # style ng table yees >_<
    def _setup_styles(self): 
        s = ttk.Style()
        s.theme_use("clam")
        s.configure("Pink.Treeview", # default style of all the tables
                    background=WHITE, foreground=TEXT, fieldbackground=WHITE, rowheight=38,
                    font=("Montserrat Regular", 10), borderwidth=0)
        s.configure("Pink.Treeview.Heading", 
                    background=BG, foreground=TEXT2, font=("Montserrat Bold", 9), borderwidth=0, relief="flat")
        s.map("Pink.Treeview", background=[("selected", "#fce7f3")], foreground=[("selected", COLOR1)])

    # NAVIGATION 
    def _build_layout(self):
        navbar = tk.Frame(self.root, bg=NAVIGATION_COLOR, height=64)
        navbar.pack(side="top", fill="x")
        navbar.pack_propagate(False)

        tk.Label(navbar, text="Paws and Pills", font=("Rubik Spray Paint Regular", 16), bg=NAVIGATION_COLOR, fg=COLOR1).pack(side="left", padx=24)

        self._nav_btns = [] # to keep references for updating styles on click
        nav_items = [ 
            ("Dashboard",     self.show_dashboard),
            ("Add Pet",       self.show_add_pet),
            ("Add Medication & Schedules",     self.show_schedules),
            ("Record Intake", self.show_record_intake),
            ("View Records",  self.show_view_records),
        ]
        links = tk.Frame(navbar, bg=NAVIGATION_COLOR)
        links.pack(side="left", padx=16)
        for text, cmd in nav_items:
            btn = tk.Button(links, text=text, font=NAV_FONT, bg=NAVIGATION_COLOR, fg=TEXT2, bd=0, padx=14, pady=8, 
                            cursor="heart", activebackground="#fff0f7", activeforeground=COLOR1,
                            relief="flat", command=lambda c=cmd, t=text: self._nav(c, t))
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

    # WIDGETS/STYLES 

    def _card(self, parent, padx=20, pady=20): # card like frame for forms and tables
        return tk.Frame(parent, bg=CARD, highlightthickness=1,
                        highlightbackground=BORDER, padx=padx, pady=pady)

    def _section(self, parent, text): # for section headers like "Medication Status", "Current Schedules"
        tk.Label(parent, text=text, font=("Montserrat Bold", 12),
                 bg=BG, fg=TEXT).pack(anchor="w", pady=(14, 4))

    def _field_label(self, parent, text): # for labels above form fields like "Pet Name", "Medication"
        tk.Label(parent, text=text, bg=CARD, fg=TEXT2,
                 font=("Montserrat Bold", 10)).pack(anchor="w", pady=(10, 2))

    def _entry(self, parent): # pag nag eentry so consistent yung style
        e = tk.Entry(parent, font=("Montserrat Regular", 11), bd=0,
                     highlightthickness=1, highlightbackground="#f3e8ff",
                     bg="#fdf4ff", fg=TEXT)
        e.pack(fill="x", ipady=9)
        return e

    def _scrollable(self): # so we can scroll.
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

    def _primary_btn(self, parent, text, command): # style ng buttons pag nag sasave 
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

    def _time_picker(self, parent):
        frame = tk.Frame(parent, bg=CARD)
        frame.pack(fill="x", pady=(4, 2))

        # HR SPINBOX
        hour_var = tk.StringVar(value="08")
        hour_sb = tk.Spinbox(
            frame, from_=1, to=12, textvariable=hour_var,
            width=3, font=("Montserrat Regular", 11), bd=0,
            highlightthickness=1, highlightbackground="#f3e8ff",
            bg="#fdf4ff", fg=TEXT, justify="center",
            format="%02.0f", wrap=True
        )
        hour_sb.pack(side="left")

        tk.Label(frame, text=":", bg=CARD, fg=TEXT,
                 font=("Montserrat Bold", 13)).pack(side="left", padx=2)

        # MIN SPINBOX
        minute_var = tk.StringVar(value="00")
        minute_sb = tk.Spinbox(
            frame, values=[f"{m:02d}" for m in range(0, 60, 5)],
            textvariable=minute_var,
            width=3, font=("Montserrat Regular", 11), bd=0,
            highlightthickness=1, highlightbackground="#f3e8ff",
            bg="#fdf4ff", fg=TEXT, justify="center", wrap=True
        )
        minute_sb.pack(side="left")

        # AM/PM
        ampm_var = tk.StringVar(value="AM")

        def toggle_ampm():
            ampm_var.set("PM" if ampm_var.get() == "AM" else "AM")
            ampm_btn.configure(
                bg=COLOR1 if ampm_var.get() == "PM" else "#fce7f3",
                fg=WHITE   if ampm_var.get() == "PM" else COLOR1
            )

        ampm_btn = tk.Button(
            frame, textvariable=ampm_var, command=toggle_ampm,
            bg="#fce7f3", fg=COLOR1, font=("Montserrat Bold", 10),
            bd=0, padx=10, pady=4, cursor="hand2",
            activebackground="#f9a8d4", relief="flat"
        )
        ampm_btn.pack(side="left", padx=(6, 0))

        def get_time():
            h = hour_var.get().strip()
            m = minute_var.get().strip()
            try:
                h = f"{int(h):02d}"
            except ValueError:
                h = "08"
            try:
                m = f"{int(m):02d}"
            except ValueError:
                m = "00"
            return f"{h}:{m} {ampm_var.get()}"

        return get_time

# DASHBOARD 

    def show_dashboard(self):
        self._clear()
        data = self.load_data()
        _, cont = self._scrollable()

        # Greeting (ello, welcome to p&p)
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
                 font=("Rubik Spray Paint Regular", 22), bg="#fce7f3", fg=TEXT3).pack(anchor="center", pady=0)
        tk.Label(text_frame, text="Here's the quick overview of your pets' medication schedules and status.",
                 font=("Montserrat Regular", 10), bg="#fce7f3", fg="#2E2E2E").pack(anchor="center", pady=(4, 0))

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
            top = tk.Frame(card, bg=CARD) # used 
            top.pack(fill="both", expand=True)
            tk.Label(top, text=kyotie,  font=("Montserrat Bold", 15), bg=CARD, fg=MUTED_PINK).pack(side="top")
            tk.Label(top, text=label, font=("Montserrat Bold", 20), bg=CARD).pack(side="left")
            tk.Label(top, text=val,   font=("Montserrat Bold", 22), bg=CARD, fg=clr).pack(side="right")

# MEDICATION STATUS
        self._section(cont, "Medication Status")
        sched_card = self._card(cont, padx=16, pady=16)
        sched_card.pack(fill="x", pady=(0, 12))

        if not data["schedules"]:
            tk.Label(sched_card, text="No schedules yet.",
                     font=("Montserrat Regular", 10), bg=CARD, fg=TEXT2).pack(anchor="w")
        else:
            cols = ("pet", "med", "frequency", "days", "time", "today")
            tree = ttk.Treeview(sched_card, columns=cols, show="headings",
                                style="Pink.Treeview", height=min(len(data["schedules"]), 6))
            for col, head, w in zip(cols,
                                    ("Pet", "Medication", "Frequency", "Days", "Time", "Status"),
                                    [110, 130, 110, 160, 80, 140]):
                tree.heading(col, text=head)
                tree.column(col, width=w, anchor="center")
            tree.pack(fill="x")
            for sc in data["schedules"]:
                lbl, _ = schedule_status(sc, data["intakes"])
                days_val = ", ".join(sc["days"]) if sc.get("days") else "Every day"
                time_val = sc.get("time", "—")
                tree.insert("", "end", values=(
                    sc["pet"], sc["med"], sc["frequency"], days_val, time_val, lbl
                ))

# ADD PET 

    def show_add_pet(self):
        self._clear()
        data = self.load_data()
        cont = tk.Frame(self.main, bg=BG, padx=40, pady=28)
        cont.pack(fill="both", expand=True)

        tk.Label(cont, text=" -`♡´-૮₍  ˶•⤙•˶ ₎ა\n|A d d  N e w  P e t|", font=("Rubik Spray Paint Regular", 20),
                 bg=BG, fg=TEXT3).pack(anchor="center")
        tk.Label(cont, text="Let's start by adding your pet's profile. You can add their medication schedules after this.",
                 font=("Montserrat Regular", 11), bg=BG, fg="#2E2E2E").pack(anchor="center")

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
            self.save_data(data)
            messagebox.showinfo("Success", f"✅ {name} has been added!")
            self.show_dashboard()

        self._primary_btn(card, "Save Pet Profile", save)

# SCHEDULES

    def show_schedules(self):
        self._clear()
        data = self.load_data()
        _, cont = self._scrollable()

        tk.Label(cont, text="𐔌՞ ܸ.ˬ.ܸ՞𐦯\n|M e d i c a t i o n  S c h e d u l e s|", font=("Rubik Spray Paint Regular", 20),
                 bg=BG, fg=TEXT3).pack(anchor="center")

        # ADD NEW SCHEDULE FORM
        form_card = self._card(cont, padx=28, pady=24)
        form_card.pack(fill="x", pady=(0, 20))
        tk.Label(form_card, text="ADD NEW SCHEDULE", font=("Montserrat Bold", 12),
                 bg=CARD, fg=TEXT).pack(anchor="w")

        self._field_label(form_card, "Pet")
        pet_names = [p["name"] for p in data["pets"]] or ["No pets added"]
        pet_cb = ttk.Combobox(form_card, values=pet_names, state="readonly",
                              font=("Montserrat Regular", 11))
        pet_cb.pack(fill="x", ipady=6) 
        if pet_names:
            pet_cb.current(0)

        self._field_label(form_card, "Medication Name")
        med_ent = self._entry(form_card)

        self._field_label(form_card, "Medicine Dosage")
        dosage_ent = self._entry(form_card)

        self._field_label(form_card, "Frequency")
        freq_cb = ttk.Combobox(form_card, values=FREQUENCIES, state="readonly",
                               font=("Montserrat Regular", 11))
        freq_cb.pack(fill="x", ipady=6)
        freq_cb.current(0)
        

# TIME PICKER
        self._field_label(form_card, "Time to Give Medication")
        tk.Label(form_card, text="For 'Twice a day', you can add two schedules with different times using once a day frequency.",
                 bg=CARD, fg="#9D5191", font=("Montserrat Regular", 10)).pack(anchor="w", pady=(0, 2))
        get_time = self._time_picker(form_card)

# DAY PICKER
        day_picker_label = tk.Label(form_card, text="Days to give medication",
                                    bg=CARD, fg=TEXT2, font=("Montserrat Bold", 10))
        day_picker_hint  = tk.Label(form_card, bg=CARD, fg="#9D5191",
                                    font=("Montserrat Regular", 10),
                                    text="Leave all unchecked to give every day.")
        day_picker_frame = tk.Frame(form_card, bg=CARD)
        day_vars = {}

        def refresh_day_picker(event=None):
            freq = freq_cb.get()
            nonlocal day_vars

            for w in day_picker_frame.winfo_children(): # clear old checks
                w.destroy()
            
            day_picker_label.pack(anchor="w", pady=(10, 2)) # shows the day picker
            day_picker_hint.pack(anchor="w", pady=(0, 2))
            day_picker_frame.pack(fill="x", pady=(0, 4))

            if freq == "Every other day": # default selection of the days
                defaults = ["Monday", "Wednesday", "Friday"]
            else:
                defaults = DAYS_OF_WEEK[:]

            day_vars = {}
            for day in DAYS_OF_WEEK:
                var = tk.BooleanVar(value=(day in defaults))
                cb = tk.Checkbutton(day_picker_frame, text=day[:3], variable=var, bg=CARD, fg=TEXT, 
                                    selectcolor="#fce7f3", activebackground=CARD,
                                    font=("Montserrat Regular", 9), cursor="hand2")
                cb.pack(side="left", padx=4)
                day_vars[day] = var

        freq_cb.bind("<<ComboboxSelected>>", refresh_day_picker)
        refresh_day_picker()

        def add_schedule():
            pet  = pet_cb.get()
            med  = med_ent.get().strip()
            dosage = dosage_ent.get()
            freq = freq_cb.get()
            if pet == "No pets added" or not med:
                messagebox.showwarning("Missing Fields", "Select a pet and enter a medication name.")
                return
            if any(s["pet"] == pet and s["med"] == med for s in data["schedules"]):
                messagebox.showwarning("Duplicate", f"A schedule for {pet} / {med} already exists.")
                return
            
            selected_days = [d for d, v in day_vars.items() if v.get()]
            if freq == "Every other day" and not selected_days:
                messagebox.showwarning("No Days Selected",
                                       "Please select at least one day for this frequency.")
                return

            data["schedules"].append({ # for saving to database
                "pet":       pet,
                "med":       med,
                "dosage":    dosage,
                "frequency": freq,
                "time":      get_time(),   
                "days":      selected_days   
            })
            self.save_data(data)
            self.show_schedules()

        self._primary_btn(form_card, "Add Schedule", add_schedule)
        
# RECORD INTAKE 

    def show_record_intake(self):
        self._clear()
        data = self.load_data()
        cont = tk.Frame(self.main, bg=BG, padx=40, pady=28)
        cont.pack(fill="both", expand=True)

        tk.Label(cont, text="ദ്ദി◝ ⩊ ◜.ᐟ\n|R e c o r d  M e d i c a t i o n  I n t a k e|", font=("Rubik Spray Paint Regular", 20),
                 bg=BG, fg=TEXT3).pack(anchor="center")

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
        
        self._field_label(card, "Medication Dosage")
        med_dosage = ttk.Combobox(card, state="readonly", font=("Montserrat Regular", 11))
        med_dosage.pack(fill="x", ipady=6)

        # Label to show the scheduled time for the selected med
        sched_time_label = tk.Label(card, text="", bg=CARD, fg=COLOR1,
                                    font=("Montserrat Regular", 9))
        sched_time_label.pack(anchor="w", pady=(2, 0))

        def refresh_meds(event=None):
            pet  = pet_cb.get()
            meds = [s["med"] for s in data["schedules"] if s["pet"] == pet]
            dosages = [s["dosage"] for s in data["schedules"] if s["pet"] == pet]
            
            if meds:
                med_cb["values"] = meds
                med_cb.current(0)
                
                med_dosage["values"] = dosages
                med_dosage.current(0)
            else:
                med_cb["values"] = ["No medicine for this pet."]
                med_cb.set("No medicine for this pet.")
                
                med_dosage["values"] = ["No dosage for this pet."]
                med_dosage.set("No dosage for this pet.")
            refresh_sched_time()

        def refresh_sched_time(event=None):
            pet = pet_cb.get()
            med = med_cb.get()
            dosage = med_dosage.get()
            sched = next((s for s in data["schedules"]
                          if s["pet"] == pet and s["med"] == med and s["dosage"] == dosage), None)
            if sched and sched.get("time"):
                sched_time_label.configure(
                    text=f"⏰ Scheduled time: {sched['time']}", font=("Montserrat Regular", 12)
                )
            else:
                sched_time_label.configure(text="")

        pet_cb.bind("<<ComboboxSelected>>", refresh_meds)
        med_cb.bind("<<ComboboxSelected>>", refresh_sched_time)
        med_dosage.bind("<<ComboboxSelected>>", refresh_sched_time)
        refresh_meds()

        self._field_label(card, "Given By")
        user_ent = self._entry(card)

        def save_intake():
            pet  = pet_cb.get()
            med  = med_cb.get()
            dosage = med_dosage.get()
            user = user_ent.get().strip()
            if pet == "No pets added" or not med or med == "No medicine for this pet.":
                messagebox.showwarning("Missing Fields", "Select a valid pet and medication.")
                return
            data["intakes"].append({
                "date":     datetime.now().strftime("%Y-%m-%d %I:%M %p"),
                "pet":      pet,
                "med":      med,
                "dosage":   dosage,
                "given_by": user,
                "status":   "Given ✅"
            })
            self.save_data(data)
            messagebox.showinfo("Success", "Intake recorded!")
            self.show_dashboard()

        self._primary_btn(card, "Record Intake", save_intake)

# VIEW RECORDS

    def show_view_records(self):
        self._clear()
        data = self.load_data()
        _, cont = self._scrollable()

        tk.Label(cont, text="◝(ᵔᗜᵔ)◜\n|V i e w  R e c o r d s|", font=("Rubik Spray Paint Regular", 20),
                 bg=BG, fg=TEXT3).pack(anchor="center")

        tab_frame = tk.Frame(cont, bg=BG)
        tab_frame.pack(fill="x", pady=14)

        table_cont = tk.Frame(cont, bg=BG)
        table_cont.pack(fill="both", expand=True)

        tab_btns = {}

        def display_tab(cat, pet_filter="All"):
            for c, b in tab_btns.items():
                b.configure(
                    bg=COLOR1 if c == cat else WHITE, fg=WHITE   if c == cat else TEXT2,
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
                cols  = ("pet", "med", "frequency", "time", "days", "status")
                heads = ("Pet", "Medication", "Frequency", "Time", "Days", "Today's Status")
                rows  = [{"pet": s["pet"], "med": s["med"],
                          "frequency": s["frequency"],
                          "time": s.get("time", "—"),
                          "days": ", ".join(s["days"]) if s.get("days") else "Every day",
                          "status": schedule_status(s, data["intakes"])[0]}
                         for s in data["schedules"]]
            else:  # intakes
                cols  = ("date", "pet", "med", "given_by", "status", "dosage")
                heads = ("Date", "Pet", "Medication", "Given By", "Status", "Dosage")
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

            # Delete button
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
                    self.save_data(data)
                    display_tab(c, pf)

            tk.Button(btn_row, text="Delete Selected",
                      bg=DANGER, fg=WHITE, font=("Montserrat Bold", 9),
                      bd=0, padx=12, pady=6, cursor="hand2",
                      command=delete_item).pack()

        for label, key in [("Pets", "pets"), ("Schedules", "schedules"), ("History", "intakes")]:
            b = tk.Button(tab_frame, text=label, font=("Montserrat Bold", 10),
                          bg=WHITE, fg=TEXT2, bd=0, padx=16, pady=8,
                          cursor="hand2", highlightthickness=1, highlightbackground=BORDER,
                          command=lambda k=key: display_tab(k))
            b.pack(side="left", padx=(0, 8))
            tab_btns[key] = b

        display_tab("pets")