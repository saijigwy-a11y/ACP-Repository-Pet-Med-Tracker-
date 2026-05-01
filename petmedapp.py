import tkinter as tk
from tkinter import messagebox, ttk
from datetime import datetime
import json

# ===== COLOR PALETTE =====
BG = "#fdf2f8"
NAVIGATION = "#ffffff"
COLOR1 = "#e879a0"
COLOR2 = "#c084fc"
TEXT_COLOR = "#1e1b4b"
TEXT_COLOR2 = "#9ca3af"
CLR_WHITE = "#ffffff"
BORDER = "#f3e8ff"
NOTSUCCESS = "#f43f5e"
SUCCESS = "#34d399"
CARD_COLOR = "#ffffff"

DATA_FILE = "data.json"

def load_data():
    try:
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {"pets": [], "medications": [], "intakes": []}

def save_data(d):
    with open(DATA_FILE, "w") as f:
        json.dump(d, f, indent=4)

data = load_data()

class PetMedApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Pet Medication Tracker")
        self.root.geometry("1100x720")
        self.root.configure(bg=BG)
        self.root.resizable(True, True)

        self.setup_styles()
        self.build_layout()
        self.show_dashboard()

    def setup_styles(self):
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Pink.Treeview",
                        background=CLR_WHITE,
                        foreground=TEXT_COLOR,
                        fieldbackground=CLR_WHITE,
                        rowheight=38,
                        font=("Segoe UI", 10),
                        borderwidth=0)
        style.configure("Pink.Treeview.Heading",
                        background=BG,
                        foreground=TEXT_COLOR2,
                        font=("Segoe UI Bold", 9),
                        borderwidth=0,
                        relief="flat")
        style.map("Pink.Treeview",
                  background=[("selected", "#fce7f3")],
                  foreground=[("selected", COLOR1)])

    def build_layout(self):
        # ── Top Nav Bar ──
        self.navbar = tk.Frame(self.root, bg=NAVIGATION, height=64)
        self.navbar.pack(side="top", fill="x")
        self.navbar.pack_propagate(False)

        # Brand
        brand_frame = tk.Frame(self.navbar, bg=NAVIGATION)
        brand_frame.pack(side="left", padx=24, pady=10)
        tk.Label(brand_frame, text="Paws and Pills", font=("Segoe UI Bold", 16),
                 bg=NAVIGATION, fg=TEXT_COLOR).pack(side="left")

        # Nav links
        self.nav_btns = []
        nav_items = [
            ("Dashboard", self.show_dashboard),
            ("Add Pet", self.show_add_pet),
            ("Record Intake", self.show_record_intake),
            ("View Records", self.show_view_records),
        ]

        nav_links_frame = tk.Frame(self.navbar, bg=NAVIGATION)
        nav_links_frame.pack(side="left", padx=30)

        for text, cmd in nav_items:
            btn = tk.Button(nav_links_frame, text=text,
                            font=("Segoe UI Semibold", 10),
                            bg=NAVIGATION, fg=TEXT_COLOR2,
                            bd=0, padx=14, pady=8,
                            cursor="hand2",
                            activebackground="#fff0f7",
                            activeforeground=COLOR1,
                            relief="flat",
                            command=lambda c=cmd, t=text: self.nav_handler(c, t))
            btn.pack(side="left", padx=2)
            self.nav_btns.append((btn, text))

        # Thin border under nav
        tk.Frame(self.root, bg=BORDER, height=2).pack(fill="x")

        # ── Main Content ──
        self.main_content = tk.Frame(self.root, bg=BG)
        self.main_content.pack(fill="both", expand=True)

    def nav_handler(self, command, text):
        for btn, t in self.nav_btns:
            is_active = t == text
            btn.configure(
                fg=COLOR1 if is_active else TEXT_COLOR2,
                bg="#fff0f7" if is_active else NAVIGATION,
                font=("Segoe UI Bold", 10) if is_active else ("Segoe UI Semibold", 10)
            )
        command()

    def clear_main(self):
        for widget in self.main_content.winfo_children():
            widget.destroy()

    def create_card(self, parent, padx=20, pady=20):
        return tk.Frame(parent, bg=CARD_COLOR,
                        highlightthickness=1,
                        highlightbackground=BORDER,
                        padx=padx, pady=pady)

    def section_label(self, parent, text):
        tk.Label(parent, text=text, font=("Segoe UI Bold", 11),
                 bg=BG, fg=TEXT_COLOR).pack(anchor="w", pady=(14, 4))

    # ── DASHBOARD ──
    def show_dashboard(self):
        self.clear_main()
        global data
        data = load_data()

        scroll_canvas = tk.Canvas(self.main_content, bg=BG, highlightthickness=0)
        scrollbar = ttk.Scrollbar(self.main_content, orient="vertical", command=scroll_canvas.yview)
        scroll_canvas.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        scroll_canvas.pack(side="left", fill="both", expand=True)

        container = tk.Frame(scroll_canvas, bg=BG, padx=40, pady=28)
        canvas_window = scroll_canvas.create_window((0, 0), window=container, anchor="nw")

        def on_configure(e):
            scroll_canvas.configure(scrollregion=scroll_canvas.bbox("all"))
        container.bind("<Configure>", on_configure)

        def on_canvas_resize(e):
            scroll_canvas.itemconfig(canvas_window, width=e.width)
        scroll_canvas.bind("<Configure>", on_canvas_resize)

        # ── Hero banner ──
        header = tk.Frame(container, bg="#fce7f3", padx=28, pady=22,
                          highlightthickness=1, highlightbackground="#f9a8d4")
        header.pack(fill="x", pady=(0, 20))

        left_header = tk.Frame(header, bg="#fce7f3")
        left_header.pack(side="left", fill="both", expand=True)

        tk.Label(left_header, text="Good day! 👋", font=("Segoe UI", 12),
                 bg="#fce7f3", fg=COLOR1).pack(anchor="w")
        tk.Label(left_header, text="Check your Pets & Medication Schedule",
                 font=("Segoe UI Bold", 18), bg="#fce7f3", fg=TEXT_COLOR).pack(anchor="w", pady=(4, 2))
        tk.Label(left_header, text="Keep your furry friends healthy 🐶🐱",
                 font=("Segoe UI", 10), bg="#fce7f3", fg="#be185d").pack(anchor="w")

        tk.Label(header, text="🐾", font=("Segoe UI", 56), bg="#fce7f3").pack(side="right", padx=20)

        # ── Stat cards for quick overview of your pet's health ──
        stats_row = tk.Frame(container, bg=BG)
        stats_row.pack(fill="x", pady=(0, 6))

        stats = [
            ("🐾", f"{len(data['pets'])}+", "Pets", COLOR1),
            ("💊", f"{len(data['medications'])}+", "Medications", COLOR2),
            ("📋", f"{len(data['intakes'])}+", "Total Logs", "#f59e0b"),
        ]

        for icon, val, label, clr in stats:
            card = self.create_card(stats_row, padx=18, pady=16)
            card.pack(side="left", fill="both", expand=True, padx=(0, 12))
            top = tk.Frame(card, bg=CARD_COLOR)
            top.pack(fill="x")
            tk.Label(top, text=icon, font=("Segoe UI", 20), bg=CARD_COLOR).pack(side="left")
            tk.Label(top, text=val, font=("Segoe UI Bold", 22), bg=CARD_COLOR, fg=clr).pack(side="right")
            tk.Label(card, text=label, font=("Segoe UI", 10), bg=CARD_COLOR, fg=TEXT_COLOR2).pack(anchor="w", pady=(6, 0))

        # ── Recent logs table ──
        self.section_label(container, "Recent Intake History")
        tree_card = self.create_card(container, padx=16, pady=16)
        tree_card.pack(fill="both", expand=True)

        cols = ("date", "pet", "med", "dose", "status")
        tree = ttk.Treeview(tree_card, columns=cols, show="headings",
                            style="Pink.Treeview", height=10)
        for col, w in zip(cols, [170, 110, 130, 100, 100]):
            tree.heading(col, text=col.capitalize())
            tree.column(col, width=w, anchor="center")
        tree.pack(fill="both", expand=True)

        for i in reversed(data["intakes"][-12:]):
            tree.insert("", "end", values=(
                i.get("date"), i.get("pet"), i.get("med"),
                i.get("dose"), i.get("status")))

    # ── ADD PET ──
    def show_add_pet(self):
        self.clear_main()
        container = tk.Frame(self.main_content, bg=BG, padx=40, pady=28)
        container.pack(fill="both", expand=True)

        tk.Label(container, text="Add New Pet", font=("Segoe UI Bold", 20),
                 bg=BG, fg=TEXT_COLOR).pack(anchor="w", pady=(0, 16))

        card = self.create_card(container, padx=28, pady=28)
        card.pack(fill="x")

        def field_label(text):
            tk.Label(card, text=text, bg=CARD_COLOR, fg=TEXT_COLOR2,
                     font=("Segoe UI Bold", 9)).pack(anchor="w", pady=(10, 2))

        def styled_entry():
            pet = tk.Entry(card, font=("Segoe UI", 11), bd=0,
                         highlightthickness=1, highlightbackground="#f3e8ff",
                         bg="#fdf4ff", fg=TEXT_COLOR)
            pet.pack(fill="x", ipady=9)
            return pet

        field_label("Pet Name")
        name_ent = styled_entry()

        field_label("Species")
        species_ent = styled_entry()

        field_label("Age (years)")
        age_ent = styled_entry()

        def handle_save():
            name = name_ent.get().strip()
            species = species_ent.get().strip()
            age = age_ent.get().strip()
            if not name or not age:
                messagebox.showwarning("Missing Fields", "Please fill in all fields.")
                return
            data["pets"].append({"name": name, "species": species, "age": age})
            save_data(data)
            messagebox.showinfo("Success", f"✅ {name} has been added!")
            self.show_dashboard()

        tk.Frame(card, bg=CARD_COLOR, height=14).pack()
        tk.Button(card, text="Save Pet Profile",
                  bg=COLOR1, fg=CLR_WHITE,
                  font=("Segoe UI Bold", 11),
                  bd=0, pady=12, cursor="hand2",
                  activebackground="#be185d",
                  command=handle_save).pack(fill="x")

    # ── RECORD INTAKE ──
    def show_record_intake(self):
        self.clear_main()
        global data
        data = load_data()

        container = tk.Frame(self.main_content, bg=BG, padx=40, pady=28)
        container.pack(fill="both", expand=True)

        tk.Label(container, text="Record Medication Intake", font=("Segoe UI Bold", 20),
                 bg=BG, fg=TEXT_COLOR).pack(anchor="w", pady=(0, 16))

        card = self.create_card(container, padx=28, pady=28)
        card.pack(fill="x")

        def field_label(text):
            tk.Label(card, text=text, bg=CARD_COLOR, fg=TEXT_COLOR2,
                     font=("Segoe UI Bold", 9)).pack(anchor="w", pady=(10, 2))

        def styled_entry():
            e = tk.Entry(card, font=("Segoe UI", 11), bd=0,
                         highlightthickness=1, highlightbackground="#f3e8ff",
                         bg="#fdf4ff", fg=TEXT_COLOR)
            e.pack(fill="x", ipady=9)
            return e

        field_label("Select Pet")
        pet_list = [p["name"] for p in data["pets"]] or ["No pets added"]
        pet_combo = ttk.Combobox(card, values=pet_list, state="readonly", font=("Segoe UI", 11))
        pet_combo.pack(fill="x", ipady=6)
        if pet_list:
            pet_combo.current(0)

        field_label("Medication Name")
        med_ent = styled_entry()

        field_label("Dosage (e.g. 1 pill, 5ml)")
        dose_ent = styled_entry()

        field_label("Given By")
        user_ent = styled_entry()

        def save_intake():
            p = pet_combo.get()
            m = med_ent.get().strip()
            d = dose_ent.get().strip()
            u = user_ent.get().strip()

            if p == "No pets added" or not m or not d:
                messagebox.showwarning("Missing Fields", "Please fill in all required fields.")
                return

            if not any(med["name"] == m for med in data["medications"]):
                data["medications"].append({"name": m, "dose": d})

            data["intakes"].append({
                "date": datetime.now().strftime("%Y-%m-%d %I:%M %p"),
                "pet": p, "med": m, "dose": d,
                "given_by": u, "status": "Given ✅"
            })
            save_data(data)
            messagebox.showinfo("Success", "✅ Intake recorded successfully!")
            self.show_dashboard()

        tk.Frame(card, bg=CARD_COLOR, height=14).pack()
        tk.Button(card, text="Record Intake",
                  bg=COLOR1, fg=CLR_WHITE,
                  font=("Segoe UI Bold", 11),
                  bd=0, pady=12, cursor="hand2",
                  activebackground="#be185d",
                  command=save_intake).pack(fill="x")

    # ── VIEW RECORDS ──
    def show_view_records(self):
        self.clear_main()
        global data
        data = load_data()

        container = tk.Frame(self.main_content, bg=BG, padx=40, pady=28)
        container.pack(fill="both", expand=True)

        tk.Label(container, text="View Records", font=("Segoe UI Bold", 20),
                 bg=BG, fg=TEXT_COLOR).pack(anchor="w")

        tab_frame = tk.Frame(container, bg=BG)
        tab_frame.pack(fill="x", pady=14)

        table_container = tk.Frame(container, bg=BG)
        table_container.pack(fill="both", expand=True)

        tab_btns = {}

        def display_tab(cat):
            for c, b in tab_btns.items():
                if c == cat:
                    b.configure(bg=COLOR1, fg=CLR_WHITE, font=("Segoe UI Bold", 10))
                else:
                    b.configure(bg=CLR_WHITE, fg=TEXT_COLOR2, font=("Segoe UI", 10))

            for w in table_container.winfo_children():
                w.destroy()

            card = self.create_card(table_container, padx=16, pady=16)
            card.pack(fill="both", expand=True)

            if cat == "pets":
                cols = ("name", "species", "age")
                headings = ("Pet Name", "Species", "Age")
            elif cat == "medications":
                cols = ("name", "dose")
                headings = ("Medication", "Standard Dosage")
            else:
                cols = ("date", "pet", "med", "dose", "status")
                headings = ("Date", "Pet", "Medication", "Dose", "Status")

            tree = ttk.Treeview(card, columns=cols, show="headings",
                                style="Pink.Treeview", height=14)
            for i, col in enumerate(cols):
                tree.heading(col, text=headings[i])
                tree.column(col, anchor="center")
            tree.pack(fill="both", expand=True)

            for item in data[cat]:
                tree.insert("", "end", values=tuple(list(item.values())[:len(cols)]))

            def delete_item():
                selected = tree.selection()
                if not selected:
                    return
                val = tree.item(selected[0])["values"][0]
                if messagebox.askyesno("Confirm Delete", f"Delete '{val}'?"):
                    data[cat] = [i for i in data[cat] if list(i.values())[0] != val]
                    save_data(data)
                    display_tab(cat)

            btn_row = tk.Frame(card, bg=CARD_COLOR)
            btn_row.pack(anchor="e", pady=(10, 0))
            tk.Button(btn_row, text="🗑  Delete Selected",
                      bg=NOTSUCCESS, fg=CLR_WHITE,
                      font=("Segoe UI Bold", 9),
                      bd=0, padx=12, pady=6,
                      cursor="hand2",
                      command=delete_item).pack()

        for label, key in [("Pets 🐾", "pets"), ("Medications 💊", "medications"), ("History 📋", "intakes")]:
            b = tk.Button(tab_frame, text=label,
                          font=("Segoe UI", 10),
                          bg=CLR_WHITE, fg=TEXT_COLOR2,
                          bd=0, padx=16, pady=8,
                          cursor="hand2",
                          highlightthickness=1, highlightbackground=BORDER,
                          command=lambda k=key: display_tab(k))
            b.pack(side="left", padx=(0, 8))
            tab_btns[key] = b

        display_tab("pets")


if __name__ == "__main__":
    root = tk.Tk()
    app = PetMedApp(root)
    root.mainloop()