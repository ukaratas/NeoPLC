# 02 — Master Mimarisi

## 1. MCU seçimi

### Karşılaştırma

| | **ESP32-S3 + W5500** | STM32G0/G4 + ESP32-C6 + W5500 | ESP32 + LAN8720 (RMII) | STM32H563 + PHY |
|---|---|---|---|---|
| WiFi | Dahili, modül sertifikalı | Ayrı modül, sertifikalı | Dahili | Yok — ek modül |
| Ethernet | SPI, donanım TCP/IP | SPI, donanım TCP/IP | RMII 50MHz + yazılım yığını | Dahili MAC + harici PHY |
| 2 katman uyumu | **İyi** | İyi | **Kötü** | Kötü |
| RT determinizmi | Orta → core pinning ile iyi | **Çok iyi** | Orta | Çok iyi |
| Firmware | **Tek image, tek toolchain** | İki image, iki toolchain | Tek | Tek |
| Lojik BOM (yaklaşık) | **~$7** | ~$10 | ~$6 | ~$14 |
| LCSC bulunabilirlik | **Çok yüksek** | Yüksek | Yüksek | Orta |
| Sertifikasyon riski | **Düşük** (hazır modül) | Düşük | Düşük | — |

### Karar: ESP32-S3-WROOM-1U-N16R8 · 🟡 D-01

**Gerekçe 1 — W5500 kısıt K3'ü çözüyor.** RMII, 50MHz saat + 4 sinyalin
kontrollü empedansla taşınmasını ister. 2 katman 1.6mm FR4'te bu pratik değil
(bkz. [08 §5](08-emc-koruma.md#5-katman-sayısı-kararı)). W5500 aynı işi SPI
üzerinden yapar ve TCP/IP yığınını donanımda taşır — Modbus TCP sunucusu 8
eşzamanlı sokete kadar neredeyse bedava gelir.

**Gerekçe 2 — çift çekirdek determinizm sorununu yönetilebilir kılıyor.**

```
Core 0 : WiFi yığını · lwIP · web UI · OTA        (best effort)
Core 1 : Backplane bus master · Modbus RTU        (deterministik, pinned)
```

Backplane taraması ağ trafiğinden izole edilir. Bu, ESP32'ye yöneltilen "RT için
uygun değil" itirazının pratikteki cevabıdır — ama tamamen ortadan kaldırmaz
(aşağıya bakınız).

**Gerekçe 3 — hazır modül sertifikasyon riskini alıyor.** WROOM modülü FCC/CE
ön sertifikalı. Kendi RF ön katımızı 2 katmanda tasarlamıyoruz.

**Gerekçe 4 — 16MB flash / 8MB PSRAM.** Web UI + OTA çift partisyon + **modül
firmware imajlarının master'da saklanması** için yeterli. Sonuncusu önemli:
[07](07-firmware-update.md)'deki merkezi güncelleme modelini mümkün kılıyor.

### Dürüst karşı argümanlar

| Risk | Değerlendirme |
|------|---------------|
| Lockstep / ECC RAM yok | NeoPLC SIL iddiası taşımıyor ([01 §6](01-sistem-genel-bakis.md#6-kapsam-dışı-şimdilik)). Kabul edilebilir. |
| WiFi yığını jitter üretir | Core pinning azaltır, sıfırlamaz. Tarama süresinde 40× marj var ([05 §4](05-dahili-bus.md#4-hız-ve-tarama-süresi)) — bu marj jitter için tampon. |
| Ağ + kontrol tek noktada | Master arızası tüm rafı düşürür. Redundancy kapsam dışı. |
| Endüstriyel sıcaklık | WROOM-1 SKU'sunun -40..+85°C derecelendirmesi sipariş öncesi doğrulanmalı. |

### Geçiş yolu (v2)

Gerçek hard-real-time veya SIL hedefi doğarsa: **STM32G0B1 + ESP32-C6-MINI.**

Backplane protokolü MCU'dan bağımsız tasarlandığı için **bu geçiş modülleri
etkilemez** — sahadaki modüller aynen çalışmaya devam eder. Platform
mimarisinin asıl kazancı burada görünüyor.

---

## 2. Ethernet

| | Değer |
|---|---|
| Kontrolcü | W5500 (SPI, donanım TCP/IP, 8 soket) |
| Hız | 10/100 Mbps |
| Manyetik | Entegre manyetikli RJ45 magjack |
| Sonlandırma | Bob Smith |
| **Yerleşim kısıtı** | **W5500 ↔ magjack diferansiyel izleri ≤ 25 mm** |

Yerleşim kısıtının gerekçesi ve hesabı: [08 §5](08-emc-koruma.md#5-katman-sayısı-kararı).

Bu kısıt PCB yerleşim aşamasında **bağlayıcıdır** ve DRC ile yakalanamaz —
yerleşim incelemesinde elle kontrol edilmeli.

---

## 3. WiFi

| | Değer |
|---|---|
| Radyo | ESP32-S3 dahili (802.11 b/g/n + BLE 5) |
| Anten | **U.FL konnektör + harici anten** (`-1U` modül varyantı) |

**PCB anten neden elenmiş:** NeoPLC metal veya metalize endüstriyel kutu içinde
DIN rayına monte edilecek. PCB anten bu ortamda çalışmaz. Modül varyantı seçimi
(`-1` PCB anten vs `-1U` U.FL) geri dönülemez bir kart kararıdır — baştan doğru
seçilmeli.

Kullanım: konfigürasyon web UI'ı, OTA, ikincil Modbus TCP erişimi.

---

## 4. RS-485 saha portu

| | Değer |
|---|---|
| Topoloji | 2 tel yarım dupleks |
| İzolasyon | **İzole** — transceiver + izole DC-DC · 🟡 D-07 |
| Klemens | A / B / GND |
| Sonlandırma | DIP ile seçilebilir 120Ω |
| Bias | Fail-safe bias direnç çifti |
| Protokol | Modbus RTU, master/slave yazılımdan seçilir |

**İzolasyon gerekçesi:** Ek maliyet ~$2–4. Buna karşılık izolasyonsuz RS-485,
saha ground loop'larında endüstriyel kurulumların en yaygın arıza kaynağıdır.
Endüstriyel güvenilirlik iddiasının en görünür sınandığı nokta burası.

Maliyet baskısı olursa çıkarılabilir bir kalem — ama bilinçli olarak
çıkarılmalı, unutularak değil.

> ⚠️ Bu port, dahili backplane bus'ı ile **karıştırılmamalıdır**. İkisi de
> RS-485 fiziksel katmanı kullanır ama tamamen ayrı hatlardır, ayrı
> protokollerdir ve backplane tarafı izole değildir.

---

## 5. GPIO bütçesi

ESP32-S3-WROOM-1U-N16R8: octal PSRAM GPIO 33–37'yi tüketir, kullanılabilir
≈ 30 GPIO.

| Fonksiyon | Pin |
|-----------|-----|
| W5500 SPI (SCK, MOSI, MISO, CS, INT, RST) | 6 |
| RS-485 saha portu (TX, RX, DE) | 3 |
| Backplane bus (TX, RX, DE) | 3 |
| I²C slot expander (SDA, SCL) + INT# | 3 |
| FAULT# wired-OR girişi | 1 |
| SYNC çıkışı | 1 |
| Durum LED'leri | 4 |
| Buton / config DIP | 2 |
| **Ara toplam** | **23** |
| **Yedek** | **~7** |

Bütçenin rahat olmasının tek sebebi, **slot başına ayrık hatların MCU'ya
çekilmemesidir.** Naif tasarım 32 GPIO isterdi; [06 §3](06-slot-yonetimi.md#3-master-tarafı-io-genişletme)'teki
üç katmanlı çözüm bunu 4 pine indiriyor.

UART tahsisi: UART0 = konsol/debug (native USB üzerinden), UART1 = RS-485 saha,
UART2 = backplane bus.

---

## 6. Modbus register haritası

Dış SCADA'nın düz ve öngörülebilir bir adres uzayı görmesi entegratör deneyimi
için kritik. · 🟡 D-27

```
0x0000 – 0x00FF    Sistem
                     0x0000  Firmware versiyonu
                     0x0002  Slot doluluk haritası (bit N = slot N dolu)
                     0x0003  Slot hata haritası
                     0x0004  Sistem durum bayrakları
                     0x0010  Tarama süresi (µs)
                     0x0012  Hata sayaçları (CRC, timeout)
                     0x0020  Güç bütçesi: tahsis / kullanım

0x1000 + N×0x100   Slot N proses imajı   (N = 0..7)
     +0x00 .. 0x3F   Girişler                      (read)
     +0x40 .. 0x7F   Çıkışlar                      (read/write)
     +0x80 .. 0xBF   Durum / diagnostik            (read)
     +0xC0 .. 0xFF   Modül descriptor              (read)
```

Slot başına sabit 0x100'lük blok, modül tipi ne olursa olsun adres hesabını
sabit tutuyor: `slot_taban = 0x1000 + slot_no × 0x100`. Entegratör tek formülle
çalışıyor.

---

## 7. Master blok diyagramı

```
   12–48V DC
       │
  ┌────▼─────────────────────────┐
  │ Giriş koruma (bkz. 03 §1)    │
  │ sigorta·CM choke·TVS·FET     │
  └────┬────────────────┬────────┘
       │ VBUS_RAW       │
       │           ┌────▼──────┐
       │           │ Buck      │ 5V @ 3A
       │           │ 12-48→5V  │
       │           └────┬──────┘
       │                │ +5V_SYS
       │                ├──────────────┐
       │                │         ┌────▼─────┐
       │                │         │ 5V→3.3V  │
       │                │         └────┬─────┘
       │                │              │ +3V3
       │                │    ┌─────────┴────────────────┐
       │                │    │                          │
       │                │  ┌─▼──────────┐      ┌────────▼───────┐
       │                │  │ ESP32-S3   │ SPI  │ W5500          │──RJ45
       │                │  │ WROOM-1U   ├──────┤ magjack ≤25mm  │
       │                │  └─┬───┬───┬──┘      └────────────────┘
       │                │    │   │   │
       │                │    │   │   └─UART1─→ İzole RS-485 ──→ A/B klemens
       │                │    │   │
       │                │    │   └─I²C──→ PCA9555 ──→ 8× PRESENT#
       │                │    │                   └──→ 8× MOD_RST#
       │                │    │
       │                │    └─UART2─→ RS-485 xcvr ─┐
       │                │                            │
  ┌────▼────────────────▼────────────────────────────▼─────┐
  │  BACKPLANE   VBUS_RAW · +5V_SYS · BUS_A/B · ADDR0-3    │
  │              FAULT# · SYNC · BOOT# · PRESENT# · RST#   │
  └──┬──────┬──────┬──────┬──────┬──────┬──────┬──────┬────┘
   slot0  slot1  slot2  slot3  slot4  slot5  slot6  slot7
     ↑ her slotta akım sınırlı load switch (+5V_SYS)
```
