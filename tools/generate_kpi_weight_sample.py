from pathlib import Path

import xlsxwriter


OUTPUT_PATH = Path("odoo_kpi") / "kpi_weight_sample.xlsx"


def main() -> None:
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

    workbook = xlsxwriter.Workbook(str(OUTPUT_PATH))
    workbook.set_properties(
        {
            "title": "KPI Weight Sample",
            "subject": "Contoh perhitungan bobot KPI employee",
            "author": "Codex",
            "comments": "Generated from odoo_kpi formula",
        }
    )
    title_fmt = workbook.add_format(
        {
            "bold": True,
            "font_size": 14,
            "bg_color": "#D9EAF7",
            "border": 1,
            "align": "center",
            "valign": "vcenter",
        }
    )
    header_fmt = workbook.add_format(
        {
            "bold": True,
            "bg_color": "#B7DEE8",
            "border": 1,
            "align": "center",
            "valign": "vcenter",
        }
    )
    text_fmt = workbook.add_format({"border": 1, "valign": "top"})
    center_fmt = workbook.add_format({"border": 1, "align": "center", "valign": "vcenter"})
    num_fmt = workbook.add_format({"border": 1, "num_format": "0.00"})
    pct_fmt = workbook.add_format({"border": 1, "num_format": "0.00%"})
    note_fmt = workbook.add_format(
        {
            "text_wrap": True,
            "valign": "top",
            "border": 1,
        }
    )
    total_label_fmt = workbook.add_format(
        {
            "bold": True,
            "bg_color": "#E2F0D9",
            "border": 1,
        }
    )
    total_num_fmt = workbook.add_format(
        {
            "bold": True,
            "bg_color": "#E2F0D9",
            "border": 1,
            "num_format": "0.00",
        }
    )
    section_fmt = workbook.add_format(
        {
            "bold": True,
            "font_size": 12,
            "bg_color": "#FCE4D6",
            "border": 1,
        }
    )
    info_fmt = workbook.add_format(
        {
            "text_wrap": True,
            "border": 1,
            "valign": "top",
            "bg_color": "#FFF2CC",
        }
    )
    input_fmt = workbook.add_format(
        {
            "border": 1,
            "bg_color": "#FFF2CC",
            "num_format": "0.00",
        }
    )
    grade_fmt = workbook.add_format(
        {
            "bold": True,
            "font_size": 12,
            "align": "center",
            "valign": "vcenter",
            "border": 1,
            "bg_color": "#E2F0D9",
        }
    )
    subtitle_fmt = workbook.add_format(
        {
            "italic": True,
            "font_color": "#555555",
        }
    )

    sheet = workbook.add_worksheet("Sample KPI")
    sheet.set_column("A:A", 8)
    sheet.set_column("B:B", 24)
    sheet.set_column("C:F", 14)
    sheet.set_column("G:H", 18)
    sheet.set_column("I:I", 16)
    sheet.set_column("J:J", 42)

    sheet.freeze_panes(3, 0)
    sheet.merge_range("A1:J1", "Sample Perhitungan Bobot KPI Employee", title_fmt)
    sheet.merge_range(
        "A2:J2",
        "Formula modul odoo_kpi: Total Score = SUM((Actual / Target) x Weight) untuk semua assignment employee dalam 1 periode.",
        info_fmt,
    )
    sheet.write_row(
        "A3",
        [
            "No",
            "KPI",
            "Target",
            "Actual",
            "Weight",
            "Achievement",
            "Nilai Assignment",
            "Kontribusi ke Total",
            "Status",
            "Catatan",
        ],
        header_fmt,
    )

    rows = [
        (
            1,
            "Sales",
            100,
            80,
            50,
            "=(D4/C4)",
            "=(D4/C4)*E4",
            "=G4/$G$8",
            '=IF(D4>C4,"Over target",IF(D4=C4,"On target","Below target"))',
            "Rumus Odoo: (actual / target) x weight",
        ),
        (
            2,
            "Visit",
            20,
            15,
            30,
            "=(D5/C5)",
            "=(D5/C5)*E5",
            "=G5/$G$8",
            '=IF(D5>C5,"Over target",IF(D5=C5,"On target","Below target"))',
            "Kontribusi dihitung dari nilai assignment dibagi total score employee",
        ),
        (
            3,
            "Collection",
            10,
            12,
            20,
            "=(D6/C6)",
            "=(D6/C6)*E6",
            "=G6/$G$8",
            '=IF(D6>C6,"Over target",IF(D6=C6,"On target","Below target"))',
            "Tidak ada cap di kode, jadi over target bisa melampaui bobot",
        ),
    ]

    start_row = 3
    for row_idx, row in enumerate(rows, start=start_row):
        sheet.write_number(row_idx, 0, row[0], center_fmt)
        sheet.write_string(row_idx, 1, row[1], text_fmt)
        sheet.write_number(row_idx, 2, row[2], num_fmt)
        sheet.write_number(row_idx, 3, row[3], num_fmt)
        sheet.write_number(row_idx, 4, row[4], num_fmt)
        sheet.write_formula(row_idx, 5, row[5], pct_fmt)
        sheet.write_formula(row_idx, 6, row[6], num_fmt)
        sheet.write_formula(row_idx, 7, row[7], pct_fmt)
        sheet.write_formula(row_idx, 8, row[8], center_fmt)
        sheet.write_string(row_idx, 9, row[9], note_fmt)

    sheet.write("F8", "Total Score", total_label_fmt)
    sheet.write_formula("G8", "=SUM(G4:G6)", total_num_fmt)
    sheet.write("F9", "Total Weight", total_label_fmt)
    sheet.write_formula("G9", "=SUM(E4:E6)", total_num_fmt)
    sheet.write("F10", "Grade", total_label_fmt)
    sheet.write_formula(
        "G10",
        '=IF(G8>=90,"A",IF(G8>=75,"B",IF(G8>=60,"C",IF(G8>=40,"D","E"))))',
        grade_fmt,
    )
    sheet.write("H8", "Interpretasi", total_label_fmt)
    sheet.write_formula(
        "I8",
        '=IF(G8>=90,"Sangat baik",IF(G8>=75,"Baik",IF(G8>=60,"Cukup",IF(G8>=40,"Kurang","Buruk"))))',
        total_label_fmt,
    )
    sheet.write("H9", "Catatan", total_label_fmt)
    sheet.merge_range(
        "I9:J10",
        "Jika total weight = 100 maka total score terasa seperti skala 0-100. Jika actual > target, nilai assignment bisa melebihi bobot karena rumus belum di-cap.",
        note_fmt,
    )

    sheet.write("A12", "Cara pakai:", header_fmt)
    instructions = [
        "Ubah kolom Target, Actual, atau Weight untuk simulasi KPI lain.",
        "Achievement = Actual / Target.",
        "Nilai Assignment = Achievement x Weight.",
        "Kontribusi ke Total = Nilai Assignment / Total Score.",
        "Jika total weight = 100, total score akan terasa seperti nilai skala 0-100.",
        "Jika actual melebihi target, nilai assignment bisa melebihi bobot karena kode saat ini tidak membatasi hasil.",
    ]
    for idx, instruction in enumerate(instructions, start=12):
        sheet.write(f"A{idx}", f"{idx - 11}.", text_fmt)
        sheet.merge_range(f"B{idx}:J{idx}", instruction, note_fmt)

    summary_sheet = workbook.add_worksheet("Executive Summary")
    summary_sheet.set_column("A:A", 24)
    summary_sheet.set_column("B:B", 18)
    summary_sheet.set_column("C:C", 40)
    summary_sheet.freeze_panes(4, 0)

    summary_sheet.merge_range("A1:C1", "Ringkasan Untuk HR / Manager", title_fmt)
    summary_sheet.write("A3", "Area", header_fmt)
    summary_sheet.write("B3", "Nilai", header_fmt)
    summary_sheet.write("C3", "Keterangan", header_fmt)
    summary_sheet.write("A4", "Total Score Employee", text_fmt)
    summary_sheet.write_formula("B4", "='Sample KPI'!G8", total_num_fmt)
    summary_sheet.write("C4", "Total nilai akhir employee untuk periode tersebut.", note_fmt)
    summary_sheet.write("A5", "Grade", text_fmt)
    summary_sheet.write_formula("B5", "='Sample KPI'!G10", grade_fmt)
    summary_sheet.write("C5", "Grade mengikuti mapping A/B/C/D/E dari modul.", note_fmt)
    summary_sheet.write("A6", "Total Weight", text_fmt)
    summary_sheet.write_formula("B6", "='Sample KPI'!G9", total_num_fmt)
    summary_sheet.write("C6", "Idealnya 100 jika ingin score langsung terbaca sebagai persentase performa.", note_fmt)
    summary_sheet.write("A8", "KPI Dominan", header_fmt)
    summary_sheet.write("B8", "Kontribusi", header_fmt)
    summary_sheet.write("C8", "Makna", header_fmt)
    summary_sheet.write_formula("A9", '=INDEX(\'Sample KPI\'!B4:B6, MATCH(MAX(\'Sample KPI\'!H4:H6), \'Sample KPI\'!H4:H6, 0))', text_fmt)
    summary_sheet.write_formula("B9", '=MAX(\'Sample KPI\'!H4:H6)', pct_fmt)
    summary_sheet.write("C9", "Assignment dengan sumbangan terbesar ke total nilai akhir.", note_fmt)
    summary_sheet.merge_range(
        "A11:C14",
        "Baca report ini seperti berikut: bobot menunjukkan porsi maksimum kontribusi KPI, tetapi nilai akhir tetap tergantung pencapaian actual terhadap target. KPI dengan bobot besar tetapi actual rendah tetap memberi kontribusi kecil.",
        info_fmt,
    )

    override_sheet = workbook.add_worksheet("Override Example")
    override_sheet.set_column("A:A", 24)
    override_sheet.set_column("B:C", 16)
    override_sheet.set_column("D:D", 38)
    override_sheet.freeze_panes(3, 0)

    override_sheet.merge_range("A1:D1", "Contoh Target Override dan Weight Override", title_fmt)
    override_sheet.write("A2", "Override dipakai lebih dulu daripada default target/weight KPI.", subtitle_fmt)
    override_sheet.write_row("A3", ["Parameter", "Nilai", "Dipakai?", "Catatan"], header_fmt)
    override_rows = [
        ("Default Target KPI", 100, "Tidak", "Akan kalah prioritas jika target_override diisi"),
        ("Default Weight KPI", 40, "Tidak", "Akan kalah prioritas jika weight_override diisi"),
        ("Target Override", 80, "Ya", "Dipakai sebagai effective_target"),
        ("Weight Override", 50, "Ya", "Dipakai sebagai effective_weight"),
        ("Actual", 60, "Ya", "Total dari semua kpi.value untuk assignment ini"),
    ]
    for idx, row in enumerate(override_rows, start=3):
        override_sheet.write_string(idx, 0, row[0], text_fmt)
        override_sheet.write_number(idx, 1, row[1], num_fmt)
        override_sheet.write_string(idx, 2, row[2], text_fmt)
        override_sheet.write_string(idx, 3, row[3], note_fmt)

    override_sheet.write("A10", "Rumus", total_label_fmt)
    override_sheet.write_formula("B10", "=(B7/B5)*B6", total_num_fmt)
    override_sheet.write("C10", "Hasil", total_label_fmt)
    override_sheet.write("D10", "Nilai assignment = (60 / 80) x 50 = 37.5", note_fmt)

    sim_sheet = workbook.add_worksheet("Simulator")
    sim_sheet.set_column("A:A", 8)
    sim_sheet.set_column("B:B", 24)
    sim_sheet.set_column("C:F", 14)
    sim_sheet.set_column("G:H", 18)
    sim_sheet.set_column("I:J", 24)
    sim_sheet.freeze_panes(5, 0)

    sim_sheet.merge_range("A1:J1", "Simulator KPI Employee", title_fmt)
    sim_sheet.merge_range(
        "A2:J2",
        "Kolom kuning bisa diubah. Rumus akan otomatis menghitung nilai assignment, kontribusi, total score, dan grade.",
        info_fmt,
    )
    sim_sheet.write("A4", "Employee Name", header_fmt)
    sim_sheet.merge_range("B4:D4", "Nama Employee", info_fmt)
    sim_sheet.write("E4", "Periode", header_fmt)
    sim_sheet.merge_range("F4:G4", "2026-03", info_fmt)
    sim_sheet.write_row(
        "A5",
        [
            "No",
            "KPI",
            "Target",
            "Actual",
            "Weight",
            "Achievement",
            "Nilai Assignment",
            "Kontribusi",
            "Catatan",
            "Status",
        ],
        header_fmt,
    )

    sim_rows = range(6, 14)
    for excel_row, seq in zip(sim_rows, range(1, 9)):
        sim_sheet.write_number(excel_row - 1, 0, seq, center_fmt)
        sim_sheet.write_blank(excel_row - 1, 1, "", text_fmt)
        sim_sheet.write_blank(excel_row - 1, 2, "", input_fmt)
        sim_sheet.write_blank(excel_row - 1, 3, "", input_fmt)
        sim_sheet.write_blank(excel_row - 1, 4, "", input_fmt)
        sim_sheet.write_formula(
            excel_row - 1,
            5,
            f'=IFERROR(D{excel_row}/C{excel_row},0)',
            pct_fmt,
        )
        sim_sheet.write_formula(
            excel_row - 1,
            6,
            f'=IF(OR(C{excel_row}<=0,E{excel_row}<=0),0,(D{excel_row}/C{excel_row})*E{excel_row})',
            num_fmt,
        )
        sim_sheet.write_formula(
            excel_row - 1,
            7,
            f'=IFERROR(G{excel_row}/$G$16,0)',
            pct_fmt,
        )
        sim_sheet.write_blank(excel_row - 1, 8, "", note_fmt)
        sim_sheet.write_formula(
            excel_row - 1,
            9,
            f'=IF(G{excel_row}=0,"No score",IF(D{excel_row}>C{excel_row},"Over target",IF(D{excel_row}=C{excel_row},"On target","Below target")))',
            center_fmt,
        )

    sim_sheet.write("F16", "Total Score", total_label_fmt)
    sim_sheet.write_formula("G16", "=SUM(G6:G13)", total_num_fmt)
    sim_sheet.write("F17", "Total Weight", total_label_fmt)
    sim_sheet.write_formula("G17", "=SUM(E6:E13)", total_num_fmt)
    sim_sheet.write("F18", "Grade", total_label_fmt)
    sim_sheet.write_formula(
        "G18",
        '=IF(G16>=90,"A",IF(G16>=75,"B",IF(G16>=60,"C",IF(G16>=40,"D","E"))))',
        grade_fmt,
    )
    sim_sheet.write("H16", "Interpretasi", total_label_fmt)
    sim_sheet.write_formula(
        "I16",
        '=IF(G16>=90,"Sangat baik",IF(G16>=75,"Baik",IF(G16>=60,"Cukup",IF(G16>=40,"Kurang","Buruk"))))',
        total_label_fmt,
    )
    sim_sheet.merge_range(
        "H17:J18",
        "Tips: set total bobot ke 100. Jika total bobot tidak 100, score akhir tetap valid menurut kode, tetapi lebih sulit dibaca sebagai skala 0-100.",
        note_fmt,
    )

    workbook.close()


if __name__ == "__main__":
    main()
