import tkinter as tk
from tkinter import ttk, messagebox
import database
from model import Service

class ServiceDialog(tk.Toplevel):
    def __init__(self, parent, title: str, svc: Service | None = None):
        super().__init__(parent)
        self.title(title)
        self.resizable(True, True)
        self.parent = parent
        self.svc = svc
        self.result = None

        tk.Label(self, text="Name:").grid(row=0, column=0, sticky="e", padx=5, pady=5)
        self.entry_name = tk.Entry(self, width=40)
        self.entry_name.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(self, text="URL:").grid(row=1, column=0, sticky="e", padx=5, pady=5)
        self.entry_url = tk.Entry(self, width=40)
        self.entry_url.grid(row=1, column=1, padx=5, pady=5)

        tk.Label(self, text="Category:").grid(row=2, column=0, sticky="e", padx=5, pady=5)
        self.entry_category = tk.Entry(self, width=40)
        self.entry_category.grid(row=2, column=1, padx=5, pady=5)

        tk.Label(self, text="Description:").grid(row=3, column=0, sticky="ne", padx=5, pady=5)
        self.text_description = tk.Text(self, width=40, height=8, wrap="word")
        self.text_description.grid(row=3, column=1, padx=5, pady=5)

    
        btn_frame = tk.Frame(self)
        btn_frame.grid(row=4, column=0, columnspan=2, pady=10)
        tk.Button(btn_frame, text="Save", width=12, command=self.on_save).pack(side="left", padx=5)
        tk.Button(btn_frame, text="Cancel",    width=12, command=self.destroy).pack(side="left")

        if svc:
            self.entry_name.insert(0, svc.name)
            self.entry_url.insert(0, svc.url)
            self.entry_category.insert(0, svc.category)
            self.text_description.insert("1.0", svc.description)

        self.entry_name.focus()
        self.grab_set()
        self.wait_window()

    def on_save(self):
        name = self.entry_name.get().strip()
        url = self.entry_url.get().strip()
        category = self.entry_category.get().strip()
        description = self.text_description.get("1.0", "end").strip()

        if not name or not url or not description:
            messagebox.showwarning("Validation error", "Label «Name», «URL» and «Description» mandatory.")
            return

        if self.svc:
            self.svc.name = name
            self.svc.url = url
            self.svc.category = category
            self.svc.description = description
            database.update_service(self.svc)
        else:
            new_svc = Service(id=0, name=name, url=url, description=description, category=category)
            database.add_service(new_svc)

        self.destroy()

class ServiceApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Catalog of web-services")
        self.geometry("800x500")
        database.initialize_db()
        self.services: list[Service] = []
        self._build_ui()
        self._load_services()

    def _build_ui(self):
        search_frame = tk.Frame(self)
        search_frame.pack(fill="x", padx=10, pady=5)
        tk.Label(search_frame, text="Search:").pack(side="left")
        self.var_search = tk.StringVar()
        ent = tk.Entry(search_frame, textvariable=self.var_search, width=30)
        ent.pack(side="left", padx=5)
        ent.bind("<KeyRelease>", lambda e: self._filter())

        cols = ("id", "name", "url", "category")
        self.tree = ttk.Treeview(self, columns=cols, show="headings")
        for col, text, width in [
            ("id", "ID", 50),
            ("name", "Name", 200),
            ("url", "URL", 300),
            ("category", "Category", 150),
        ]:
            self.tree.heading(col, text=text)
            self.tree.column(col, width=width, anchor="w")
        self.tree.pack(fill="both", expand=True, padx=10, pady=5)

        btn_frame = tk.Frame(self)
        btn_frame.pack(fill="x", padx=10, pady=5)
        tk.Button(btn_frame, text="Add",  command=self._on_add).pack(side="right", padx=5)
        tk.Button(btn_frame, text="Update", command=self._on_edit).pack(side="right", padx=5)
        tk.Button(btn_frame, text="Delete", command=self._on_delete).pack(side="right")

    def _load_services(self):
        self.services = database.get_all_services()
        self._display(self.services)

    def _display(self, lst: list[Service]):
        for i in self.tree.get_children():
            self.tree.delete(i)
        for svc in lst:
            self.tree.insert("", "end", values=(svc.id, svc.name, svc.url, svc.category))

    def _filter(self):
        q = self.var_search.get().lower()
        filtered = [s for s in self.services if q in s.name.lower() or q in s.category.lower()]
        self._display(filtered)

    def _on_add(self):
        ServiceDialog(self, "Service creation")
        self._load_services()

    def _on_edit(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("Attention", "Choose service for update.")
            return
        item = self.tree.item(sel[0])["values"]
        svc = database.get_service_by_id(item[0])
        if svc:
            ServiceDialog(self, "Service updating", svc)
            self._load_services()

    def _on_delete(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("Attention", "Choose service for deleting.")
            return
        item = self.tree.item(sel[0])["values"]
        if messagebox.askyesno("Confirmation", f"Delete service «{item[0]}»?"):
            database.delete_service(item[0])
            self._load_services()

if __name__ == "__main__":
    app = ServiceApp()
    app.mainloop()
