# 04 — Backplane ve Mekanik

> Bu dokümandaki kararlar **geriye dönük değiştirilemez**. Üretilmiş her node
> buraya bağlıdır.

## 1. Mekanik standart

### Karar: 1U = 22.5 mm · 2U = 45 mm

Bu değer keyfi seçilmedi. **22.5 mm, endüstriyel DIN ray node genişliğinin
fiili standardıdır** — Phoenix Contact ME serisi, Wago, Beckhoff, Italtronic,
Camdenboss hepsi bu adımı kullanıyor.

**Sonuç: özel kalıp yaptırmıyoruz.** Hazır, satın alınabilir, birden fazla
tedarikçisi olan kutu ekosistemine oturuyoruz. Bir platform ürünü için bu,
estetik değil tedarik kararıdır.

```
1U slot adımı        22.5 mm
2U slot adımı        45.0 mm
8U toplam genişlik   8 × 22.5 = 180 mm   (+ host elektroniği bölümü)
```

### 1.2 Node yönelimi

Node'lar yan yana dizilen **dikey kartlardır** — PCB düzlemi komşusuna paralel.

```
            ön yüz (saha klemensleri)
                     ↓
      ┌──────────────────────┐
      │                      │  ← 22.5 mm genişlik (kutu dahil)
      │      Node PCB       │
      │   100 mm × 90 mm     │  ← PCB düzlemi sayfa düzlemine dik
      │                      │
      └──────────┬───────────┘
                 ↓
         arka kenar: kart kenarı konnektörü
```

| Boyut | Değer |
|-------|-------|
| Node PCB yüksekliği | ~100 mm (standart DIN kutu iç yüksekliği) |
| Node PCB derinliği | ~90 mm |
| PCB kalınlığı | 1.6 mm |
| Konnektör kenarı | Arka kenar, 100 mm boyunca — 26 pin için fazlasıyla yer var |

Ön yüzde 22.5 mm genişlik, iki sıra klemens için yeterli.

---

## 2. Konnektör seçimi

| Seçenek | Node tarafı maliyet | Servis ömrü | Stagger | Değerlendirme |
|---------|---------------------|-------------|---------|---------------|
| **PCB kart kenarı (gold finger)** | **$0 — sadece PCB** | ENIG ~50 takma · sert altın 500+ | **Bedava** (finger boyu ile) | **Seçilen** |
| Pin header 2×N | ~$0.15 | Düşük — tekrarlı takmaya uygun değil | Yok | Servis gereksinimini karşılamıyor |
| DIN 41612 | ~$2–4 | Çok yüksek | Var | Sağlam ama pahalı ve hacimli |

### Karar: PCB kart kenarı, 2.54 mm adım, çift sıra, 26 pin

Blade server ve PCIe'nin yaptığının aynısı. İki kritik kazanç:

1. **Node tarafı bedava** — konnektör diye bir parça yok, sadece PCB üzerinde
   gold finger. K1 (node ucuz olmalı) doğrudan karşılanıyor.
2. **Staggered kontak bedava** — finger boylarını farklı çizmek maliyet
   getirmiyor. Bu, §5'teki hot-plug kararını neredeyse bedava kılıyor.

**Üretim notu:** JLCPCB gold finger opsiyonu ek kurulum ücreti gerektiriyor.
Prototipte ENIG yeterli (~50 takma çevrimi); seri üretimde sert altına geçilir.
Bu bir BOM kararı değil, PCB süreç kararı — prototip ile seri arasında
değişebilir, tasarımı etkilemez.

---

## 3. Pinout

### Karar: 26 pin, 4 kademeli mate sırası

| # | Sinyal | Yön | Mate | Açıklama |
|---|--------|-----|------|----------|
| 1–4 | **GND** | — | **1** | Referans her şeyden önce oturmalı |
| 5–6 | **VBUS_RAW** | → node | 2 | 12–48V ham, slot başına 500 mA |
| 7–8 | **+5V_SYS** | → node | 2 | Slot başına 200 mA (1U) / 400 mA (2U) |
| 9–12 | **ADDR0–3** | backplane sabit | 2 | Coğrafi slot kimliği, GND'ye bağlı veya açık |
| 13 | **BUS_A** | çift yön | 3 | RS-485 non-inverting |
| 14 | **BUS_B** | çift yön | 3 | RS-485 inverting |
| 15–16 | *RSVD_BUS_Y / Z* | — | 3 | **Tam dupleks yükseltmesi için rezerve** |
| 17 | **MOD_RST#** | host → node | 3 | Slot başına. Node'da 10k pull-**down** |
| 18 | **BOOT#** | host → tüm slotlar | 3 | Ortak. Reset bırakılırken örneklenir |
| 19 | **FAULT#** | node → host | 3 | Ortak, open-drain wired-OR |
| 20 | **SYNC** | host → tüm slotlar | 3 | Eşzamanlı I/O latch strobe |
| 21–24 | *RSVD* | — | 3 | Gelecek genişleme |
| 25 | **PRESENT#** | node → host | **4 (en kısa)** | GND'ye bağlı. **Son oturan pin** |
| 26 | **GND** | — | 1 | Ek dönüş |

### 3.1 Mate sırasının mantığı

```
Kademe 1 (en uzun)   GND              → referans kurulur
Kademe 2             Güç + ADDR       → besleme gelir, slot kimliği geçerli olur
Kademe 3             Sinyaller        → bus ve kontrol hatları bağlanır
Kademe 4 (en kısa)   PRESENT#         → "tam oturdu" sinyali
```

**PRESENT#'in en son oturması tasarımın kilit taşı.** Host, PRESENT# düşene
kadar node'u yok sayar. Yarım oturmuş bir node — güç ve sinyal kısmen bağlı —
sistemi hiç etkilemez, çünkü host onu görmez ve reset'ini bırakmaz.

### 3.2 Rezerve pinlerin gerekçesi

| Pin | Rezerve sebebi |
|-----|----------------|
| 15–16 | Yarım → tam dupleks yükseltmesi ([05 §2](05-dahili-bus.md#2-yarım-dupleks-mi-tam-dupleks-mi)). Pinout geri dönülemez olduğu için şimdi ayrılmalı. |
| 21–24 | Bilinmeyen gelecek ihtiyaçları. 4 pinin maliyeti sıfıra yakın; sonradan eklemenin maliyeti tüm node ailesi. |

**BUS_A/B çifti CAN'e de uygun.** İleride event-driven multi-host ihtiyacı
doğarsa sadece transceiver değişir, pinout ve mekanik aynı kalır.

---

## 4. 2U node stratejisi

| Seçenek | Değerlendirme |
|---------|---------------|
| **(a) Sadece sol slotun konnektörüne oturur** | Tek konnektör hizalaması — mekanik olarak belirgin şekilde basit. Discovery'de "2U" bildirir, host N+1'i kapalı işaretler. |
| (b) Her iki konnektöre de oturur | 2× pin ve güç, ama iki konnektörün toleranslı hizalanması gerekir |

### Karar: (a)

Güç yeterliliği kontrol edildi: 2U node'un 400 mA'i 2 adet +5V_SYS kontağından
geçiyor, 2.54 mm kart kenarı kontak kapasitesinin çok altında.

(b) sadece gelecekte yüksek güçlü bir 2U node gerekirse açılacak — pinout'ta
bunu engelleyen bir şey yok.

### 4.1 Adresleme tutarlılığı

```
Slot 3–4'e takılı bir 2U node:
  · ADDR pinlerinden slot 3'ü okur
  · Descriptor'da form_factor = 2U bildirir
  · Host slot 4'ü "2U tarafından kapatıldı" olarak işaretler
  · Slot 4'ün PRESENT# hattı yüksek kalır (konnektörü boş) — tutarlı
```

---

## 5. Hot-plug değerlendirmesi

Brief'in talebi üzerine karar öncesi maliyet analizi.

| Gereksinim | Maliyet | Not |
|------------|---------|-----|
| Staggered kontak (GND→güç→sinyal→presence) | **$0** | Kart kenarı finger boyları ile (§2) |
| Slot başına akım sınırlı load switch | ~$0.20 | **Zaten arıza izolasyonu için öneriliyor** ([06 §7](06-slot-yonetimi.md#7-slot-başına-akım-koruması)) |
| Node tarafı soft-start | ~$0.15 | |
| Hot-plug toleranslı RS-485 transceiver | **$0** | Aynı fiyat sınıfında mevcut |
| Protokol desteği | **$0** | Host-node zaten timeout tabanlı; kaybolan node = timeout, yeni node = PCA9555 INT# |
| **Toplam ek maliyet** | **~$0.35 / node** | |

### Karar: donanımı hot-plug yetenekli tasarla, v1'de garanti verme

**Gerekçe — asimetrik risk:**

| | Şimdi yaparsak | Sonra yapmak istersek |
|---|---|---|
| Maliyet | ~$0.35/node | **Tüm node ailesi + backplane yeniden tasarım** |
| Sebep | — | Konnektör pin sıralaması ve pinout geri dönülemez |

Yeteneği inşa etmenin maliyeti marjinal, inşa etmemenin geri dönüş maliyeti
felaket. Bu yüzden donanım hazır olacak; **doğrulama ve garanti v1.1'e
bırakılıyor** — çünkü hot-swap iddiası test gerektirir, donanım değil.

### 5.1 v1'de yapılacaklar

- [x] Staggered finger tasarımı
- [x] Slot load switch (soft-start dahil)
- [x] Node soft-start
- [x] Hot-plug toleranslı transceiver seçimi
- [x] PRESENT# tabanlı protokol toleransı

### 5.2 v1.1'e bırakılanlar

- [ ] Canlı takma/çıkarma testi (en az 50 çevrim)
- [ ] Takma anında komşu slotların rail dip ölçümü
- [ ] Bus bütünlüğü testi (takma sırasında devam eden trafik)
- [ ] Dokümantasyonda hot-swap iddiası
