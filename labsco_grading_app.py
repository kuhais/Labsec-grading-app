"""
LabsCo Training Division - Field Evaluation Grading Tool
----------------------------------------------------------
"""
import os
import datetime
import webbrowser
import tkinter as tk
from tkinter import ttk, messagebox, filedialog

from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
)


# ---------------------------------------------------------------------
# Evaluation data
# ---------------------------------------------------------------------

EVAL_1 = {
    "title": "Field Evaluation 1 — Patrol",
    "rubric_url": "https://www.quickrubric.com/r#/qr/ummhi1234/field-evaluation-1--20-marks-",
    "sections": [
        {
            "name": "Driving",
            "max": 10,
            "pass_threshold": 5,
            "deductions": [
                ("Running a stop sign", 0.5),
                ("Not indicating when switching lanes or turning", 0.5),
                ("Running a red light", 1.0),
                ("Other traffic violation (Mayflower State Code)", 0.5),
            ],
        },
        {
            "name": "Patrol",
            "max": 10,
            "pass_threshold": 5,
            "deductions": [
                ("Disrespectful attitude towards the public", 0.5),
                ("Disrespectful attitude towards the examiner", 1.0),
                ("Violation of one of our policies", 1.0),
                ("Misuse of equipment on a civilian", 5.0),
                ("Poor / no communication on the radio", 2.0),
            ],
        },
    ],
}

EVAL_2 = {
    "title": "Field Evaluation 2 — Convoy Driving",
    "rubric_url": "https://www.quickrubric.com/r#/qr/ummhi1234/field-evaluation-2--25-marks-total-",
    "sections": [
        {
            "name": "Convoy Driving",
            "max": 15,
            "pass_threshold": 7.5,
            "deductions": [
                ("Minor traffic violation", 0.5),
                ("Major traffic violation", 2.0),
                ("Client(s) got killed during convoy", 2.0),
                ("Not following basic convoy procedures", 5.0),
                ("Not following/guiding the client to the right destination", 3.0),
            ],
        },
        {
            "name": "Client Interaction",
            "max": 10,
            "pass_threshold": 5,
            "deductions": [
                ("A rude remark towards the client", 1.0),
                ("Collecting payment improperly (exempt if UCPS/Meyerhauser staff)", 2.0),
                ("Poor communication with the client", 2.0),
            ],
        },
    ],
}


# ---------------------------------------------------------------------
# Scrollable container helper
# ---------------------------------------------------------------------

class ScrollableFrame(ttk.Frame):
    def __init__(self, container, *args, **kwargs):
        super().__init__(container, *args, **kwargs)
        canvas = tk.Canvas(self, borderwidth=0, highlightthickness=0)
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=canvas.yview)
        self.scrollable_frame = ttk.Frame(canvas)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all")),
        )
        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        def _on_wheel(event):
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

        canvas.bind_all("<MouseWheel>", _on_wheel)


# ---------------------------------------------------------------------
# Main application
# ---------------------------------------------------------------------

class GradingApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("LabsCo Field Evaluation Grading Tool")
        self.geometry("640x700")
        self.minsize(560, 480)

        style = ttk.Style(self)
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass

        self.section_widgets = []
        self.overall_label = None
        self.latest_results = None

        self.show_menu()

    def clear(self):
        for widget in self.winfo_children():
            widget.destroy()

    # ---------------- Menu screen ----------------

    def show_menu(self):
        self.clear()
        ttk.Label(
            self, text="LabsCo Training Division", font=("Segoe UI", 17, "bold")
        ).pack(pady=(40, 4))
        ttk.Label(
            self, text="Field Evaluation Grading Tool", font=("Segoe UI", 11)
        ).pack(pady=(0, 35))

        ttk.Button(
            self,
            text="Field Evaluation 1 (Patrol)",
            command=lambda: self.show_eval(EVAL_1),
        ).pack(pady=8, ipadx=12, ipady=10, fill="x", padx=80)

        ttk.Button(
            self,
            text="Field Evaluation 2 (Convoy Driving)",
            command=lambda: self.show_eval(EVAL_2),
        ).pack(pady=8, ipadx=12, ipady=10, fill="x", padx=80)

        ttk.Button(
            self,
            text="Grading Rubric for Field Evaluation 1",
            command=lambda: webbrowser.open(EVAL_1["rubric_url"]),
        ).pack(pady=8, ipadx=12, ipady=10, fill="x", padx=80)

        ttk.Button(
            self,
            text="Grading Rubric for Field Evaluation 2",
            command=lambda: webbrowser.open(EVAL_2["rubric_url"]),
        ).pack(pady=8, ipadx=12, ipady=10, fill="x", padx=80)

        ttk.Label(
            self,
            text="Note: failing one section still fails the whole evaluation.",
            font=("Segoe UI", 9),
            foreground="#666666",
        ).pack(pady=(30, 0))

    # ---------------- Scoring screen ----------------

    def show_eval(self, eval_data):
        self.clear()
        self.current_eval = eval_data

        top = ttk.Frame(self)
        top.pack(fill="x", padx=12, pady=10)
        ttk.Button(top, text="← Back to Menu", command=self.show_menu).pack(side="left")
        ttk.Button(top, text="Reset", command=lambda: self.show_eval(eval_data)).pack(side="right")

        ttk.Label(self, text=eval_data["title"], font=("Segoe UI", 15, "bold")).pack(pady=(0, 10))

        names_frame = ttk.Frame(self)
        names_frame.pack(fill="x", padx=12, pady=(0, 8))
        names_frame.columnconfigure(1, weight=1)
        names_frame.columnconfigure(3, weight=1)

        ttk.Label(names_frame, text="Examiner name:").grid(row=0, column=0, sticky="w", padx=(0, 6))
        self.filler_name_var = tk.StringVar(value="")
        ttk.Entry(names_frame, textvariable=self.filler_name_var).grid(row=0, column=1, sticky="ew", padx=(0, 16))

        ttk.Label(names_frame, text="Trainee name:").grid(row=0, column=2, sticky="w", padx=(0, 6))
        self.trainee_name_var = tk.StringVar(value="")
        ttk.Entry(names_frame, textvariable=self.trainee_name_var).grid(row=0, column=3, sticky="ew")

        scroll = ScrollableFrame(self)
        scroll.pack(fill="both", expand=True, padx=12)

        self.section_widgets = []

        for section in eval_data["sections"]:
            frame = ttk.LabelFrame(
                scroll.scrollable_frame,
                text=f'{section["name"]}   (max {section["max"]:g}  •  pass >= {section["pass_threshold"]:g})',
            )
            frame.pack(fill="x", pady=8, padx=4)

            section_vars = []
            for name, points in section["deductions"]:
                row = ttk.Frame(frame)
                row.pack(fill="x", pady=3, padx=8)
                row.columnconfigure(0, weight=1)

                ttk.Label(
                    row,
                    text=f"{name}  (-{points:g} each)",
                    wraplength=420,
                    justify="left",
                ).grid(row=0, column=0, sticky="w")

                var = tk.IntVar(value=0)
                spin = ttk.Spinbox(row, from_=0, to=50, width=4, textvariable=var)
                spin.grid(row=0, column=1, sticky="e", padx=(10, 0))
                var.trace_add("write", lambda *args: self.recalculate())

                section_vars.append((var, points, name))

            # ---- Custom deduction block ----
            ttk.Separator(frame, orient="horizontal").pack(fill="x", pady=(6, 6), padx=8)

            custom_frame = ttk.Frame(frame)
            custom_frame.pack(fill="x", padx=8, pady=(0, 4))

            ttk.Label(
                custom_frame,
                text="Custom deduction (for anything not listed above):",
                font=("Segoe UI", 9, "italic"),
            ).pack(anchor="w")

            custom_var = tk.DoubleVar(value=0.0)

            quick_row = ttk.Frame(custom_frame)
            quick_row.pack(fill="x", pady=(4, 2))
            for amt in (0.5, 1, 2, 5):
                ttk.Button(
                    quick_row,
                    text=f"-{amt:g}",
                    width=5,
                    command=lambda a=amt, cv=custom_var: self.add_custom(cv, a),
                ).pack(side="left", padx=3)

            undo_row = ttk.Frame(custom_frame)
            undo_row.pack(fill="x", pady=(0, 2))
            ttk.Label(undo_row, text="Undo:", font=("Segoe UI", 9)).pack(side="left", padx=(0, 4))
            for amt in (0.5, 1, 2, 5):
                ttk.Button(
                    undo_row,
                    text=f"+{amt:g}",
                    width=5,
                    command=lambda a=amt, cv=custom_var: self.add_custom(cv, -a),
                ).pack(side="left", padx=3)

            entry_row = ttk.Frame(custom_frame)
            entry_row.pack(fill="x", pady=(2, 2))
            custom_entry_var = tk.StringVar(value="")
            ttk.Entry(entry_row, width=8, textvariable=custom_entry_var).pack(side="left")
            ttk.Button(
                entry_row,
                text="Apply amount",
                command=lambda cv=custom_var, ev=custom_entry_var: self.apply_custom_entry(cv, ev),
            ).pack(side="left", padx=6)
            ttk.Button(
                entry_row,
                text="Clear custom",
                command=lambda cv=custom_var: self.clear_custom(cv),
            ).pack(side="left", padx=6)

            custom_label = ttk.Label(custom_frame, text="Custom deductions applied: -0", font=("Segoe UI", 9))
            custom_label.pack(anchor="w", pady=(4, 0))

            custom_var.trace_add("write", lambda *args: self.recalculate())

            # ---- Section notes block ----
            ttk.Separator(frame, orient="horizontal").pack(fill="x", pady=(6, 6), padx=8)

            notes_frame = ttk.Frame(frame)
            notes_frame.pack(fill="x", padx=8, pady=(0, 6))

            ttk.Label(
                notes_frame,
                text=f"Notes for {section['name']} section:",
                font=("Segoe UI", 9, "italic"),
            ).pack(anchor="w", pady=(0, 3))

            section_notes_text = tk.Text(
                notes_frame,
                height=3,
                wrap="word",
                font=("Segoe UI", 9),
                relief="solid",
                borderwidth=1,
            )
            section_notes_text.pack(fill="x")

            result_label = ttk.Label(frame, text="", font=("Segoe UI", 10, "bold"))
            result_label.pack(anchor="e", padx=8, pady=(8, 6))

            self.section_widgets.append({
                "section": section,
                "vars": section_vars,
                "label": result_label,
                "custom_var": custom_var,
                "custom_label": custom_label,
                "notes_widget": section_notes_text,
            })

        # ---- Overall notes block ----
        overall_notes_frame = ttk.LabelFrame(scroll.scrollable_frame, text="Overall Notes / Comments")
        overall_notes_frame.pack(fill="x", pady=8, padx=4)

        ttk.Label(
            overall_notes_frame,
            text="General observations, recommendations, or anything else to include in the report:",
            font=("Segoe UI", 9, "italic"),
        ).pack(anchor="w", padx=8, pady=(6, 3))

        self.overall_notes_text = tk.Text(
            overall_notes_frame,
            height=4,
            wrap="word",
            font=("Segoe UI", 9),
            relief="solid",
            borderwidth=1,
        )
        self.overall_notes_text.pack(fill="x", padx=8, pady=(0, 8))

        self.overall_label = ttk.Label(self, text="", font=("Segoe UI", 13, "bold"))
        self.overall_label.pack(pady=10)

        btn_row = ttk.Frame(self)
        btn_row.pack(pady=(0, 14))
        ttk.Button(btn_row, text="Export PDF", command=self.export_pdf).pack()

        self.recalculate()

    # ---------------- Custom deduction helpers ----------------

    def add_custom(self, custom_var, amount):
        try:
            current = custom_var.get()
        except tk.TclError:
            current = 0.0
        custom_var.set(max(round(current + amount, 2), 0.0))

    def apply_custom_entry(self, custom_var, entry_var):
        text = entry_var.get().strip()
        if not text:
            return
        try:
            amount = abs(float(text))
        except ValueError:
            return
        self.add_custom(custom_var, amount)
        entry_var.set("")

    def clear_custom(self, custom_var):
        custom_var.set(0.0)

    # ---------------- Scoring logic ----------------

    def recalculate(self):
        if not self.section_widgets:
            return

        overall_pass = True
        results_snapshot = []

        for sw in self.section_widgets:
            section = sw["section"]
            total_deduction = 0.0
            deduction_detail = []

            for var, points, name in sw["vars"]:
                try:
                    count = var.get()
                except tk.TclError:
                    count = 0
                if count > 0:
                    subtotal = count * points
                    deduction_detail.append((name, count, points, subtotal))
                    total_deduction += subtotal

            try:
                custom_amount = sw["custom_var"].get()
            except tk.TclError:
                custom_amount = 0.0

            if custom_amount > 0:
                deduction_detail.append(("Custom deduction", 1, custom_amount, custom_amount))
            total_deduction += custom_amount

            sw["custom_label"].config(text=f"Custom deductions applied: -{custom_amount:g}")

            score = max(section["max"] - total_deduction, 0)
            passed = score >= section["pass_threshold"]
            overall_pass = overall_pass and passed

            status = "PASS" if passed else "FAIL"
            color = "#1a7f37" if passed else "#c0392b"
            sw["label"].config(
                text=f'Section Score: {score:g} / {section["max"]:g}   ->   {status}',
                foreground=color,
            )

            results_snapshot.append({
                "name": section["name"],
                "score": score,
                "max": section["max"],
                "pass_threshold": section["pass_threshold"],
                "passed": passed,
                "deduction_detail": deduction_detail,
                "total_deduction": total_deduction,
            })

        if self.overall_label is not None:
            final_text = "OVERALL RESULT: PASS" if overall_pass else "OVERALL RESULT: FAIL"
            self.overall_label.config(
                text=final_text,
                foreground="#1a7f37" if overall_pass else "#c0392b",
            )

        self.latest_results = {
            "sections": results_snapshot,
            "overall_pass": overall_pass,
        }

    # ---------------- PDF export ----------------

    def export_pdf(self):
        filler = self.filler_name_var.get().strip()
        trainee = self.trainee_name_var.get().strip()

        if not filler or not trainee:
            messagebox.showwarning(
                "Missing names",
                "Please enter both the examiner name and the trainee name before exporting.",
            )
            return

        eval_data = self.current_eval
        results = self.latest_results

        # Collect notes from each section widget
        section_notes = []
        for sw in self.section_widgets:
            note_text = sw["notes_widget"].get("1.0", "end").strip()
            section_notes.append(note_text)

        overall_notes = self.overall_notes_text.get("1.0", "end").strip()

        safe_trainee = "".join(c for c in trainee if c.isalnum() or c in " _-").strip().replace(" ", "_")
        default_name = f"FieldEval_{safe_trainee}_{datetime.date.today()}.pdf"

        path = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("PDF files", "*.pdf")],
            initialfile=default_name,
            title="Save evaluation report as…",
        )
        if not path:
            return

        self._build_pdf(path, eval_data, filler, trainee, results, section_notes, overall_notes)
        messagebox.showinfo("PDF saved", f"Report saved to:\n{path}")

    def _build_pdf(self, path, eval_data, filler, trainee, results, section_notes, overall_notes):
        doc = SimpleDocTemplate(
            path,
            pagesize=letter,
            leftMargin=0.85 * inch,
            rightMargin=0.85 * inch,
            topMargin=0.9 * inch,
            bottomMargin=0.9 * inch,
        )

        styles = getSampleStyleSheet()
        DARK = colors.HexColor("#1a1a2e")
        GREEN = colors.HexColor("#1a7f37")
        RED = colors.HexColor("#c0392b")
        LIGHT_GRAY = colors.HexColor("#f5f5f5")
        MID_GRAY = colors.HexColor("#cccccc")
        ACCENT = colors.HexColor("#2c3e7a")
        NOTE_BG = colors.HexColor("#fffbe6")
        NOTE_BORDER = colors.HexColor("#e0c84a")

        title_style = ParagraphStyle(
            "ReportTitle",
            parent=styles["Title"],
            fontSize=20,
            textColor=DARK,
            spaceAfter=4,
            fontName="Helvetica-Bold",
        )
        subtitle_style = ParagraphStyle(
            "Subtitle",
            parent=styles["Normal"],
            fontSize=11,
            textColor=ACCENT,
            spaceAfter=2,
            fontName="Helvetica",
        )
        section_heading_style = ParagraphStyle(
            "SectionHeading",
            parent=styles["Heading2"],
            fontSize=13,
            textColor=ACCENT,
            spaceBefore=14,
            spaceAfter=4,
            fontName="Helvetica-Bold",
        )
        normal = ParagraphStyle(
            "Body",
            parent=styles["Normal"],
            fontSize=10,
            leading=14,
            fontName="Helvetica",
        )
        small_italic = ParagraphStyle(
            "SmallItalic",
            parent=styles["Normal"],
            fontSize=9,
            fontName="Helvetica-Oblique",
            textColor=colors.HexColor("#555555"),
        )
        notes_style = ParagraphStyle(
            "NotesBody",
            parent=styles["Normal"],
            fontSize=9,
            leading=13,
            fontName="Helvetica",
            textColor=DARK,
        )
        notes_label_style = ParagraphStyle(
            "NotesLabel",
            parent=styles["Normal"],
            fontSize=9,
            fontName="Helvetica-Bold",
            textColor=colors.HexColor("#7a6000"),
        )

        story = []

        # ---- Header ----
        story.append(Paragraph("LabsCo Training Division", subtitle_style))
        story.append(Paragraph(eval_data["title"], title_style))
        story.append(HRFlowable(width="100%", thickness=1.5, color=ACCENT, spaceAfter=10))

        # ---- Info table ----
        date_str = datetime.datetime.now().strftime("%B %d, %Y  %H:%M")
        info_data = [
            ["Examiner:", filler, "Date:", date_str],
            ["Trainee:", trainee, "", ""],
        ]
        info_table = Table(info_data, colWidths=[1.4 * inch, 2.4 * inch, 0.8 * inch, 2.1 * inch])
        info_table.setStyle(TableStyle([
            ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
            ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
            ("FONTNAME", (2, 0), (2, -1), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 10),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ("TOPPADDING", (0, 0), (-1, -1), 5),
            ("TEXTCOLOR", (0, 0), (-1, -1), DARK),
        ]))
        story.append(info_table)
        story.append(Spacer(1, 14))

        # ---- Overall result banner ----
        overall_pass = results["overall_pass"]
        overall_color = GREEN if overall_pass else RED
        overall_text = "OVERALL RESULT: PASS" if overall_pass else "OVERALL RESULT: FAIL"
        overall_style = ParagraphStyle(
            "Overall",
            parent=styles["Normal"],
            fontSize=14,
            fontName="Helvetica-Bold",
            textColor=colors.white,
            alignment=1,
            spaceAfter=0,
        )
        overall_table = Table([[Paragraph(overall_text, overall_style)]], colWidths=["100%"])
        overall_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), overall_color),
            ("TOPPADDING", (0, 0), (-1, -1), 10),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
            ("LEFTPADDING", (0, 0), (-1, -1), 12),
            ("RIGHTPADDING", (0, 0), (-1, -1), 12),
            ("ROUNDEDCORNERS", [4, 4, 4, 4]),
        ]))
        story.append(overall_table)
        story.append(Spacer(1, 18))

        # ---- Per-section breakdown ----
        for idx, sec in enumerate(results["sections"]):
            passed = sec["passed"]
            sec_color = GREEN if passed else RED
            sec_status = "PASS" if passed else "FAIL"

            heading_style = ParagraphStyle(
                "SecHead",
                parent=styles["Normal"],
                fontSize=12,
                fontName="Helvetica-Bold",
                textColor=colors.white,
            )
            status_style = ParagraphStyle(
                "SecStatus",
                parent=styles["Normal"],
                fontSize=12,
                fontName="Helvetica-Bold",
                textColor=colors.white,
                alignment=2,
            )
            sec_header = Table(
                [[Paragraph(sec["name"], heading_style),
                  Paragraph(sec_status, status_style)]],
                colWidths=["75%", "25%"],
            )
            sec_header.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, -1), sec_color),
                ("TOPPADDING", (0, 0), (-1, -1), 7),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
                ("LEFTPADDING", (0, 0), (0, -1), 10),
                ("RIGHTPADDING", (-1, 0), (-1, -1), 10),
            ]))
            story.append(sec_header)

            score_data = [
                [
                    f"Score: {sec['score']:g} / {sec['max']:g}",
                    f"Pass threshold: {sec['pass_threshold']:g}",
                    f"Points deducted: {sec['total_deduction']:g}",
                ]
            ]
            score_table = Table(score_data, colWidths=["34%", "33%", "33%"])
            score_table.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, -1), LIGHT_GRAY),
                ("FONTNAME", (0, 0), (-1, -1), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 10),
                ("TEXTCOLOR", (0, 0), (-1, -1), DARK),
                ("TOPPADDING", (0, 0), (-1, -1), 6),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
                ("LEFTPADDING", (0, 0), (-1, -1), 10),
                ("LINEBELOW", (0, 0), (-1, -1), 0.5, MID_GRAY),
            ]))
            story.append(score_table)

            if sec["deduction_detail"]:
                ded_header = [["Deduction Reason", "Count", "Pts Each", "Total Deducted"]]
                ded_rows = []
                for desc, count, pts_each, subtotal in sec["deduction_detail"]:
                    ded_rows.append([
                        Paragraph(desc, normal),
                        f"x{count}",
                        f"-{pts_each:g}",
                        f"-{subtotal:g}",
                    ])

                ded_table = Table(
                    ded_header + ded_rows,
                    colWidths=["52%", "12%", "16%", "20%"],
                )
                ded_style = TableStyle([
                    ("BACKGROUND", (0, 0), (-1, 0), ACCENT),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("FONTSIZE", (0, 0), (-1, -1), 9),
                    ("ALIGN", (1, 0), (-1, -1), "CENTER"),
                    ("TOPPADDING", (0, 0), (-1, -1), 5),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
                    ("LEFTPADDING", (0, 0), (-1, -1), 8),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 8),
                    ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, LIGHT_GRAY]),
                    ("GRID", (0, 0), (-1, -1), 0.4, MID_GRAY),
                    ("TEXTCOLOR", (3, 1), (3, -1), RED),
                    ("FONTNAME", (3, 1), (3, -1), "Helvetica-Bold"),
                ])
                ded_table.setStyle(ded_style)
                story.append(ded_table)
            else:
                story.append(Paragraph("No deductions applied in this section.", small_italic))

            # ---- Section notes in PDF ----
            note_text = section_notes[idx] if idx < len(section_notes) else ""
            if note_text:
                note_table = Table(
                    [[
                        Paragraph("📝  Section Notes:", notes_label_style),
                        Paragraph(note_text, notes_style),
                    ]],
                    colWidths=["22%", "78%"],
                )
                note_table.setStyle(TableStyle([
                    ("BACKGROUND", (0, 0), (-1, -1), NOTE_BG),
                    ("TOPPADDING", (0, 0), (-1, -1), 7),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
                    ("LEFTPADDING", (0, 0), (-1, -1), 10),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 10),
                    ("LINEABOVE", (0, 0), (-1, 0), 1, NOTE_BORDER),
                    ("LINEBELOW", (0, 0), (-1, -1), 1, NOTE_BORDER),
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ]))
                story.append(note_table)

            story.append(Spacer(1, 14))

        # ---- Overall notes in PDF ----
        if overall_notes:
            story.append(HRFlowable(width="100%", thickness=0.8, color=MID_GRAY, spaceBefore=4, spaceAfter=8))
            overall_note_table = Table(
                [[
                    Paragraph("📝  Overall Notes & Comments:", notes_label_style),
                    Paragraph(overall_notes, notes_style),
                ]],
                colWidths=["30%", "70%"],
            )
            overall_note_table.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, -1), NOTE_BG),
                ("TOPPADDING", (0, 0), (-1, -1), 9),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 9),
                ("LEFTPADDING", (0, 0), (-1, -1), 10),
                ("RIGHTPADDING", (0, 0), (-1, -1), 10),
                ("LINEABOVE", (0, 0), (-1, 0), 1.5, NOTE_BORDER),
                ("LINEBELOW", (0, 0), (-1, -1), 1.5, NOTE_BORDER),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ]))
            story.append(overall_note_table)
            story.append(Spacer(1, 10))

        # ---- Footer ----
        story.append(HRFlowable(width="100%", thickness=0.8, color=MID_GRAY, spaceBefore=6, spaceAfter=6))
        story.append(Paragraph(
            f"Generated by LabsCo Field Evaluation Grading Tool  •  {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}",
            small_italic,
        ))

        doc.build(story)


if __name__ == "__main__":
    app = GradingApp()
    app.mainloop()