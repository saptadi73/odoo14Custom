# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

{

    "name": "Basic Hospital Management System in Odoo",
    "version": "14.0.0.2",
    "currency": 'EUR',
    "summary": "Apps basic Hospital Management system Healthcare Management Clinic Management apps manage clinic manage Patient hospital manage Healthcare system Patient Management Hospital Management Healthcare Management Clinic Management hospital Lab Test Request",
    "category": "Industries",
    "description": """
    BrowseInfo developed a new odoo/OpenERP module apps
    This module is used to manage Hospital and Healthcare Management and Clinic Management apps. 
    manage clinic manage Patient hospital in odoo manage Healthcare system Patient Management, 
    Odoo Hospital Management odoo Healthcare Management Odoo Clinic Management
    Odoo hospital Patients
    Odoo Healthcare Patients Card Report
    Odoo Healthcare Patients Medication History Report
    Odoo Healthcare Appointments
    Odoo hospital Appointments Invoice
    Odoo Healthcare Families Prescriptions Healthcare Prescriptions
    Odoo Healthcare Create Invoice from Prescriptions odoo hospital Prescription Report
    Odoo Healthcare Patient Hospitalization
    odoo Hospital Management System
    Odoo Healthcare Management System
    Odoo Clinic Management System
    Odoo Appointment Management System
    health care management system
    Generate Report for patient details, appointment, prescriptions, lab-test

    Odoo Lab Test Request and Result
    Odoo Patient Hospitalization details
    Generate Patient's Prescriptions

    
""",

    "depends": ["mail", "sale_management", "stock", 'peternak_sapi', 'master_sapi',],
    "data": [
        'security/hospital_groups.xml',
        'security/ir.model.access.csv',
        'data/ir_sequence_data.xml',
        'views/assets.xml',
        'views/login_page.xml',
        'views/main_menu_file.xml',
        'wizard/medical_appointments_invoice_wizard.xml',
        'wizard/create_prescription_invoice_wizard.xml',
        'wizard/create_prescription_shipment_wizard.xml',
        'wizard/medical_inpatient_inovice_wizard.xml',
        'views/medical_medicament.xml',
        'views/medical_drug_route.xml',
        # 'wizard/medical_lab_test_create_wizard.xml',
        # 'wizard/medical_lab_test_invoice_wizard.xml',
        'wizard/medical_appointment_prescription_wizard.xml',
        'views/medical_prescription_order.xml',
        'views/medical_directions.xml',
        'views/medical_dose_unit.xml',
        'views/medical_patient_evaluation.xml',
        'views/medical_family_disease.xml',
        'views/medical_inpatient_registration.xml',
        'views/medical_inpatient_medication.xml',
        'views/medical_insurance_plan.xml',
        'views/medical_appointment.xml',
        'views/medical_insurance.xml',
        # 'views/medical_patient_lab_test.xml',
        # 'views/medical_lab_test_units.xml',
        # 'views/medical_lab.xml',
        'views/medical_neomatal_apgar.xml',
        'views/medical_pathology_category.xml',
        'views/medical_pathology_group.xml',
        'views/medical_pathology.xml',
        'views/medical_patient_disease.xml',
        'views/medical_patient_medication.xml',
        'views/medical_patient_medication1.xml',
        'views/medical_patient_pregnancy.xml',
        'views/medical_patient_prental_evolution.xml',
        'views/medical_patient.xml',
        'views/medical_physician.xml',
        'views/medical_preinatal.xml',
        'views/medical_prescription_line.xml',
        'views/medical_puerperium_monitor.xml',
        'views/medical_rcri.xml',
        'views/medical_rounding_procedure.xml',
        'views/medical_test_critearea.xml',
        'views/medical_test_type.xml',
        'views/medical_vaccination.xml',
        'views/res_partner.xml',
        'views/medical_room.xml',
        'views/medical_fasilitas.xml',
        'views/deceased_views.xml',
        # 'views/oprasi_views.xml',
        # 'views/discharge_hospitalized.xml',
        # 'views/pulang_paksa.xml',
        # 'views/pulang_sendiri.xml',
        'views/jenis_pelayanan.xml',
        'views/master_jenis_mutasi_views.xml',
        'views/master_jabatan_petugas_views.xml',
        'views/master_tanda_kebuntingan_views.xml',
        'views/master_posisi_views.xml',
        'views/report_layanan_views.xml',
        'views/master_status_kesehatan_views.xml',
        'views/master_status_reproduksi_views.xml',
        'views/master_metoda_views.xml',
        'views/master_abortus_views.xml',
        'views/master_specimen_views.xml',
        'views/master_specimen_tes_views.xml',
        'views/master_pengeringan_views.xml',
        'views/master_kategori_obat_views.xml',
        'views/master_obat_views.xml',
        'views/master_metoda_pengobatan_views.xml',
        'views/master_alasan_potkuku_views.xml',
        'views/master_alasan_palpasi_views.xml',
        'views/master_temuan_uterus_views.xml',
        'views/master_temuan_ovarium_views.xml',
        'views/master_temuan_cervix_views.xml',
        'views/master_tipe_sapi_views.xml',
        'views/master_status_laktasi_views.xml',
        'views/master_metode_perhitungan_jss_views.xml',
        'views/master_kategori_penyakit_views.xml',
        'views/master_kasus_penyakit_views.xml',
        'views/master_kode_kelahiran_views.xml',
        'views/master_keadaan_melahirkan_views.xml',
        'views/master_kuman_sampel_kuartir_views.xml',
        'views/master_kategori_breed_views.xml',
        'views/master_breed_views.xml',
        'views/master_metoda_pengobatan_views.xml',
        'views/master_pejantan_views.xml',
        'views/master_semen_beku_views.xml',
        'views/form_abortus_views.xml',
        'views/form_pkb_views.xml',
        # 'views/form_bsk_views.xml',
        # 'views/form_dm_views.xml',
        'views/form_mutasi_views.xml',
        'views/form_et_views.xml',
        'views/form_gis_views.xml',
        # 'views/form_hormon_views.xml',
        'views/form_vaksinasi_views.xml',
        'views/form_ib_views.xml',
        # 'views/form_pedet_views.xml',
        'views/form_kk_views.xml',
        'views/form_masuk_views.xml',
        'views/form_melahirkan_views.xml',
        'views/form_nkt_views.xml',
        'views/form_pr_views.xml',
        'views/form_pt_views.xml',
        'views/form_sq_views.xml',
        'views/form_specimen_views.xml',
        'views/form_peng_bb_tb_views.xml',
        'views/form_pengobatan_views.xml',
        'views/form_ganti_pmlk_views.xml',
        'views/form_vaksinasi_views.xml',
        # 'views/form_susu_views.xml',
        'views/medical_physician.xml',
        'views/master_vaksin_views.xml',
        'views/form_pot_kuku_views.xml',
        'views/form_ident_views.xml',
        'views/inherit_modul_views.xml',
        'report/report_view.xml',
        'report/appointment_recipts_report_template.xml',
        # 'report/medical_view_report_document_lab.xml',
        # 'report/medical_view_report_lab_result_demo_report.xml',
        'report/newborn_card_report.xml',
        'report/patient_card_report.xml',
        'report/patient_diseases_document_report.xml',
        'report/patient_medications_document_report.xml',
        'report/patient_vaccinations_document_report.xml',
        'report/prescription_demo_report.xml',
    ],
    "author": "BrowseInfo",
    "website": "https://www.browseinfo.in",
    "installable": True,
    "application": True,
    "auto_install": False,
    "images": ["static/description/Banner.png"],
    "live_test_url": 'https://youtu.be/fk9dY53I9ow',

}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
