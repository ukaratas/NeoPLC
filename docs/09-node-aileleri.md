# 09 — Node tipleri

Dil **node tipi**, "aile" değil. Katalog **D-72** ile kilitli. İlk PCB: **DI-8**
(D-28).

---

## 1. Ortak node çekirdeği

Platformun en önemli tasarım kalemi. Her node, **aynı değişmez çekirdeği**
paylaşır; sadece saha tarafı farklıdır.

```
┌─────────────────────────────────────────────────────────────┐
│  NODE                                                       │
│                                                             │
│  ┌── ORTAK ÇEKİRDEK (tüm node'larda aynı) ──────────────┐   │
│  │                                                       │   │
│  │  Kart kenarı konnektörü (12 pin)                     │   │
│  │  +5V → 3.3V regülatör                                │   │
│  │  RS-485 transceiver                                  │   │
│  │  MCU + protokol firmware'i                           │   │
│  │  MOD_RST# pull-down                                  │   │
│  │  Soft-start · lokal tampon kapasitör                 │   │
│  │  SWD test noktaları                                  │   │
│  │  (opsiyonel) lokal boost — bobin / compliance için   │   │
│  └───────────────────────────────────────────────────────┘   │
│                            ↕                                 │
│  ┌── SAHA TARAFI (node tipine özgü) ────────────────────┐   │
│  │  İzolasyon · sürücüler · filtreleme · klemensler      │   │
│  └───────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

### 1.1 Neden bu ayrım kritik

| Kazanç | Açıklama |
|--------|----------|
| **Yeni node türetme maliyeti düşer** | Sadece saha tarafı tasarlanır; çekirdek kopyalanır |
| **Doğrulama bir kez yapılır** | Çekirdek bir node'da doğrulandıysa hepsinde doğrulanmıştır |
| **Firmware paylaşılır** | Protokol katmanı ortak kütüphane; node sadece I/O katmanını yazar |
| **KiCAD'de yeniden kullanım** | Hiyerarşik sayfa veya design block olarak saklanabilir |

**Tasarım kuralı:** Çekirdekte yapılan her değişiklik tüm node ailesini
etkiler. Çekirdek, ilk node'la birlikte donduruluyor.

### 1.2 Çekirdeğin BOM tahmini

| Bileşen | Tahmini |
|---------|---------|
| MCU (düşük sınıf, 32-bit) | ~$0.60 |
| RS-485 transceiver | ~$0.20 |
| 3.3V regülatör (5V→3.3V) | ~$0.15 |
| Pasifler, LED, soft-start | ~$0.30 |
| **Çekirdek toplamı** | **~$1.25** |

Kart kenarı konnektörü **$0** ([04 §4](04-backplane-mekanik.md#4-konnektör-seçimi)) —
bu, çekirdek maliyetinin neden bu kadar düşük kalabildiğinin ana sebebi.

---

## 2. İlk node seçimi

### D-28 — Kabul edildi · 🟢

**İlk node: DI-8** — dijital giriş, 8 kanal, 1U. Saha: **~5–30 V, opto izole**
(D-76) — 12 V karavan anahtarı ve 24 V pano aynı direnç/opto.

Gerekçe:

| Kriter | Dijital giriş |
|--------|---------------|
| Karmaşıklık | **En düşük** — optocoupler + seri direnç, başka bir şey yok |
| Saha koruması | Doğal olarak sağlam ([08 §1.1](08-emc-koruma.md#11-dijital-girişin-doğal-sağlamlığı)) |
| Çekirdek doğrulaması | **Tam** — backplane, protokol, discovery, güç, reset, fault mantığının hepsini kullanır |
| Güç tüketimi | En düşük — güç bütçesi varsayımlarını doğrulamak için iyi başlangıç |
| Hata riski | Saha tarafında yanlış gidecek çok az şey var |

**Amaç ilk node'da I/O fonksiyonunu göstermek değil, platform sözleşmesini
doğrulamaktır.** Bunun için en basit node en iyisidir — saha tarafındaki
karmaşıklık, çekirdekteki sorunları maskeler.

### 2.1 Alternatif değerlendirmesi

| Aday | Neden ilk olarak uygun değil |
|------|------------------------------|
| Dijital çıkış | Yük sürme, freewheel, kısa devre koruması — çekirdek hatalarını maskeleyebilir |
| Röle çıkış | Bobin darbe akımı güç bütçesi testini bulandırır |
| Analog giriş | Referans, kalibrasyon, gürültü — en zor node. Çekirdek olgunlaşmadan yapılmamalı |

---

## 3. Node MCU'su

### D-37 — Kabul edildi · 🟢

**Tek SKU, tüm node tipleri: STM32G071 128 KB sınıfı** (aday: G071CB, LQFP48
veya eşdeğeri — LCSC stok doğrulanınca bağlayıcı).

| Gerekçe | |
|---------|---|
| STOP + USART start-bit wake | Enerji bütçesi D-41 |
| Donanımsal DE | Yarım dupleks D-11 |
| 128 KB | Tek app bootloader rahat; COM/AI da sığar. Çift bank D-25 yeniden açılabilir |
| Tek toolchain | DI'dan COM'a aynı firmware omurgası |

COM-1U Ethernet yığını sıkışırsa bu SKU büyütülür (G0B1); çekirdek pinout
aynı pakette tutulur.

---

## 4. Saha bağlantısı

### D-38 — Kabul edildi · 🟢

**Çıkarılabilir yaylı (pluggable) klemens.** Vidalı yok (K5). Adım **tek değil**
— her SKU kendi kablo sınıfına göre.

Karavanda DC'de **4 mm² ve 6 mm²** bol. 3.5 mm fiş bunları almaz. Sinyal
modülü 3.5 mm kalır; güç modülü geniş adım alır.

1U ön yüz **17.5 mm** = bir sıradaki kutup × adım:

| Sınıf | SKU | Kablo (tipik) | Adım | 1U kutup/sıra | 2U kutup/sıra |
|-------|-----|---------------|------|---------------|---------------|
| Sinyal | DI, AI, AO, COM | 0.5–1.5 mm² | **3.5 mm** | 5 | — |
| 8 A | DO-M-8A-8 | **1.5–2.5 mm²** | **3.5 mm** | 5 | — |
| 16 A | DC-L-16A-4 | 2.5–4 mm² | **5.08–6.35 mm** | 3 | 6 |
| 32 A | DC-H-32A-2 | **6 mm²** | **7.5 mm** | 2 | 4 |
| 64 A | DC-H-64A-2 | 6–16 mm² | **10–12 mm** | 1 | 2–3 |
| AC 16 A | AC-L-16A-4 | 2.5–4 mm² | **7.5 mm** | — | ~4 |
| AC 32 A | AC-L-32A-2 | 6 mm² | **10 mm** | — | 2–3 |

Pluggable kazancı: node çekilince saha kablosu **fişte** kalır. Tel fişin
içinde (yüksük / krimp); dışarıda çıplak iletken yok. AC fiş **parmak-güvenli
(IP20)** — mated ve unmated.

D-38 = kablo/fiş. D-64 = PCB 230 V adası (klipsli bariyer, tam kutu değil).

**DO-M-8A-8: 2.5 mm² / 3.5 mm** (D-38). 8 A için 2.5 mm² yeterli; 4 mm² yalnız
16 A+ güç node'larında. 8 OUT + 2 BAT+ = iki sıra × 5 kutup.

```
3.5 mm × 5 = 17.5 mm     sinyal + 8 A DO
5.08 mm × 3 = 15.2 mm    16 A / 4 mm²
7.5 mm × 2 = 15.0 mm     32 A / 6 mm²
10 mm × 1 = 10 mm        64 A, 1U'da tek kutup
```

---

## 5. Node katalogu · D-72

Form **en fazla 2U** (D-75). 4U yok. **Yükseklik sığmazsa 2U** (D-61), kanal
aynı; 4U gerekecek kadar şişerse kanal düşer veya ikinci 2U.
Her node **tek teknoloji** (D-52).

| SKU | U | Kanal | Saha | Not |
|-----|---|-------|------|-----|
| **DI-8** | 1 | 8 | **5–30 V izole** (12/24 V aynı kart) | D-28 · D-76 |
| **DO-M-8A-8** | 1 | 8 | High-side MOSFET **8 A/ch** | Standart DC çıkış. 8 A latching yok. PWM (dimmer / RGBW) firmware |
| **AI-8** | 1 | 8 | Analog giriş | Port başı config · D-73 |
| **AO-4** | 1 | 4 | 0–10 V çıkış | Ayrı kart, lokal boost. 8ch sürücü 1U'da kalabalık |
| **DC-L-16A-4** | 1* | 4 | Latching 16 A DC | Aux kontak (D-53). *Yükseklik → 2U (D-61) |
| **DC-H-32A-2** | 2 | 2 | Hibrit 32 A DC | Metal ön panel ısı (D-54) |
| **DC-H-64A-2** | 2 | 2 | Hibrit 64 A DC | D-54. 48 V ark |
| **AC-L-16A-4** | 2 | 4 | Latching 16 A AC | Aux (D-53). D-64. ZC sinüste (D-55) |
| **AC-L-32A-2** | 2 | 2 | Latching 32 A AC | Aux (D-53). D-64 |
| **COM-1U** | 1* | — | CAN izolesiz + Ethernet magjack | D-74. 2 katman (D-36). Sığmazsa 2U **veya** CAN/ETH ayrı 1U |

Yok: 1 A DO SKU, 8 A latching, ayrı PWM node, 4U gövde, AI+AO kombi.

### 5.1 DO-M-8A-8 — standart çıkış

1 A vs 8 A akıllı high-side fiyat farkı kanal başına küçüktür; tek SKU stok
ve yazılımı böler. Saatlerce açık yük de MOSFET — charge pump kabul edildi.

Yük akımı **saha bataryasından** geçer, backplane +5 V'tan değil.

| Limit | Değer | Neden |
|-------|--------|--------|
| Kanal | 8 A | PROFET sınıfı |
| Node eşzamanlı | **≤ 32 A** (sarı, şemada doğrulanır) | 8×8 A = 64 A iz/klemens/pasif ısıl 1U'da durmaz |
| PWM | Evet | Lamba kısma, RGBW 4 kanalı kullanır |

### 5.2 Analog · D-73

**AI-8 ve AO-4 ayrı 1U.** AI sessiz referans; AO 5 V→12 V boost.

AI-8 her kanal, firmware/config ile **bir** mod:

| Mod | Kullanım |
|-----|----------|
| NTC | Kabin, su, buzdolabı |
| 4–20 mA | Endüstriyel verici |
| 0–20 mA | Aynı donanım, 4 mA offsüz |
| 0–10 V | Gerilim verici / tank (bölenli) |

Paylaşılan analog GND; iki sıra klemens. Pals/akış AI'da veya DI'da — ayrı
SKU yok.

AO-4: 0–10 V, kanal başı. Daha fazla AO = ikinci node.

### 5.3 Güç ve AC — 1U / 2U

| SKU | Neden bu kanal |
|-----|----------------|
| DC-L-16A-4 | 3.5–5 mm klemens, 4ch 1U hedef |
| DC-H-32A-2 | 8.5 mm, 2U'da 2ch |
| DC-H-64A-2 | 10–12 mm; 2ch 2U sıkı ama 4U yok |
| AC-L-16A-4 | 7.5 mm, 2U'da 4 L+N sınıfı — 8ch 4U olurdu |
| AC-L-32A-2 | 10 mm, 2ch |

DC 32/64 A **hibrit** (latching + MOSFET ark kesici) · [11 §3](11-cikis-node-topolojileri.md#3-hibrit-anahtar--ikisini-birden-almak).

### 5.4 Haberleşme · D-74

**COM-1U:** CAN (ESS / Victron / BMS) **izolesiz** + Ethernet (W5500, magjack
izolasyonu). Takılı değilse enerji sıfır. Host Ethernet'te kalmaz (D-47).
CAN ortak şasi varsayar; saha RS-485 kadar düşman değil — 1U yer ETH'ye kalır.

### 5.5 Tip ID

```
0x0101  DI-8
0x0201  DO-M-8A-8
0x0301  AI-8          (mod bayrakları descriptor'da)
0x0401  AO-4
0x0501  DC-L-16A-4
0x0502  DC-H-32A-2
0x0503  DC-H-64A-2
0x0581  AC-L-16A-4
0x0582  AC-L-32A-2
0x0601  COM-1U
0xFFxx  test
```

---

## 6. 1U → 2U kuralı · D-75

| Kalem | 1U | 2U |
|-------|----|----|
| Ortak çekirdek | Aynı | Aynı |
| Backplane konnektörü | 1 | 1 elektrik (sol) + bakırsız yalancı dil (sağ) · D-16 |
| +5V tavan | 250 mA sürekli (D-29) | 500 mA |
| Ön yüz | 17.5 mm | 35 mm |
| PCB | 2 katman (D-36) | 2 katman |
| Descriptor `form_factor` | 1U | 2U |

**3U / 4U yok.** 1U'ya sığmayan **2U olur** (D-61) veya modül bölünür — 4 katman
yok (D-36). 4U gerekecek kadar şişerse kanal kesilir veya ikinci 2U (D-75).
