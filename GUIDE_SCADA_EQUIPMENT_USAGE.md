# Panduan: Penggunaan SCADA Equipment Propagation di Manufacturing Order

## Overview
Fitur ini memastikan bahwa informasi SCADA Equipment (Silo/Equipment) yang diatur di Bill of Materials (BoM) **otomatis tersalin ke Manufacturing Order (MO)**, sehingga pengguna tidak perlu mengisi ulang untuk setiap komponen.

## Langkah-Langkah Penggunaan

### Step 1: Setup BoM dengan SCADA Equipment

1. Buka **Manufacturing > Bill of Materials**
2. Buat atau edit BoM
3. Di section **Bill of Materials** (product lines), pada setiap line:
   - Isi **Product** (bahan baku)
   - Isi **Qty** (jumlah)
   - **NEW**: Isi **SCADA Equipment** dengan silo/equipment yang akan digunakan untuk material ini
4. Save BoM

**Contoh:**
```
BoM: Final Product A
─ Component 1 → SCADA Equipment: SILO_01
─ Component 2 → SCADA Equipment: SILO_02
─ Component 3 → SCADA Equipment: SILO_03
```

### Step 2: Create Manufacturing Order dari BoM

1. Buka **Manufacturing > Manufacturing Orders**
2. Click **Create** untuk membuat MO baru
3. Isi:
   - **Product**: Pilih product yang ada BoM-nya
   - **Bill of Materials**: Akan ter-auto-select BoM untuk product tersebut
   - **Quantity**: Jumlah yang akan diproduksi
4. Di section **Components** (raw materials):
   - **IMPORTANT**: SCADA Equipment akan **sudah terisi otomatis** dari BoM
   - Anda bisa melihat untuk setiap material, SCADA Equipment sudah ada

### Step 3: Confirm Manufacturing Order

1. Review data MO termasuk components dan SCADA Equipment-nya
2. Click tombol **Confirm** (atau action sesuai workflow)
3. Saat dikonfirmasi, sistem akan **kembali sync** SCADA Equipment dari BoM ke semua components
4. MO siap untuk produksi dengan equipment mapping yang lengkap

## Automatic Sync Points

SCADA Equipment dipropagasi secara otomatis pada **2 timing**:

1. **Saat MO Dibuat**: Ketika Anda membuat MO baru, components sudah langsung mendapat equipment dari BoM
2. **Saat MO Dikonfirmasi**: Sebelum moves di-generate, sistem memastikan semua equipment terisi dengan benar

## Contoh Workflow

```
┌─────────────────────────────────────────────────┐
│ 1. SETUP BoM dengan SCADA Equipment             │
│    Product A ← SILO_01                          │
│    Product B ← SILO_02                          │
│    Product C ← SILO_03                          │
└─────────────────┬───────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────┐
│ 2. CREATE Manufacturing Order dari BoM          │
│    [AUTO] Components + SCADA Equipment copied   │
│    Product A: SILO_01 ✓                         │
│    Product B: SILO_02 ✓                         │
│    Product C: SILO_03 ✓                         │
└─────────────────┬───────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────┐
│ 3. CONFIRM Manufacturing Order                  │
│    [AUTO SYNC] Verify all equipment present     │
│    Ready for production with equipment mapping  │
└─────────────────────────────────────────────────┘
```

## Benefit

| Sebelum | Setelah |
|---------|---------|
| ❌ Input manual SCADA Equipment di setiap MO component | ✅ Otomatis dari BoM |
| ❌ Risk: Lupa input atau input salah | ✅ Consistent & reliable |
| ❌ Time consuming untuk banyak components | ✅ Instant, no manual work |
| ❌ Error prone saat banyak MO | ✅ Reduce human error |

## FAQ

**Q: Apa if SCADA Equipment tidak terisi saat create MO?**
A: 
- Pastikan BoM sudah punya SCADA Equipment di setiap line
- Jika masih tidak ada setelah confirm, Anda bisa manual input di MO component section
- Sistem akan mendeteksi jika ada konflik (satu equipment untuk multiple materials)

**Q: Bisa gak override equipment di MO level?**
A: 
- Ya, Anda bisa tetap edit SCADA Equipment di MO component section
- Ini berguna jika operasional perlu menggunakan equipment berbeda dari BoM
- Original BoM tidak berubah

**Q: Apakah ini mempengaruhi existing MO?**
A: 
- Tidak, hanya MO baru atau yang sudah di-confirm setelah fix
- Existing MO tidak otomatis ter-update
- Anda bisa manually re-confirm untuk trigger sync jika perlu

**Q: Bagaimana jika BoM punya banyak variants?**
A: 
- Setiap variant BoM bisa punya mapping SCADA Equipment sendiri
- Saat create MO, sistem akan ambil dari variant BoM yang dipilih

## Troubleshooting

### Equipment masih kosong setelah Create MO
1. Cek BoM sudah punya SCADA Equipment di setiap line
2. Re-confirm MO atau reload page
3. Check error logs di manufacturing order timeline

### Error: "Equipment sudah dipakai oleh material lain"
- Ini adalah constraint yang mencegah 1 equipment untuk 2 material berbeda
- Fix: Pilih equipment berbeda untuk setiap material di BoM

### Equipment hilang setelah edit MO
- Equipment akan tetap ada, tidak hilang saat edit
- Jika perlu re-sync, confirm ulang MO

## Support

Untuk issues atau pertanyaan, silakan hubungi team development atau check module documentation.

---
Generated: 2024
Module: grt_scada v7.0.73
